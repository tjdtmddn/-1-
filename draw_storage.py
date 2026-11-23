import sqlite3
import sys
from collections.abc import Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from missions import Mission


APP_DIRECTORY = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve().parent
DEFAULT_DB_PATH = APP_DIRECTORY / "daily_missions.sqlite3"


@dataclass(frozen=True)
class DailyDraw:
    date: date
    mission: Mission


@contextmanager
def open_database(db_path: Path) -> Iterator[sqlite3.Connection]:
    with closing(sqlite3.connect(db_path)) as connection, connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS daily_draws (
                draw_date TEXT PRIMARY KEY NOT NULL,
                mission_id TEXT NOT NULL,
                content TEXT NOT NULL,
                difficulty TEXT NOT NULL
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS mission_completions (
                draw_date TEXT PRIMARY KEY NOT NULL REFERENCES daily_draws(draw_date)
            )
        """)
        yield connection


def _read_draw(connection: sqlite3.Connection, day: date) -> DailyDraw | None:
    row = connection.execute(
        "SELECT mission_id, content, difficulty FROM daily_draws WHERE draw_date = ?",
        (day.isoformat(),),
    ).fetchone()
    if row is None:
        return None
    return DailyDraw(day, Mission(*row))


def load_draw(day: date, db_path: Path = DEFAULT_DB_PATH) -> DailyDraw | None:
    with open_database(db_path) as connection:
        return _read_draw(connection, day)


def save_draw(draw: DailyDraw, db_path: Path = DEFAULT_DB_PATH) -> DailyDraw:
    """Save the first draw for the date and return the record that was stored."""
    with open_database(db_path) as connection:
        connection.execute(
            """
            INSERT INTO daily_draws (draw_date, mission_id, content, difficulty)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(draw_date) DO NOTHING
            """,
            (
                draw.date.isoformat(),
                draw.mission.id,
                draw.mission.content,
                draw.mission.difficulty,
            ),
        )
        saved_draw = _read_draw(connection, draw.date)
        if saved_draw is None:
            raise sqlite3.DatabaseError("저장된 추첨 결과를 찾을 수 없습니다.")
        return saved_draw


@dataclass(frozen=True)
class MissionRecord:
    draw: DailyDraw
    completed: bool


def list_records(db_path: Path = DEFAULT_DB_PATH) -> list[MissionRecord]:
    with open_database(db_path) as connection:
        rows = connection.execute("""
            SELECT d.draw_date, d.mission_id, d.content, d.difficulty,
                   c.draw_date IS NOT NULL
            FROM daily_draws AS d
            LEFT JOIN mission_completions AS c ON c.draw_date = d.draw_date
            ORDER BY d.draw_date DESC
        """).fetchall()
    return [
        MissionRecord(DailyDraw(date.fromisoformat(day), Mission(mission_id, content, difficulty)), bool(completed))
        for day, mission_id, content, difficulty, completed in rows
    ]


def mark_completed(draw: DailyDraw, db_path: Path = DEFAULT_DB_PATH) -> None:
    """Record completion for a saved draw. Repeated completion is harmless."""
    with open_database(db_path) as connection:
        connection.execute(
            """
            INSERT INTO mission_completions (draw_date)
            SELECT draw_date FROM daily_draws WHERE draw_date = ? AND mission_id = ?
            ON CONFLICT(draw_date) DO NOTHING
            """,
            (draw.date.isoformat(), draw.mission.id),
        )
