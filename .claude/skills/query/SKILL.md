---
name: query
description: LLM Wiki 질문 답변 — wiki/ 마크다운 + graphify subgraph + raw 폴백을 결합해 답한다 . 사용자가 "/query <질문>" 또는 "위키에서 X 찾아줘 / X에 대해 알려줘"처럼 물으면 사용. 의미 있는 답변은 wiki/syntheses/로 환원해 지식이 사라지지 않게 한다.
---

# /query — LLM Wiki 질의응답

> **벡터 DB 없음.** graphify subgraph + 키워드 grep (조사 strip) + 위키링크 traversal + raw 드릴다운 — 서버 없이 Claude Code 세션이 직접 retrieval·추론한다.

## 절대 원칙
- **모든 사실 주장에 인용** — `[[페이지명]]` 또는 `wiki/<경로>.md:LINE`
- **추측 금지** — 위키·raw 어디에도 없으면 "근거 없음 → 외부 검색·신규 ingest 권장" 솔직히 표시
- 의미 있는 답변은 **`wiki/syntheses/`로 환원** (대화 히스토리에 묻히지 않게)

## 단계

### 0. 동기화 (git 저장소일 때만)

로컬 단독 운영이 기본. 볼트가 git 저장소이고 원격(origin)이 있을 때만 먼저 `git pull --rebase --no-edit` 로 흡수한다. git 이 없거나 원격이 없으면 이 단계는 건너뛴다.

### 1. graphify subgraph (구조적 진입점)
```bash
graphify query "<질문>" --budget 2000
# 깊은 체인 추적이면: graphify query "..." --dfs --budget 3000
```
- BFS depth=2 로 매칭 노드 + 1-hop 이웃 dump
- "No matching nodes found" 면 다음 단계로
- subgraph 의 `src=<경로>` 행에서 후보 페이지 경로 수집

### 2. 키워드 grep (조사·합성어 처리)
질문에서 토큰 추출 후 wiki/ 안 .md 매칭:
```bash
# 한국어 조사는 떼기. 예: "예산은" → "예산"
# 숫자+한글 합성어 보존 + 변형. 예: "2차년도" + "차년도"
grep -rln "<token1>" wiki/ | head
grep -rln "<token2>" wiki/ | head
```
실용적으로는 Read 도구로 직접 토큰 hit 횟수 ranking. meta 파일 (`index.md`, `log.md`, `_ingested.md`, `CLAUDE.md`) 은 제외.

### 3. 후보 페이지 통합 + 본문 읽기
- (1) graphify subgraph 의 src 경로 + (2) grep 결과 → 합쳐 **top 8 페이지** 선정
- 각 페이지 Read (frontmatter 의 `sources`, `tags` 도 확인)
- 본문 안 `[[X]]` 위키링크 → **1-hop 까지** 추가 traversal (그 이상은 컨텍스트 폭발)

### 4. raw/ 폴백 (wiki 비면)
wiki 결과 0건이거나 질문이 raw 영역 (인제스트 안 된 새 자료) 일 때:
```bash
grep -rln "<token>" raw/ --include="*.md"
```
- raw .md 본문 직접 read. PDF/HWP/PPTX 는 인제스트 시 wiki/sources/ 에 텍스트 추출돼있을 가능성이 더 큼.
- 핵심 원본은 wiki source 페이지 frontmatter `sources` 따라 raw 까지 드릴다운.

### 5. 답변 작성

#### 일반 형식
- **결론** (1~2 문장)
- **근거** — 위키 페이지 인용 표 또는 불릿 (구체적 수치·인용 포함)
- **불확실/한계** (있으면)
- **관련 페이지** (사용자가 더 파고들 수 있도록)

#### 비교 질문
표 형식. 행 = 비교 대상, 열 = 비교 차원, 셀 = 인용 포함.

#### 평가 질문 ("이 아이디어 어때?", "이 RFP 적합?")
[[조인표]]의 **3대 기준 + 사회임팩트** 매트릭스:
| 기준 | 평가 | 근거 |
|---|---|---|
| 상용화 가능성 | ✓/✗/△ | ... |
| 실증 가능성 | ✓/✗/△ | ... |
| 기술적 신규성 | ✓/✗/△ | ... |
| 사회문제 임팩트 | ✓/✗/△ | ... |

