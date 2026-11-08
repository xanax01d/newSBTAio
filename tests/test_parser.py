from sbt_bot.db import Base, ScheduleRepository, UserRepository, create_engine_and_sessionmaker
from sbt_bot.db.repositories import ParsedLessonDTO
from sbt_bot.parser.bsac_pdf import _parse_table, normalize_group_name


def test_normalize_group_name() -> None:
    assert normalize_group_name("СИ - 391") == "СИ-391"
    assert normalize_group_name("  тк-311 ") == "ТК-311"
    assert normalize_group_name("Группа без кода") is None


def test_parse_table_extracts_lessons() -> None:
    table = [
        ["День", "Пара", "СИ - 391", "АП - 391"],
        ["Понедельник", "1 (8:00-9:40)", "Математика (л)", "!"],
        ["", "2 (9:55-11:35)", "-", "Физика (пз)"],
        ["Вторник", "1 (8:00-9:40)", "История", "История"],
    ]
    lessons = _parse_table(table, stage="ВО", course=1, week_number=2)
    assert len(lessons) == 4
    assert lessons[0].group_name == "СИ-391"
    assert lessons[0].day_of_week == 0
    assert lessons[0].lesson_number == 1
    assert lessons[0].subject == "Математика (л)"
    assert lessons[1].group_name == "АП-391"
    assert lessons[1].lesson_number == 2


async def test_repositories_roundtrip() -> None:
    engine, session_factory = create_engine_and_sessionmaker("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        user_repo = UserRepository(session)
        user = await user_repo.upsert(
            user_id=101, username="tester", first_name="Test", chat_id=101
        )
        assert user.id == 101
        await user_repo.set_group(101, "СИ-391")
        assert (await user_repo.get(101)).selected_group == "СИ-391"

        sched_repo = ScheduleRepository(session)
        groups_cnt, entries_cnt = await sched_repo.replace_schedule_entries(
            [
                ParsedLessonDTO(
                    group_name="СИ-391",
                    stage="ВО",
                    course=1,
                    week_number=1,
                    day_of_week=0,
                    lesson_number=1,
                    subgroup=0,
                    time_range="8:00 - 9:40",
                    subject="Математика",
                )
            ]
        )
        assert groups_cnt == 1
        assert entries_cnt == 1
        assert await sched_repo.list_stages() == ["ВО"]
        assert await sched_repo.list_courses("ВО") == [1]
        assert await sched_repo.list_groups("ВО", 1) == ["СИ-391"]
        day_entries = await sched_repo.get_day_schedule(
            group_name="СИ-391", week_number=1, day_of_week=0
        )
        assert len(day_entries) == 1
        assert day_entries[0].subject == "Математика"

    await engine.dispose()
