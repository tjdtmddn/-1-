"""Date-based JSON history adapted from GeonJun-Park's MissionStore."""

import json
from datetime import date
from pathlib import Path


class HistoryFormatError(ValueError):
    pass


class MissionStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        try:
            with self.path.open("r", encoding="utf-8") as file:
                self.records = json.load(file)
        except FileNotFoundError:
            self.records = {}
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise HistoryFormatError("기록 파일을 읽을 수 없습니다.") from error
        self._validate_records()

    def _validate_records(self):
        if not isinstance(self.records, dict):
            raise HistoryFormatError("기록 파일의 형식이 올바르지 않습니다.")
        for day, record in self.records.items():
            try:
                valid_day = date.fromisoformat(day).isoformat() == day
            except (TypeError, ValueError):
                valid_day = False
            if (
                not valid_day
                or not isinstance(record, dict)
                or not isinstance(record.get("mission"), str)
                or not isinstance(record.get("completed"), bool)
                or any(key in record and not isinstance(record[key], str)
                       for key in ("mission_id", "difficulty"))
            ):
                raise HistoryFormatError("기록 파일에 올바르지 않은 미션 데이터가 있습니다.")

    def get_daily_mission(self, day: date, new_record: dict) -> dict:
        day_key = day.isoformat()
        if day_key not in self.records:
            self.records[day_key] = new_record
            try:
                self._save()
            except OSError:
                del self.records[day_key]
                raise
        return self.records[day_key]

    def complete(self, day: date):
        record = self.records.get(day.isoformat())
        if record is None or record["completed"]:
            return

        record["completed"] = True
        try:
            self._save()
        except OSError:
            record["completed"] = False
            raise

    def merge_legacy(self, records):
        merged = dict(self.records)
        for day, old in records.items():
            current = merged.get(day)
            if current is None:
                merged[day] = old
            elif current["mission"] == old["mission"]:
                merged[day] = {**old, **current, "completed": old["completed"] or current["completed"]}

        if merged != self.records:
            original = self.records
            self.records = merged
            try:
                self._save()
            except OSError:
                self.records = original
                raise

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(self.path.suffix + ".tmp")
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(self.records, file, ensure_ascii=False, indent=2)
        temporary_path.replace(self.path)
