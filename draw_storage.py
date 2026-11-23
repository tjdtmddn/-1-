import sqlite3
import sys
from collections.abc import Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from mission_history import MissionStore
from missions import MISSIONS, Mission


APP_DIRECTORY = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve().parent
DEFAULT_DB_PATH = APP_DIRECTORY / "daily_missions.sqlite3"
DEFAULT_HISTORY_NAME = "mission_data.json"


@dataclass(frozen=True)
class DailyDraw:
    date: date
    mission: Mission


@dataclass(frozen=True)
class MissionRecord:
    draw: DailyDraw
    completed: bool


@contextmanager
def open_database(db_path: Path) -> Iterator[sqlite3.Connection]:
    with closing(sqlite3.connect(db_path)) as connection, connection:
        yield connection


def _legacy_records(connection: sqlite3.Connection) -> dict:
    tables = {name for name, in connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name IN ('daily_draws', 'mission_completions')"
    )}
    if "daily_draws" not in tables:
        return {}

    selection = "SELECT d.draw_date, d.mission_id, d.content, d.difficulty"
    if "mission_completions" in tables:
        rows = connection.execute(
            selection + ", c.draw_date IS NOT NULL FROM daily_draws AS d "
            "LEFT JOIN mission_completions AS c ON c.draw_date = d.draw_date"
        )
    else:
        rows = connection.execute(selection + ", 0 FROM daily_draws AS d")
    return {
        day: {"mission_id": mission_id, "mission": content, "difficulty": difficulty, "completed": bool(completed)}
        for day, mission_id, content, difficulty, completed in rows
    }


@contextmanager
def _open_history(db_path: Path) -> Iterator[MissionStore]:
    db_path = Path(db_path)
    history_path = (db_path.with_name(DEFAULT_HISTORY_NAME) if db_path.name == DEFAULT_DB_PATH.name
                    else db_path.with_suffix(".json"))
    with open_database(db_path) as connection:
        # Serialize JSON read/modify/write across the desktop and CLI processes.
        connection.execute("BEGIN IMMEDIATE")
        store = MissionStore(history_path)
        connection.execute("CREATE TABLE IF NOT EXISTS history_migration (source TEXT PRIMARY KEY)")
        migrated = connection.execute("SELECT 1 FROM history_migration WHERE source = 'sqlite'").fetchone()
        if not migrated:
            store.merge_legacy(_legacy_records(connection))
            connection.execute("INSERT INTO history_migration (source) VALUES ('sqlite')")
        yield store


_BASIC_BY_CONTENT = {mission.content: mission for mission in MISSIONS}


def _draw_from_record(day: date, record: dict) -> DailyDraw:
    basic = _BASIC_BY_CONTENT.get(record["mission"])
    mission_id = record.get("mission_id") or (basic.id if basic else f"history-{day.isoformat()}")
    difficulty = record.get("difficulty") or (basic.difficulty if basic else "")
    return DailyDraw(day, Mission(mission_id, record["mission"], difficulty))


def load_draw(day: date, db_path: Path = DEFAULT_DB_PATH) -> DailyDraw | None:
    with _open_history(db_path) as store:
        record = store.records.get(day.isoformat())
        return _draw_from_record(day, record) if record is not None else None


def save_draw(draw: DailyDraw, db_path: Path = DEFAULT_DB_PATH) -> DailyDraw:
    with _open_history(db_path) as store:
        record = store.get_daily_mission(draw.date, {
            "mission": draw.mission.content,
            "completed": False,
            "mission_id": draw.mission.id,
            "difficulty": draw.mission.difficulty,
        })
        return _draw_from_record(draw.date, record)


def list_records(db_path: Path = DEFAULT_DB_PATH) -> list[MissionRecord]:
    with _open_history(db_path) as store:
        return [
            MissionRecord(_draw_from_record(date.fromisoformat(day), record), record["completed"])
            for day, record in sorted(store.records.items(), reverse=True)
        ]


def mark_completed(draw: DailyDraw, db_path: Path = DEFAULT_DB_PATH) -> None:
    with _open_history(db_path) as store:
        record = store.records.get(draw.date.isoformat())
        if record is not None and _draw_from_record(draw.date, record).mission.id == draw.mission.id:
            store.complete(draw.date)
