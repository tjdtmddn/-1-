import sqlite3
import sys
from datetime import date

from draw import draw_mission
from draw_storage import DailyDraw, load_draw, save_draw
from mission_catalog import active_missions
from missions import DIFFICULTIES


def choose_difficulty(available=DIFFICULTIES) -> str:
    options = {
        str(number): difficulty
        for number, difficulty in enumerate(DIFFICULTIES, 1)
        if difficulty in available
    }
    print("난이도를 선택하세요.")
    for number, difficulty in options.items():
        print(f"{number}. {difficulty}")

    while True:
        choice = input("번호 입력: ").strip()
        difficulty = options.get(choice)
        if difficulty is not None:
            return difficulty
        print("잘못된 입력입니다. 메뉴에 있는 번호를 입력해 주세요.")


def main() -> int:
    today = date.today()
    try:
        result = load_draw(today)
        if result is None:
            missions = active_missions()
            if not missions:
                print("추첨할 수 있는 활성 미션이 없습니다. 미션관리에서 미션을 추가하거나 활성화해 주세요.")
                return 1
            difficulty = choose_difficulty({mission.difficulty for mission in missions})
            mission = draw_mission(missions, difficulty)
            result = save_draw(DailyDraw(today, mission))
    except (EOFError, KeyboardInterrupt):
        print("\n미션 선택을 취소했습니다.")
        return 1
    except sqlite3.Error as error:
        print(f"추첨 결과 저장소를 사용할 수 없습니다. ({error})", file=sys.stderr)
        return 1

    print("\n오늘의 미션")
    print(f"날짜: {result.date.isoformat()}")
    print(f"난이도: {result.mission.difficulty}")
    print(f"미션: {result.mission.content}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
