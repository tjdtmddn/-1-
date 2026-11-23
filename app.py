import calendar
import json
import random
import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import messagebox, ttk


MISSIONS = (
    "물 한 컵 더 마시기",
    "10분 산책하기",
    "책 10쪽 읽기",
    "주변 정리 5분 하기",
    "고마운 사람에게 안부 전하기",
    "스트레칭 5분 하기",
    "오늘의 생각 한 줄 적기",
    "계단 한 층 걸어 올라가기",
)


class MissionStore:
    def __init__(self, path: Path, missions=MISSIONS):
        self.path = Path(path)
        self.missions = tuple(missions)
        if not self.missions:
            raise ValueError("미션 목록이 비어 있습니다.")

        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as file:
                self.records = json.load(file)
            self._validate_records()
        else:
            self.records = {}

    def _validate_records(self):
        if not isinstance(self.records, dict):
            raise ValueError("기록 파일의 형식이 올바르지 않습니다.")
        for day, record in self.records.items():
            if (
                not isinstance(day, str)
                or not isinstance(record, dict)
                or not isinstance(record.get("mission"), str)
                or not isinstance(record.get("completed"), bool)
            ):
                raise ValueError("기록 파일에 올바르지 않은 미션 데이터가 있습니다.")

    def get_daily_mission(self, day: date) -> dict:
        day_key = day.isoformat()
        if day_key not in self.records:
            self.records[day_key] = {
                "mission": random.choice(self.missions),
                "completed": False,
            }
            try:
                self._save()
            except OSError:
                del self.records[day_key]
                raise
        return self.records[day_key]

    def complete(self, day: date):
        record = self.get_daily_mission(day)
        was_completed = record["completed"]
        record["completed"] = True
        try:
            self._save()
        except OSError:
            record["completed"] = was_completed
            raise

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(self.path.suffix + ".tmp")
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(self.records, file, ensure_ascii=False, indent=2)
        temporary_path.replace(self.path)


