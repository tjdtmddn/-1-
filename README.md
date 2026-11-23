# -1-

## 하루 랜덤 미션 생성기

Windows에서 `하루 랜덤 미션.exe`를 더블클릭하면 앱이 열립니다. 실행 파일과 `runtime` 폴더는 같은 위치에 두세요. 기록과 미션 목록을 옮길 때는 `mission_data.json`과 `daily_missions.sqlite3`도 함께 복사합니다.

### 소스 코드에서 실행

Python 3.10 이상이 필요합니다. 데스크톱 앱은 PySide6와 Qt Quick(QML)을 사용합니다. 프로젝트 폴더에서 다음 명령을 실행합니다.

```powershell
python -m pip install -r requirements.txt
python app.py
```

PowerShell에서 프로젝트 가상 환경을 사용 중이면 활성화 과정 없이 아래처럼 직접 실행할 수 있습니다.

```powershell
.\.venv\Scripts\python.exe app.py
```

기존 터미널 버전은 `python main.py`로 실행할 수 있으며, 두 버전은 추첨·완료 기록용 `mission_data.json`과 미션 목록용 `daily_missions.sqlite3`를 공유합니다.

- **오늘의 미션**에서 난이도를 선택해 추첨합니다. 결과 화면에서 미션을 완료할 수 있습니다.
- **미션관리**에서 미션을 추가·수정·삭제할 수 있습니다. 수정 화면에서 활성화 여부를 바꿀 수 있습니다. 활성화된 미션만 새 추첨에 사용되며, 기존 추첨과 완료 기록은 유지됩니다.
- **기록**에서 달력이나 목록에서 날짜를 선택하면 해당 미션과 완료 상태를 볼 수 있습니다.

실행 시 컴퓨터의 현지 날짜를 기준으로 그날 저장된 미션을 조회합니다. 처음 실행한 날에는 난이도를 선택하고, 같은 날 다시 실행하면 기존 결과가 표시됩니다. 결과는 팀원의 `MissionStore`를 사용해 `mission_data.json`에 날짜별로 저장합니다. 첫 실행 때 기존 SQLite 기록을 한 번 가져옵니다. 같은 날짜에 다른 미션이 있으면 JSON 기록을 사용하며, 미션 내용이 같으면 완료 상태를 합칩니다. 이전 JSON에서 기본 목록에 없는 미션은 난이도 없이 표시합니다.

### 팀원 기능과 연결하기

- `missions.py`의 `Mission(id, content, difficulty)`는 기본 미션과 사용자 미션에 공통으로 사용할 수 있습니다. 난이도는 `DIFFICULTIES`에 있는 `쉬움`, `보통`, `어려움` 중 하나를 사용하세요. 사용자 미션에는 기본 미션과 겹치지 않는 고유 ID를 부여하세요.
- `draw.py`의 `draw_mission(missions, difficulty)`에 기본 미션과 사용자 미션을 합친 목록을 넘길 수 있습니다. 선택한 난이도의 미션 한 개를 반환하며, 해당 난이도의 미션이 없으면 `ValueError`를 발생시킵니다.
- 완료 기록 기능은 `draw_storage.py`의 `load_draw(조회할_날짜)`로 `DailyDraw`를 가져올 수 있습니다. 결과는 `date`와 `mission`을 가지며, 해당 날짜에 추첨 이력이 없으면 `None`을 반환합니다. 완료 기록을 추첨 결과와 연결할 때는 `date`와 `mission.id`를 사용하세요. 추첨 당시의 내용과 난이도는 저장된 결과에서도 읽을 수 있습니다.
