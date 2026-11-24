import calendar
import sqlite3
import sys
from datetime import date
from pathlib import Path

from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from draw import draw_mission
from draw_storage import DailyDraw, list_records, load_draw, mark_completed, save_draw
from mission_catalog import active_missions, delete_mission, list_catalog, save_mission
from mission_history import HistoryFormatError
from missions import DIFFICULTIES
from admin_auth import get_admin_pin, MAX_PIN_ATTEMPTS


class MissionController(QObject):
    changed = Signal()
    calendar_changed = Signal()
    catalog_changed = Signal()
    admin_changed = Signal()

    def __init__(self):
        super().__init__()
        self._today = date.today()
        self._month = self._today.replace(day=1)
        self._daily = {}
        self._records = []
        self._catalog = []
        self._completed_days = set()
        self._error = ""
        self._admin_unlocked = False
        self._pin_attempts = 0
        self.refresh()

    @Property(bool, notify=admin_changed)
    def adminUnlocked(self):
        return self._admin_unlocked

    @Property(bool, notify=admin_changed)
    def pinLocked(self):
        return self._pin_attempts >= MAX_PIN_ATTEMPTS

    @Slot(str, result=bool)
    def verifyAdminPin(self, pin):
        if self._pin_attempts >= MAX_PIN_ATTEMPTS:
            return False
        if pin == get_admin_pin():
            self._admin_unlocked = True
            self._pin_attempts = 0
            self.admin_changed.emit()
            return True
        self._pin_attempts += 1
        return False

    @Property(str, notify=changed)
    def today(self):
        return self._today.strftime("%Y.%m.%d")

    @Property("QStringList", constant=True)
    def difficulties(self):
        return list(DIFFICULTIES)

    @Property("QVariantList", notify=catalog_changed)
    def catalog(self):
        return self._catalog

    @Property("QStringList", notify=catalog_changed)
    def availableDifficulties(self):
        available = {entry["difficulty"] for entry in self._catalog if entry["active"]}
        return [difficulty for difficulty in DIFFICULTIES if difficulty in available]

    @Slot(str, str, str, bool, result=str)
    def saveMission(self, mission_id, content, difficulty, active):
        if not self._admin_unlocked:
            return "관리자 PIN 인증이 필요합니다."
        try:
            save_mission(content, difficulty, active, mission_id)
        except ValueError as error:
            return str(error)
        except sqlite3.Error:
            return "미션을 저장할 수 없습니다. 다시 시도해 주세요."
        self.refresh()
        return ""

    @Slot(str, result=str)
    def deleteMission(self, mission_id):
        if not self._admin_unlocked:
            return "관리자 PIN 인증이 필요합니다."
        try:
            delete_mission(mission_id)
        except sqlite3.Error:
            return "미션을 삭제할 수 없습니다. 다시 시도해 주세요."
        self.refresh()
        return ""

    @Property("QVariantMap", notify=changed)
    def daily(self):
        return self._daily

    @Property("QVariantList", notify=changed)
    def records(self):
        return self._records

    @Property(str, notify=changed)
    def error(self):
        return self._error

    @Property(str, notify=calendar_changed)
    def monthTitle(self):
        return f"{self._month.year}년 {self._month.month}월"

    @Property("QVariantList", notify=calendar_changed)
    def calendarDays(self):
        days = []
        for week in calendar.Calendar().monthdayscalendar(self._month.year, self._month.month):
            for number in week:
                day = self._month.replace(day=number) if number else None
                days.append({
                    "number": number,
                    "date": day.isoformat() if day else "",
                    "today": day == self._today,
                    "completed": day in self._completed_days,
                })
        return days

    @staticmethod
    def _snapshot(record):
        return {
            "date": record.draw.date.isoformat(),
            "difficulty": record.draw.mission.difficulty,
            "content": record.draw.mission.content,
            "missionId": record.draw.mission.id,
            "completed": record.completed,
        }

    def _set_error(self, message):
        self._error = message
        self.changed.emit()

    @Slot()
    def refresh(self):
        current = date.today()
        if current != self._today:
            self._today = current
            self._month = current.replace(day=1)
            self._daily = {}
        try:
            records = list_records()
            catalog = [
                {"missionId": entry.mission.id, "content": entry.mission.content,
                 "difficulty": entry.mission.difficulty, "active": entry.active}
                for entry in list_catalog()
            ]
        except (sqlite3.Error, OSError, HistoryFormatError):
            self._set_error("미션 저장소를 열 수 없습니다. 다시 시도해 주세요.")
            self.calendar_changed.emit()
            return

        if catalog != self._catalog:
            self._catalog = catalog
            self.catalog_changed.emit()
        self._records = [self._snapshot(record) for record in records]
        today_key = self._today.isoformat()
        self._daily = next((record for record in self._records if record["date"] == today_key), {})
        self._completed_days = {record.draw.date for record in records if record.completed}
        self._set_error("")
        self.calendar_changed.emit()

    @Slot()
    def checkDate(self):
        if self._today != date.today():
            self.refresh()

    @Slot(str)
    def pick(self, difficulty):
        if self._today != date.today():
            self.refresh()
            return
        if difficulty not in DIFFICULTIES:
            return
        try:
            mission = draw_mission(active_missions(), difficulty)
            save_draw(DailyDraw(self._today, mission))
        except (sqlite3.Error, OSError, HistoryFormatError):
            self._set_error("오늘의 미션을 저장할 수 없습니다. 다시 시도해 주세요.")
            return
        except ValueError:
            self.refresh()
            self._set_error("이 난이도에 활성 미션이 없습니다.")
            return
        self.refresh()

    @Slot()
    def complete(self):
        if self._today != date.today():
            self.refresh()
            return
        try:
            draw = load_draw(self._today)
            if draw is not None:
                mark_completed(draw)
        except (sqlite3.Error, OSError, HistoryFormatError):
            self._set_error("완료 기록을 저장할 수 없습니다. 다시 시도해 주세요.")
            return
        self.refresh()

    @Slot(int)
    def changeMonth(self, offset):
        year, month = divmod(self._month.year * 12 + self._month.month - 1 + offset, 12)
        if 1 <= year <= 9999:
            self._month = date(year, month + 1, 1)
            self.calendar_changed.emit()


def create_window(controller):
    engine = QQmlApplicationEngine()
    engine.setInitialProperties({"controller": controller})
    engine.load(Path(__file__).with_name("Main.qml"))
    return engine


def main():
    application = QGuiApplication(sys.argv)
    QQuickStyle.setStyle("Basic")
    controller = MissionController()
    engine = create_window(controller)
    if not engine.rootObjects():
        return 1
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
