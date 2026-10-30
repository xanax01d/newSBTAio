from datetime import datetime

from sbt_bot.utils.week import get_current_week, resolve_day_and_week


def test_first_week_starting_august_1() -> None:
    # 2025-08-01 is Friday
    assert get_current_week(datetime(2025, 8, 1, 10, 0)) == 1
    assert get_current_week(datetime(2025, 8, 3, 23, 0)) == 1


def test_four_week_cycle_wraps() -> None:
    # 2025-08-04 is Monday of week 2
    assert get_current_week(datetime(2025, 8, 4, 9, 0)) == 2
    assert get_current_week(datetime(2025, 8, 11, 9, 0)) == 3
    assert get_current_week(datetime(2025, 8, 18, 9, 0)) == 4
    assert get_current_week(datetime(2025, 8, 25, 9, 0)) == 1


def test_resolve_day_shifts_sunday_to_monday() -> None:
    # 2025-08-10 is Sunday (end of week 2), Monday 2025-08-11 is week 3
    day_idx, week_num, shifted = resolve_day_and_week(
        offset_days=0,
        dt=datetime(2025, 8, 10, 12, 0),
    )
    assert shifted is True
    assert day_idx == 0
    assert week_num == 3
