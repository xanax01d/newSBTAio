import io
import logging
import re
from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
import pdfplumber
from bs4 import BeautifulSoup

from sbt_bot.db.repositories import ParsedLessonDTO
from sbt_bot.utils.week import DAYS_OF_WEEK, LESSON_TIMES

logger = logging.getLogger(__name__)

_GROUP_RE = re.compile(r"\b([А-ЯЁA-Z]{2,4})\s*[-–]\s*(\d{3})\b", re.IGNORECASE)
_COURSE_FROM_URL_RE = re.compile(r"(?:curs|kurs|курс)[_\-\s]*(\d)", re.IGNORECASE)
_WEEK_RE = re.compile(r"(\d)\s*недел", re.IGNORECASE)
_TIME_RE = re.compile(r"(\d{1,2}[:.]\d{2})\s*[-–]\s*(\d{1,2}[:.]\d{2})")

_DAY_LOOKUP: dict[str, int] = {day.lower(): idx for idx, day in enumerate(DAYS_OF_WEEK)}


@dataclass(frozen=True, slots=True)
class PdfLink:
    url: str
    stage: str
    course_hint: int | None


def normalize_group_name(raw: str) -> str | None:
    """Normalize group name like 'СИ - 391' or 'СИ-391' to 'СИ-391'."""
    match = _GROUP_RE.search(raw)
    if not match:
        return None
    return f"{match.group(1).upper()}-{match.group(2)}"


def _detect_day_index(text: str) -> int | None:
    lowered = text.lower()
    for name, idx in _DAY_LOOKUP.items():
        if name in lowered:
            return idx
    return None


def _detect_lesson_number(text: str) -> tuple[int | None, str]:
    cleaned = text.strip()
    time_match = _TIME_RE.search(cleaned)
    time_str = f"{time_match.group(1)} - {time_match.group(2)}" if time_match else ""

    for num, std_time in LESSON_TIMES.items():
        start_hour = std_time.split("-")[0].strip().split(":")[0]
        if time_match and time_match.group(1).replace(".", ":").startswith(f"{start_hour}:"):
            return num, time_str or std_time

    digit_match = re.match(r"^\s*([1-6])\b", cleaned)
    if digit_match:
        num = int(digit_match.group(1))
        return num, time_str or LESSON_TIMES.get(num, "")

    return None, time_str


def _extract_course_from_text(text: str) -> int | None:
    match = re.search(r"(\d)\s*курс", text, re.IGNORECASE)
    if match:
        val = int(match.group(1))
        if 1 <= val <= 4:
            return val
    return None


def parse_pdf_bytes(
    data: bytes,
    *,
    stage: str,
    default_course: int | None = None,
) -> list[ParsedLessonDTO]:
    """Parse BSAC schedule PDF bytes into normalized ParsedLessonDTO records."""
    lessons: list[ParsedLessonDTO] = []

    with pdfplumber.open(io.BytesIO(data)) as pdf:
        current_course = default_course
        current_week = 1

        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if current_course is None:
                current_course = _extract_course_from_text(page_text)
            week_match = _WEEK_RE.search(page_text)
            if week_match:
                week_num = int(week_match.group(1))
                if 1 <= week_num <= 4:
                    current_week = week_num

            tables = page.extract_tables() or []
            for table in tables:
                lessons.extend(
                    _parse_table(
                        table,
                        stage=stage,
                        course=current_course or 1,
                        week_number=current_week,
                    )
                )

    return lessons