class MissionApp:
    def __init__(self, root: tk.Tk, store: MissionStore):
        self.root = root
        self.store = store
        self.today = date.today()
        self.current_month = self.today.replace(day=1)
        self.selected_day = self.today
        self.today_record = self.store.get_daily_mission(self.today)

        root.title("하루 랜덤 미션")
        root.geometry("760x640")
        root.minsize(620, 560)

        self.tabs = ttk.Notebook(root)
        self.today_tab = ttk.Frame(self.tabs, padding=18)
        self.history_tab = ttk.Frame(self.tabs, padding=18)
        self.tabs.add(self.today_tab, text="오늘의 미션")
        self.tabs.add(self.history_tab, text="미션 기록")
        self.tabs.pack(fill="both", expand=True)

        self._build_today_tab()
        self._build_history_tab()
        self._refresh_calendar()
        self._refresh_history()

    def _build_today_tab(self):
        ttk.Label(
            self.today_tab, text="오늘의 랜덤 미션", font=("맑은 고딕", 20, "bold")
        ).pack(pady=(0, 12))

        self.mission_label = ttk.Label(
            self.today_tab,
            text=self.today_record["mission"],
            font=("맑은 고딕", 15),
            wraplength=600,
        )
        self.mission_label.pack(pady=8)

        self.complete_button = ttk.Button(
            self.today_tab, text="미션 완료!", command=self._complete_mission
        )
        self.complete_button.pack(pady=6)
        self.status_label = ttk.Label(self.today_tab, font=("맑은 고딕", 10))
        self.status_label.pack(pady=(0, 12))

        calendar_header = ttk.Frame(self.today_tab)
        calendar_header.pack(fill="x", pady=(8, 4))
        ttk.Button(calendar_header, text="◀", width=4, command=self._previous_month).pack(
            side="left"
        )
        self.month_label = ttk.Label(
            calendar_header, font=("맑은 고딕", 13, "bold"), anchor="center"
        )
        self.month_label.pack(side="left", fill="x", expand=True)
        ttk.Button(calendar_header, text="▶", width=4, command=self._next_month).pack(
            side="right"
        )

        self.calendar_frame = ttk.Frame(self.today_tab)
        self.calendar_frame.pack(fill="both", expand=True)

    def _build_history_tab(self):
        ttk.Label(
            self.history_tab, text="날짜별 미션 기록", font=("맑은 고딕", 18, "bold")
        ).pack(anchor="w", pady=(0, 12))

        content = ttk.Frame(self.history_tab)
        content.pack(fill="both", expand=True)
        self.history_list = tk.Listbox(content, width=24, height=18, exportselection=False)
        self.history_list.pack(side="left", fill="y")
        self.history_list.bind("<<ListboxSelect>>", self._show_history_detail)
        scrollbar = ttk.Scrollbar(
            content, orient="vertical", command=self.history_list.yview
        )
        scrollbar.pack(side="left", fill="y")
        self.history_list.configure(yscrollcommand=scrollbar.set)

        self.history_detail = ttk.LabelFrame(
            content,
            text="선택한 날짜",
            padding=(18, 14),
        )
        self.history_detail.pack(side="left", fill="both", expand=True, padx=20)
        self.history_date = ttk.Label(
            self.history_detail, font=("맑은 고딕", 11, "bold")
        )
        self.history_date.pack(anchor="w", pady=(0, 14))
        ttk.Label(
            self.history_detail, text="오늘의 미션", font=("맑은 고딕", 10)
        ).pack(anchor="w")
        self.history_mission = ttk.Label(
            self.history_detail,
            font=("맑은 고딕", 16, "bold"),
            foreground="#B52F2F",
            wraplength=400,
            justify="left",
        )
        self.history_mission.pack(anchor="w", fill="x", pady=(4, 14))
        self.history_status = ttk.Label(
            self.history_detail, font=("맑은 고딕", 10)
        )
        self.history_status.pack(anchor="w")

    def _complete_mission(self):
        try:
            self.store.complete(self.today)
        except (OSError, ValueError) as error:
            messagebox.showerror("저장 오류", f"미션 기록을 저장하지 못했습니다.\n{error}")
            return

        self.today_record = self.store.records[self.today.isoformat()]
        self._update_completion_status()
        self._refresh_calendar()
        self._refresh_history()

    def _update_completion_status(self):
        completed = self.today_record["completed"]
        self.status_label.configure(
            text="완료 도장이 찍혔어요! 🎉" if completed else "미션을 완료하면 달력에 도장이 찍혀요."
        )
        self.complete_button.configure(
            text="미션완료" if completed else "미션 완료!",
            state="disabled" if completed else "normal",
        )

    def _refresh_calendar(self):
        for child in self.calendar_frame.winfo_children():
            child.destroy()

        self.month_label.configure(
            text=f"{self.current_month.year}년 {self.current_month.month}월"
        )
        weekdays = ("월", "화", "수", "목", "금", "토", "일")
        for column, weekday in enumerate(weekdays):
            ttk.Label(
                self.calendar_frame, text=weekday, anchor="center"
            ).grid(row=0, column=column, sticky="nsew", padx=2, pady=4)
            self.calendar_frame.grid_columnconfigure(column, weight=1)

        for row, week in enumerate(
            calendar.monthcalendar(self.current_month.year, self.current_month.month),
            start=1,
        ):
            self.calendar_frame.grid_rowconfigure(row, weight=1)
            for column, day_number in enumerate(week):
                if day_number == 0:
                    continue
                day = self.current_month.replace(day=day_number)
                record = self.store.records.get(day.isoformat())
                cell = tk.Canvas(
                    self.calendar_frame,
                    width=82,
                    height=76,
                    highlightthickness=0,
                    background=ttk.Style().lookup("TFrame", "background")
                    or self.root.cget("background"),
                    cursor="hand2",
                )
                cell.grid(
                    row=row, column=column, sticky="nsew", padx=2, pady=2
                )

                def redraw_cell(
                    event,
                    canvas=cell,
                    number=day_number,
                    is_today=day == self.today,
                    is_completed=bool(record and record["completed"]),
                ):
                    self._draw_calendar_cell(
                        canvas,
                        event.width,
                        event.height,
                        number,
                        is_today,
                        is_completed,
                    )

                cell.bind(
                    "<Configure>", redraw_cell
                )
                cell.bind(
                    "<Button-1>",
                    lambda _event, selected=day: self._select_calendar_day(selected),
                )
                if day == self.today:
                    cell.configure(highlightthickness=1, highlightbackground="#5B8DEF")

    @staticmethod
    def _draw_calendar_cell(canvas, width, height, day_number, is_today, is_completed):
        canvas.delete("all")
        date_font_size = max(8, min(10, int(height * 0.18)))
        canvas.create_text(
            width / 2,
            max(6, date_font_size * 0.7),
            text=str(day_number),
            font=(
                "맑은 고딕",
                date_font_size,
                "bold" if is_today else "normal",
            ),
        )

        if not is_completed:
            return

        date_bottom = date_font_size * 1.5
        stamp_top = max(date_bottom + 2, height * 0.3)
        diameter = min(width - 8, height - stamp_top - 3)
        if diameter <= 0:
            return

        center_x = width / 2
        center_y = stamp_top + diameter / 2
        canvas.create_oval(
            center_x - diameter / 2,
            center_y - diameter / 2,
            center_x + diameter / 2,
            center_y + diameter / 2,
            outline="#C83D3D",
            width=2,
            fill="#FFF4F2",
        )
        inner_diameter = max(0, diameter - 7)
        canvas.create_oval(
            center_x - inner_diameter / 2,
            center_y - inner_diameter / 2,
            center_x + inner_diameter / 2,
            center_y + inner_diameter / 2,
            outline="#C83D3D",
            width=1,
        )
        stamp_font_size = max(6, min(9, int(diameter * 0.18)))
        canvas.create_text(
            center_x,
            center_y,
            text="미션\n완료",
            fill="#B52F2F",
            font=("맑은 고딕", stamp_font_size, "bold"),
            justify="center",
        )

    def _select_calendar_day(self, day: date):
        self.selected_day = day
        self.tabs.select(self.history_tab)
        self._refresh_history()

    def _refresh_history(self):
        self.history_list.delete(0, tk.END)
        self.history_days = sorted(self.store.records, reverse=True)
        for day_key in self.history_days:
            record = self.store.records[day_key]
            stamp = "미션완료" if record["completed"] else "진행 중"
            self.history_list.insert(tk.END, f"{day_key}  {stamp}")

        if self.selected_day.isoformat() in self.history_days:
            index = self.history_days.index(self.selected_day.isoformat())
            self.history_list.selection_set(index)
            self.history_list.see(index)
        self._show_history_record(
            self.selected_day.isoformat(),
            self.store.records.get(self.selected_day.isoformat()),
        )

    def _show_history_record(self, day_key, record):
        self.history_date.configure(text=day_key)
        if record is None:
            self.history_mission.configure(
                text="이 날짜에는 저장된 미션이 없습니다.", foreground="#666666"
            )
            self.history_status.configure(text="미션 기록 없음")
            return

        self.history_mission.configure(
            text=record["mission"], foreground="#B52F2F"
        )
        status = "미션완료" if record["completed"] else "진행 중"
        self.history_status.configure(text=f"상태: {status}")

    def _show_history_detail(self, _event):
        selection = self.history_list.curselection()
        if not selection:
            return
        day_key = self.history_days[selection[0]]
        self.selected_day = date.fromisoformat(day_key)
        self._show_history_record(day_key, self.store.records[day_key])

    def _previous_month(self):
        year, month = self.current_month.year, self.current_month.month - 1
        if month == 0:
            year, month = year - 1, 12
        self.current_month = self.current_month.replace(year=year, month=month)
        self._refresh_calendar()

    def _next_month(self):
        year, month = self.current_month.year, self.current_month.month + 1
        if month == 13:
            year, month = year + 1, 1
        self.current_month = self.current_month.replace(year=year, month=month)
        self._refresh_calendar()


def main():
    data_path = Path(__file__).with_name("mission_data.json")
    root = tk.Tk()
    try:
        store = MissionStore(data_path)
        app = MissionApp(root, store)
        app._update_completion_status()
    except (OSError, json.JSONDecodeError, ValueError) as error:
        root.withdraw()
        messagebox.showerror("기록 불러오기 오류", f"미션 기록을 불러오지 못했습니다.\n{error}")
        root.destroy()
        return

    root.mainloop()


if __name__ == "__main__":
    main()
