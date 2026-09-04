import secrets
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CaptchaItem:
    """Single captcha option."""

    label: str
    emoji: str
    code: str


CAPTCHA_ITEMS: tuple[CaptchaItem, ...] = (
    CaptchaItem(label="Яблоко", emoji="🍎", code="cap1"),
    CaptchaItem(label="Банан", emoji="🍌", code="cap2"),
    CaptchaItem(label="Арбуз", emoji="🍉", code="cap3"),
    CaptchaItem(label="Морковь", emoji="🥕", code="cap4"),
    CaptchaItem(label="Виноград", emoji="🍇", code="cap5"),
    CaptchaItem(label="Кукурузу", emoji="🌽", code="cap6"),
)


@dataclass(frozen=True, slots=True)
class CaptchaChallenge:
    """Generated captcha challenge."""

    prompt_label: str
    emoji: str
    expected_code: str


def generate_captcha() -> CaptchaChallenge:
    """Pick a random fruit captcha challenge using CSPRNG."""
    item = secrets.choice(CAPTCHA_ITEMS)
    return CaptchaChallenge(
        prompt_label=item.label,
        emoji=item.emoji,
        expected_code=item.code,
    )
