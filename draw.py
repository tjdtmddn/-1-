import random
from collections.abc import Iterable

from missions import Mission


def draw_mission(missions: Iterable[Mission], difficulty: str) -> Mission:
    candidates = [mission for mission in missions if mission.difficulty == difficulty]
    if not candidates:
        raise ValueError(f"'{difficulty}' 난이도의 미션이 없습니다.")
    return random.choice(candidates)
