---
type: ai-context
purpose: 이 볼트에서 작업하는 모든 AI(LLM)가 매 작업마다 가장 먼저 읽는 행동 지침
last_updated: 2026-10-13
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
- 질문 처리: graphify 그래프(있으면) → wiki 본문 → raw 드릴다운 순으로 근거 확보, `[[페이지명]]`·경로 인용. 근거 없으면 "위키에 없음".
- 의미 있는 종합은 `wiki/syntheses/` 로 환원, `wiki/log.md` append.
- 셸 명령은 Windows(Git Bash)·Linux 양쪽에서 돌도록 `python` (표준 라이브러리) 우선. `python3`·GNU 전용 옵션 의존 금지.
