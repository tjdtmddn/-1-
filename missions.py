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
    Mission("basic-09", "창문 열고 깊게 숨쉬기", EASY),
    Mission("basic-10", "좋아하는 노래 한 곡 듣기", EASY),
    Mission("basic-11", "거울을 보고 미소 짓기", EASY),
    Mission("basic-12", "귀여운 동물 사진 보기", EASY),
    Mission("basic-13", "오늘 입은 옷 구석구석 살펴보기", EASY),
    Mission("basic-14", "손가락 마사지 1분 하기", EASY),
    Mission("basic-15", "하늘 사진 한 장 찍기", EASY),
    Mission("basic-16", "가장 가까운 문에 하트 붙이기", EASY),
    Mission("basic-17", "오늘의 다짐 한 글자 쓰기", EASY),
    Mission("basic-18", "좋아하는 간식 이름 떠올리기", EASY),
    Mission("basic-19", "자판기 앞에서 인사하기", EASY),
    Mission("basic-20", "아무 노래나 흥얼거리기", EASY),
    Mission("basic-21", "책상 위 펜 하나만 예쁘게 놓기", EASY),
    Mission("basic-22", "손에 닿는 물건 하나 감사하기", EASY),
    Mission("basic-23", "거울 셀카 한 장 찍기", EASY),
    Mission("basic-24", "오늘 기분을 이모지로 표현하기", EASY),
    Mission("basic-25", "집에서 제자리 걷기 100걸음", NORMAL),
    Mission("basic-26", "어색한 자세로 10초 버티기", NORMAL),
    Mission("basic-27", "만난 사람마다 인사 건네기", NORMAL),
    Mission("basic-28", "방에서 낯선 장소 구석 찾기", NORMAL),
    Mission("basic-29", "테이블 위 물건 3개로 전시 만들기", NORMAL),
    Mission("basic-30", "좋아하는 말로 자작 시 쓰기", NORMAL),
    Mission("basic-31", "안 쓰는 물건 하나 사진 찍기", NORMAL),
    Mission("basic-32", "오늘 들은 소리 3가지 기록하기", NORMAL),
    Mission("basic-33", "발바닥 문지르기 2분 하기", NORMAL),
    Mission("basic-34", "집안의 작은 보물 찾기", NORMAL),
    Mission("basic-35", "가슴을 펴고 1분 자세 유지하기", NORMAL),
    Mission("basic-36", "눈 감고 주변 소리 듣기 1분", NORMAL),
    Mission("basic-37", "오늘 본 색깔 5개 적기", NORMAL),
    Mission("basic-38", "핸드폰 대신 10분 동안 종이 보기", NORMAL),
    Mission("basic-39", "반대 손으로 이름 세 번 쓰기", NORMAL),
    Mission("basic-40", "신발 한 켤레를 예쁘게 정돈하기", NORMAL),
    Mission("basic-41", "가족이나 친구에게 농담 건네기", NORMAL),
    Mission("basic-42", "일하던 자세를 유쾌하게 바꿔보기", HARD),
    Mission("basic-43", "외출 전 춤을 한 곡에 맞춰 추기", HARD),
    Mission("basic-44", "오늘의 새로운 별명 지어보기", HARD),
    Mission("basic-45", "거울 앞에서 30초 즉석 발표하기", HARD),
    Mission("basic-46", "핸드폰으로 짧은 코믹 영상 만들기", HARD),
    Mission("basic-47", "오늘의 공상을 소설로 한 줄 쓰기", HARD),
    Mission("basic-48", "가장 따뜻한 물건을 찾아 포옹하기", HARD),
    Mission("basic-49", "친구에게 뜻밖의 칭찬 보내기", HARD),
    Mission("basic-50", "스스로 이상한 사물극 시도하기", HARD),
)
