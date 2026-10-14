![로컬 위키 포탈 — 내 PC 속 도서관](docs/banner.jpg)

# 📚 로컬 위키 포탈 (wiki_local)

**서버 없이, 리눅스 몰라도** — Windows/Mac PC 한 대에서 **Claude 데스크탑 앱의 Code 모드**로 돌리는
[Karpathy식 LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 포탈.

- 사람은 브라우저로 `portal.html` 을 열어 자료를 올리고 위키를 읽는다 (File System Access API 로 폴더를 직접 읽고 씀).
- AI(Claude Code)는 이 폴더에서 `/ingest`·`/query`·`/lint` 로 위키를 컴파일·유지보수한다.
- 백엔드·포트·Docker·nginx 없음. 폴더 하나 복사하면 끝.

| 장점 | 단점 |
|---|---|
| 서버·클라우드 불필요, 설치는 Claude 데스크탑 + Edge/Chrome 뿐 | 온라인 공유 불가 → **사실상 1인용** |
| 리눅스·터미널 몰라도 됨 | 동시 편집 잠금 없음 (공유 폴더에 둘 경우 나중 저장이 이김) |
| 자료가 내 PC 밖으로 안 나감 (AI 호출 제외) | 브라우저는 Edge·Chrome 만 (Firefox·Safari 미지원) |

## 3계층

| 계층 | 경로 | 누가 | 역할 |
|---|---|---|---|
| Raw | `raw/` | 사람 (포탈 업로드·메모) | 원본, 불변 |
| Wiki | `wiki/` | AI (Claude Code) | `/ingest` 로 컴파일된 마크다운 지식베이스 |
| Output | `Output/` | AI 초안 → 사람 | 보고서·슬라이드 |

## 준비물
- [Claude 데스크탑 앱](https://claude.ai/download) (Pro/Max 구독, **Code** 탭 사용) — 또는 Claude Code CLI
- Microsoft Edge 또는 Google Chrome
- (선택) Python 3 — PDF·PPT·엑셀·HWP 추출용: `pip install pypdf python-pptx openpyxl pyhwp`
- (선택) [graphify](https://github.com/safishamsi/graphify) — 지식 그래프: `pip install graphifyy` 후 `graphify install --platform claude` (Claude Code `/graphify` 스킬 설치)

## 시작
1. 이 저장소를 내려받아 원하는 위치에 둔다 (GitHub → Code → Download ZIP → 압축 해제, 예: `D:\내위키`)
2. **포탈 열기**
   - Windows: `open-portal.bat` 더블클릭 (Edge 로 열림)
   - Mac: `portal.html` 을 Chrome 으로 열기 (Chrome 아이콘에 끌어다 놓기)
   - **📂 볼트 폴더 선택** → 이 폴더 선택 → "파일 편집 허용". 이후엔 기억하고, 브라우저 재시작 뒤엔 「↻ 다시 열기」 한 번
3. 📁 Raw 탭에서 자료 업로드(설명 함께) 또는 📝 메모 작성 → 🏠 홈에 **인제스트 대기** 로 표시
4. **인제스트** — Claude 데스크탑 → **Code** 탭 → 이 폴더를 작업 폴더로 열고 `/ingest` 입력
   (Windows + CLI 사용자는 `ingest.bat` 더블클릭도 가능) → `wiki/` 생성·갱신 → 포탈에서 새로고침
5. 질문은 같은 Code 세션에서 `/query <질문>`, 정기 점검은 `/lint`

## 포탈 기능 (`portal.html` 단일 파일)
- 🏠 **홈** — 통계, 다가오는 일정, 인제스트 대기 목록, 최근 변경 페이지, `wiki/log.md` 최근 5건
- 📁 **Raw** — 폴더 탐색·생성, 드래그 업로드 + 설명(`portal_data/raw_meta.json`), md 메모 작성, 대기/반영 배지
- 📚 **위키** — 폴더 트리, 전문 검색, 마크다운 뷰어 (frontmatter 칩·`[[위키링크]]`·`![[이미지]]`·상대 링크), `#wiki=경로` 딥링크·뒤로가기
- 📅 **일정** — 월간 달력, 일정 등록·수정(여러 날·시간·장소), 미완료 이슈 기한 함께 표시, 홈에 14일 이내 일정, `.ics` 내보내기(구글·아웃룩 캘린더 가져오기) (`portal_data/schedule.json` — `/ingest` 가 공고 마감 등을 자동 등록하기도 함)
- 🐛 **이슈** — 기한·상태 관리 (`portal_data/issues.json`, AI 에게 맡길 일도 여기에)
- 🕸 **그래프** — `graphify-out/graph.html` 을 포탈 안에 임베드 + 허브 노드·커뮤니티 목록 (노드 클릭 → 그래프 포커스, 📄 → 위키 페이지), `GRAPH_REPORT.md` 보기

## AI 쪽 (Claude Code)
- 규칙: `CLAUDE.md` (루트), `wiki/CLAUDE.md`, `raw/CLAUDE.md` — Code 모드가 폴더를 열면 자동으로 읽는다
- 프로젝트 스킬: `.claude/skills/ingest`·`query`·`lint` — 폴더째 복사하면 같이 따라간다
- 야간 자동 인제스트 (선택, Windows + Claude Code CLI, 관리자 cmd 1회):
  ```bat
  schtasks /create /tn wiki_local_ingest /sc daily /st 21:00 /tr "cmd /c cd /d D:\내위키 && claude -p /ingest --permission-mode bypassPermissions >> ingest.log 2>&1"
  ```

## 개인 자료 주의
`.gitignore` 가 `raw/`·`wiki/` 내용과 `portal_data/` 를 제외하므로, 이 저장소를 포크해 써도 내 자료는 커밋되지 않는다.

## 라이선스
MIT. `assets/marked.min.js` 는 [marked](https://github.com/markedjs/marked) (MIT).
상단 배너: "[Indiana Supreme Court Law Library bookshelves](https://commons.wikimedia.org/w/index.php?curid=153694365)" by LingLass, [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) (Openverse 경유, 잘라서 사용).