def _parse_table(
    table: list[list[str | None]],
    *,
    stage: str,
    course: int,
    week_number: int,
) -> list[ParsedLessonDTO]:
    if not table:
        return []

    group_columns: dict[int, str] = {}
    header_row_idx = -1

    for idx, row in enumerate(table[:5]):
        found: dict[int, str] = {}
        for col_idx, cell in enumerate(row):
            if not cell:
                continue
            group_name = normalize_group_name(cell)
            if group_name:
                found[col_idx] = group_name
        if found:
            group_columns = found
            header_row_idx = idx
            break

    if not group_columns:
        return []

    results: list[ParsedLessonDTO] = []
    current_day: int | None = None
    lesson_counter = 0

    for row in table[header_row_idx + 1 :]:
        if not row:
            continue

        row_cells = [(c or "").strip() for c in row]
        row_joined = " ".join(c for c in row_cells if c)
        if not row_joined:
            continue

        detected_day = _detect_day_index(row_joined)
        if detected_day is not None and detected_day != current_day:
            current_day = detected_day
            lesson_counter = 0

        if current_day is None:
            continue

        # Try detecting lesson number & time from non-group leading columns
        first_group_col = min(group_columns.keys())
        meta_text = " ".join(row_cells[:first_group_col])
        lesson_num, time_str = _detect_lesson_number(meta_text)
        if lesson_num is None:
            lesson_counter += 1
            if lesson_counter > 6:
                continue
            lesson_num = lesson_counter
            time_str = LESSON_TIMES.get(lesson_num, "")
        else:
            lesson_counter = lesson_num

        for col_idx, group_name in group_columns.items():
            if col_idx >= len(row_cells):
                continue
            cell_text = " ".join(row_cells[col_idx].split())
            if not cell_text or cell_text in {"-", "—", "!"}:
                continue

            results.append(
                ParsedLessonDTO(
                    group_name=group_name,
                    stage=stage,
                    course=course,
                    week_number=week_number,
                    day_of_week=current_day,
                    lesson_number=lesson_num,
                    subgroup=0,
                    time_range=time_str or LESSON_TIMES.get(lesson_num, ""),
                    subject=cell_text,
                )
            )

    return results


class BsacPdfScheduleSource:
    """Fetches and parses schedule PDFs from bsac.by."""

    name = "bsac_pdf"

    def __init__(self, *, stage_urls: dict[str, str], timeout: float = 20.0) -> None:
        self.stage_urls = stage_urls
        self.timeout = timeout

    async def fetch_lessons(self) -> list[ParsedLessonDTO]:
        all_lessons: list[ParsedLessonDTO] = []
        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; BSACScheduleBot/2.0)"},
        ) as client:
            for stage, page_url in self.stage_urls.items():
                try:
                    links = await self._discover_pdf_links(client, page_url, stage)
                except Exception:
                    logger.exception("Failed to discover PDF links for %s (%s)", stage, page_url)
                    continue

                for link in links:
                    try:
                        resp = await client.get(link.url)
                        resp.raise_for_status()
                        parsed = parse_pdf_bytes(
                            resp.content,
                            stage=link.stage,
                            default_course=link.course_hint,
                        )
                        logger.info(
                            "Parsed %d lessons from %s (stage=%s, course=%s)",
                            len(parsed),
                            link.url,
                            link.stage,
                            link.course_hint,
                        )
                        all_lessons.extend(parsed)
                    except Exception:
                        logger.exception("Failed to parse PDF %s", link.url)

        return all_lessons

    async def _discover_pdf_links(
        self,
        client: httpx.AsyncClient,
        page_url: str,
        stage: str,
    ) -> list[PdfLink]:
        resp = await client.get(page_url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        links: list[PdfLink] = []
        seen: set[str] = set()

        for anchor in soup.find_all("a", href=True):
            href = str(anchor["href"]).strip()
            if not href.lower().endswith(".pdf"):
                continue
            if "curs" not in href.lower() and "kurs" not in href.lower():
                continue
            full_url = urljoin(page_url, href)
            if full_url in seen:
                continue
            seen.add(full_url)

            course_match = _COURSE_FROM_URL_RE.search(href)
            course_hint = int(course_match.group(1)) if course_match else None
            links.append(PdfLink(url=full_url, stage=stage, course_hint=course_hint))

        return links
