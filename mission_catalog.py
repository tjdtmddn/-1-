from contextlib import contextmanager
from dataclasses import dataclass
from uuid import uuid4

from draw_storage import DEFAULT_DB_PATH, open_database
from missions import DIFFICULTIES, MISSIONS, Mission


@dataclass(frozen=True)
class CatalogEntry:
    mission: Mission
    active: bool


def _catalog_exists(connection):
    return connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'mission_catalog'"
    ).fetchone() is not None


@contextmanager
def _open_catalog(db_path):
    with open_database(db_path) as connection:
        if not _catalog_exists(connection):
            # Seed only when this database first gets a catalog, even after all rows are deleted.
            connection.execute("BEGIN IMMEDIATE")
            if not _catalog_exists(connection):
                connection.execute("""
                    CREATE TABLE mission_catalog (
                        position INTEGER PRIMARY KEY,
                        mission_id TEXT UNIQUE NOT NULL,
                        content TEXT NOT NULL,
                        difficulty TEXT NOT NULL,
                        active INTEGER NOT NULL CHECK (active IN (0, 1))
                    )
                """)
                connection.executemany(
                    "INSERT INTO mission_catalog (mission_id, content, difficulty, active) VALUES (?, ?, ?, 1)",
                    ((mission.id, mission.content, mission.difficulty) for mission in MISSIONS),
                )
        yield connection


def list_catalog(db_path=DEFAULT_DB_PATH):
    with _open_catalog(db_path) as connection:
        rows = connection.execute(
            "SELECT mission_id, content, difficulty, active FROM mission_catalog ORDER BY position"
        ).fetchall()
    return [CatalogEntry(Mission(mission_id, content, difficulty), bool(active))
            for mission_id, content, difficulty, active in rows]


def active_missions(db_path=DEFAULT_DB_PATH):
    return [entry.mission for entry in list_catalog(db_path) if entry.active]


def save_mission(content, difficulty, active=True, mission_id="", db_path=DEFAULT_DB_PATH):
    content = content.strip()
    if not 1 <= len(content) <= 120:
        raise ValueError("미션 내용은 1~120자로 입력해 주세요.")
    if difficulty not in DIFFICULTIES:
        raise ValueError("난이도를 선택해 주세요.")

    with _open_catalog(db_path) as connection:
        if mission_id:
            updated = connection.execute(
                "UPDATE mission_catalog SET content = ?, difficulty = ?, active = ? WHERE mission_id = ?",
                (content, difficulty, active, mission_id),
            )
            if updated.rowcount == 0:
                raise ValueError("이미 삭제된 미션입니다.")
        else:
            mission_id = f"user-{uuid4().hex}"
            connection.execute(
                "INSERT INTO mission_catalog (content, difficulty, active, mission_id) VALUES (?, ?, ?, ?)",
                (content, difficulty, active, mission_id),
            )
    return mission_id


def delete_mission(mission_id, db_path=DEFAULT_DB_PATH):
    with _open_catalog(db_path) as connection:
        connection.execute("DELETE FROM mission_catalog WHERE mission_id = ?", (mission_id,))