### 6. wiki 환원 — **기준 강화 (2026-05-11~)**

`wiki/syntheses/` 는 **사람이 검토할 가치가 있는 종합·아이디어·평가 매트릭스의 보관소**다. 단순 검색·요약·인용은 syntheses 가 아닌 **답변 텍스트 자체로 충분**. 자동 저장은 위키를 빠르게 노이즈로 오염시키므로 **기본 = 저장 안 함**.

#### 저장 트리거 — 다음 중 하나만 충족:

**A. 사용자 명시적 요청** (가장 강한 시그널)
- "저장해", "syntheses 에 추가해", "이거 보관해", "위키에 박아둬", "기록해 둬" 등 직접 표현

**B. 진짜 종합 (모든 조건 동시 충족, 매우 드물게)**
1. **5개 이상의 다른 source 페이지** 종합 (단일 출처 인용 ❌)
2. **신규 통찰** — 기존 페이지 어디에도 없는 결론·평가·아이디어 (기존 정보 재배열 ❌)
3. **구조화된 형식** — 표·평가 매트릭스·과제 후보·비교 차트
4. **자산화 가능** — 향후 보고서/제안서 작성 시 직접 끌어쓸 수 있는 형태

#### 절대 저장 ❌ (노이즈 차단)
- 단순 사실 검색 ("X가 무엇이지?", "Y의 값은?", "Z 페이지 요약")
- 기존 페이지 한 두개 인용 답
- "근거 없음" / "정보 없음" 답
- 사용자가 분명히 단발성 질문으로 던진 경우 (어조·맥락으로 판단)
- 4문단 이상이라도 신규 통찰 없으면 저장 ❌

#### 판단 모호하면 — 저장하지 말고 사용자에게 물어보기
"이 답변 syntheses 에 보관할까요? (구조화·자산화 가치 X 측면에서)" 식 짧은 확인.

#### 저장 형식 (저장하기로 결정한 경우만)
- `wiki/syntheses/YYYY-MM-DD_<짧은-제목>.md`
- frontmatter: `type: synthesis`, `status: draft`, `sources: [관련 페이지 list]`, `tags: [...]`
  - `status: draft` = 사람 검토 대기. 검토 후 `reviewed` 로 승급.
  - **`status: web-auto` 는 사용 금지** — 웹 자동 저장 트랙 자체가 폐지됨 (2026-05-11)
- 본문: "## 원 질문" + "## 답변" + "## 신규 통찰" + "## 출처" 4섹션 명확히
- `wiki/index.md` syntheses 섹션 + `wiki/log.md` 에 query 항목 추가:
  ```
  ## [YYYY-MM-DD] query  | <질문 한 줄>
  - 답변 환원: [[<synthesis 페이지>]]
  - 참고 페이지: [[A]] [[B]] [[C]]
  ```

### 7. 사용자에게 결과 전달
짧고 직접적으로. 마크다운 표·인용 활용. 답변 자체가 핵심 출력 — 메타 코멘트 없이.

## 형식 출력 옵션 (사용자가 명시한 경우)
- "표로" → 마크다운 표
- "Marp 슬라이드로" → `Output/slides/YYYY-MM-DD_<제목>.md` (Marp frontmatter 포함)
- "보고서로" → `Output/reports/YYYY-MM-DD_<제목>.md` 작성 + 본문에 wiki 인용 + log 에 output 항목 기록
- "차트로" → matplotlib 스크립트 + PNG 저장 (Output/reports/ 또는 Output/prototypes/)


## 주의

- **위키에 없는 정보를 환각으로 채우지 않는다.** 빈 곳은 빈 곳으로 표시하고, 신규 ingest·외부검색·lint 권장.
- 위키 본문이 모순되면 (`⚠️ 충돌` 마커가 있으면) 두 입장 모두 답변에 보존.
- graphify CLI 는 한국어 합성어 매칭 약함 (예: "1차년도", "예산은") → 토큰화 후 조사 strip 후 grep 으로 보강.
