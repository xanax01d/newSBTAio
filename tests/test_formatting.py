from sbt_bot.db.models import ScheduleEntry
from sbt_bot.utils.formatting import format_day_schedule, format_week_schedule


def test_format_day_schedule_empty() -> None:
    text = format_day_schedule([], day_of_week=0, week_number=2, group_name="СИ-391")
    assert "Понедельник" in text
    assert "2 неделя" in text
    assert "СИ-391" in text
    assert "Пар нет." in text


def test_format_day_schedule_with_subgroups_and_html_escape() -> None:
    entries = [
        ScheduleEntry(
            group_id=1,
            week_number=1,
            day_of_week=2,
            lesson_number=1,
            subgroup=1,
            time_range="8:00 - 9:40",
            subject="ОАиП <Лаб>",
            auditorium="301",
        ),
        ScheduleEntry(
            group_id=1,
            week_number=1,
            day_of_week=2,
            lesson_number=1,
            subgroup=2,
            time_range="8:00 - 9:40",
            subject="Физика",
            auditorium="205",
        ),
    ]
    text = format_day_schedule(entries, day_of_week=2, week_number=1, group_name="СИ-391")
    assert "1 пара (8:00 - 9:40)" in text
    assert "1 п/г: ОАиП &lt;Лаб&gt; <i>(ауд. 301)</i>" in text
    assert "2 п/г: Физика <i>(ауд. 205)</i>" in text


def test_format_week_schedule_lists_all_days() -> None:
    entries = [
        ScheduleEntry(
            group_id=1,
            week_number=3,
            day_of_week=0,
            lesson_number=2,
            subgroup=0,
            time_range="9:55 - 11:35",
            subject="Математика",
        )
    ]
    text = format_week_schedule(entries, week_number=3, group_name="ТК-311")
    assert "📅 Понедельник" in text
    assert "Математика" in text
    assert "📅 Суббота" in text
