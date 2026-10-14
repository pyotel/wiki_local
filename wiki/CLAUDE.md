---
scope: wiki/
purpose: AI가 컴파일·유지보수하는 지식베이스 — AI 전권
---

# wiki/ — AI가 쓰는 위키

## 하위 폴더

| 폴더 | 페이지 종류 |
|---|---|
| `entities/` | 개체 — 사람, 기관, 프로젝트, 제품, 도구 |
| `concepts/` | 개념 — 방법론, 알고리즘, 이론, 아키텍처 |
| `topics/` | 도메인 주제 — 큰 화두 묶음 |
| `sources/` | 원본별 요약 — `raw/` 와 1:1 (`YYYY-MM-DD_<유형>_<제목>.md`) |
| `syntheses/` | 종합 — 비교 분석, 신규 아이디어 |
| `assets/` | 위키에 쓰는 이미지 (`![[파일명.png]]` 또는 상대경로) |

## 특수 파일
- `index.md` 카탈로그 · `log.md` 작업로그(append-only) · `_ingested.md` 인제스트 레지스트리
- `_canonical_ids.md` graphify 노드 ID 정규 사전 — `/graphify wiki/` 시 subagent 프롬프트에 전문 prepend
- `_session_state.md` 세션 간 가변 상태

## 페이지 규약
1. **YAML frontmatter** 필수 — `type`, `tags`, `sources`, `created`/`updated` (포탈이 type·tags·updated 를 칩으로 표시)
2. **Obsidian 위키링크** `[[페이지명]]` / `[[페이지명|별칭]]` — 포탈은 파일명(확장자 제외)으로 해석하므로 **파일명 = 페이지명**, 폴더 간 중복 파일명 금지
3. **모든 주장에 근거 인용** — `(출처: raw/foo.pdf)`
4. **모순은 보존** — `> ⚠️ 충돌: [[A]]는 X, [[B]]는 Y`
5. 새 페이지: inbound link 추가 + `index.md` 등록 + `log.md` 기록
