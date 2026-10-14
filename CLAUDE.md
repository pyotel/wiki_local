---
type: ai-context
purpose: 이 볼트에서 작업하는 모든 AI(LLM)가 매 작업마다 가장 먼저 읽는 행동 지침
last_updated: 2026-10-14
---

# CLAUDE.md — 로컬 위키 포탈 (wiki_local)

> 서버 없이 Windows PC 한 대에서 운영하는 Karpathy LLM Wiki. 사람은 `portal.html`(브라우저)로 자료를 올리고 위키를 읽고,
> AI(Claude Code)는 이 폴더에서 `/ingest`·`/query`·`/lint` 로 위키를 컴파일·유지보수한다.

## 세션 시작 시 읽기 (이 순서)
1. `CLAUDE.md` (이 파일) — 불변 규칙
2. `wiki/_session_state.md` — 가변 상태 (직전 작업·in-progress)
3. `wiki/log.md` 마지막 100줄
4. `portal_data/issues.json` — 사용자 이슈 (AI 처리 요청이 있으면 대상)
5. `wiki/index.md` 통계 섹션

## 3계층

| 계층 | 경로 | 소유자 | 역할 |
|---|---|---|---|
| **Raw** | `raw/` | 사람 (불변) | 원본. AI는 **읽기만** (md frontmatter `ingest_status` 갱신·사이드카 생성만 허용) |
| **Wiki** | `wiki/` | **AI (전권)** | 컴파일된 마크다운 지식베이스 — 규약은 `wiki/CLAUDE.md` |
| **Output** | `Output/` | AI 초안 → 사람 승인 | 보고서·슬라이드·프로토타입 |

- **raw 파일 설명**: 포탈 업로드 시 사용자가 적은 설명이 `portal_data/raw_meta.json` (`{"raw/경로": {"description": ...}}`) 에 있다. **ingest 시 반드시 참고**.
- **인제스트 대기 판정** (포탈과 `/ingest` 공통): md 는 `ingest_status: done` 이 없으면 대기, 그 외 파일은 `<파일명>.ingest.md` 사이드카가 없으면 대기.

## 포탈 (portal.html — 서버 없음)

- `open-portal.bat` 더블클릭 → Edge 로 `portal.html` 열림 → 이 폴더 선택 (최초 1회, 이후 기억)
- 브라우저의 File System Access API 로 이 폴더를 **직접** 읽고 쓴다. 백엔드·포트·Docker 없음.
- 포탈이 쓰는 파일: `raw/**` (업로드·메모), `portal_data/raw_meta.json`, `portal_data/issues.json` — 그 외엔 읽기만.
- 그래프: `graphify-out/graph.html` 이 있으면 🕸 버튼으로 연다.

## 작업 규칙
- **한국어**로 응답. 간결하게.
- **위키 우선 (모든 질의·작업)**: `/query` 뿐 아니라 이 세션의 **모든 질문·작업**(문서 작성, Output 초안, 이슈 처리, 일반 질문 등)은 답하거나 손대기 전에 이 위키를 먼저 참고한다. 일반 지식으로 바로 답하지 말 것.
  1. **그래프** — `graphify-out/` (`graph.json`·`GRAPH_REPORT.md`) 이 있으면 관련 노드·이웃·커뮤니티로 범위를 좁힌다
  2. **위키 본문** — `wiki/index.md` → 관련 `entities/`·`concepts/`·`topics/`·`syntheses/` 페이지와 `[[링크]]` 를 따라 읽는다
  3. **raw 드릴다운** — 위키가 부족하거나 수치·원문 확인이 필요하면 `raw/` 원본 (`portal_data/raw_meta.json` 설명 포함)
- 근거는 `[[페이지명]]`·경로로 인용. 위키에 근거가 없으면 "위키에 없음" 이라 밝히고, 외부·일반 지식은 그와 구분해 표시.
- 위키 내용과 충돌·누락을 발견하면 작업 후 해당 페이지 갱신(또는 `/lint` 제안).
- 의미 있는 종합·결론은 `wiki/syntheses/` 로 환원, `wiki/log.md` append.
- 셸 명령은 Windows(Git Bash)·Linux 양쪽에서 돌도록 `python` (표준 라이브러리) 우선. `python3`·GNU 전용 옵션 의존 금지.
