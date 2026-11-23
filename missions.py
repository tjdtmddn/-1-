from dataclasses import dataclass


DIFFICULTIES = ("쉬움", "보통", "어려움")


@dataclass(frozen=True)
class Mission:
    id: str
    content: str
    difficulty: str


EASY, NORMAL, HARD = DIFFICULTIES

MISSIONS = (
    Mission("basic-01", "물 한 컵 더 마시기", EASY),
    Mission("basic-02", "10분 산책하기", NORMAL),
    Mission("basic-03", "책 10쪽 읽기", HARD),
    Mission("basic-04", "주변 정리 5분 하기", NORMAL),
    Mission("basic-05", "고마운 사람에게 안부 전하기", HARD),
    Mission("basic-06", "스트레칭 5분 하기", EASY),
    Mission("basic-07", "오늘의 생각 한 줄 적기", EASY),
    Mission("basic-08", "계단 한 층 걸어 올라가기", NORMAL),
)
