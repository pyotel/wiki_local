---
name: ingest
description: LLM Wiki 인제스트 자동화 — raw/의 미인제스트 소스를 모두 찾아 wiki/ 페이지로 컴파일하고 상태를 갱신한다. 사용자가 새 raw 파일을 떨군 뒤 "/ingest" 또는 "ingest 해줘" 라고 말하면 사용. 인자로 특정 경로(`/ingest raw/youtube/foo.md`)를 주면 그 파일만 처리한다.
---

# /ingest — LLM Wiki 인제스트 워크플로우

> Karpathy LLM Wiki 패턴의 핵심 동작. 본 볼트의 [`CLAUDE.md`](../../../CLAUDE.md)와 [`raw/CLAUDE.md`](../../../raw/CLAUDE.md)에 정의된 규약을 그대로 따른다.

## 절대 원칙
- **`raw/`는 불변**. 원본 파일을 절대 수정·이동·삭제하지 않는다 (단, markdown raw의 frontmatter `ingest_status` 필드 갱신은 허용).
- **wiki/는 AI 전권**. 새 페이지를 능동적으로 만들고 cross-link을 적극 발굴한다.
- 작업 종료 직전에 **반드시** 상태 갱신 + 레지스트리 + 로그 3종을 모두 마쳐야 인제스트 완료로 간주.

## 단계

### 0. 동기화 (git 저장소일 때만)

로컬 단독 운영이 기본. 볼트가 git 저장소이고 원격(origin)이 있을 때만 먼저 `git pull --rebase --no-edit` 로 흡수한다. git 이 없거나 원격이 없으면 이 단계는 건너뛴다.

### 1. 미인제스트 소스 탐지
포탈.html 의 "인제스트 대기" 판정과 같은 규칙 (Windows·Linux 공통, python 표준 라이브러리만):
```bash
python -c "
import os, unicodedata
N = lambda s: unicodedata.normalize('NFC', s)
for root, _, files in os.walk('raw'):
    names = {N(f) for f in files}
    for f in files:
        if f == 'CLAUDE.md' or f.endswith('.ingest.md') or f.startswith('.'): continue
        p = os.path.join(root, f)
        if f.endswith('.md'):
            if 'ingest_status: done' not in open(p, encoding='utf-8', errors='ignore').read(): print('PENDING:', p)
        elif N(f) + '.ingest.md' not in names:
            print('PENDING:', p)
"
```
- md: frontmatter 에 `ingest_status: done` 이 없으면 대기 (frontmatter 없는 md 도 대기)
- 그 외 모든 파일: 같은 폴더에 `<파일명>.ingest.md` 사이드카가 없으면 대기
- **`portal_data/raw_meta.json`** 에 업로드 시 사용자가 적은 설명이 `{"raw/경로": {"description": ...}}` 로 있다 — 파일 맥락의 1차 힌트로 반드시 참고

사용자가 인자로 특정 경로를 줬다면 해당 파일만 처리. 인자 없으면 위 명령으로 발견된 모든 파일을 대상으로.

대상이 0건이면 "인제스트 대기 0건"이라 답하고 종료.

### 2. 사용자에게 처리 계획 1줄 요약
대상이 N개면 한 줄로 알리고 진행. 너무 많으면(>10) 사용자에게 일괄 처리 OK인지 짧게 확인.

### 3. 각 소스별 처리

#### 3-1. 원본 통독
- markdown은 Read 도구로 직접 읽기
- PDF는 `pdftotext -layout <file> -` (없으면 `python -c "import pypdf; ..."`) 로 텍스트 추출
- PPTX는 `python -c "from pptx import Presentation; ..."` 로 슬라이드 텍스트 덤프
- HWP/HWPX는 사용 가능 시 `hwp5txt` 또는 ZIP 추출, 불가 시 사용자에게 변환 요청 후 보류

#### 3-2. wiki/sources/ 요약 페이지 생성
파일명 규약: `YYYY-MM-DD_<유형>_<짧은-제목>.md` (한국어 가능). frontmatter 필수:
```yaml
---
type: source
source_type: source-article | source-youtube | source-podcast | source-book | source-research | source-paper-kor | source-patent | source-rfp | source-govdoc | source-report
title: <원문 제목>
sources: [raw/<경로>]
authored_by: "[[<작성자>]]"
authored_at: YYYY-MM-DD
ingested: YYYY-MM-DD
tags: [...]
---
```
본문 구조:
1. 한 단락 핵심 요지
2. 원문에서 추출한 표·인용·핵심 데이터
3. **재활용 가능 자산** (보고서·제안서·논문 작성 시 끌어쓸 표현·도식·수치)
4. **관련 페이지** — `[[ ]]` 위키링크 다수

#### 3-3. 영향받는 wiki/entities/, wiki/concepts/, wiki/topics/ 갱신·생성
- 본문에 처음 등장하는 **인물·기관·제품·도구**는 `entities/` 신규 페이지
- 본문에 처음 등장하는 **방법론·알고리즘·이론·아키텍처**는 `concepts/` 신규 페이지
- 본문이 새로운 **도메인 화두**를 형성하면 `topics/` 신규 페이지
- 기존 페이지에는 본 source를 참조 추가 + cross-link 보강
- 사실 충돌 시: `> ⚠️ 충돌: [[페이지A]]는 X라 하고 [[페이지B]]는 Y라 함` 마커로 **두 주장 모두 보존**

#### 3-4. wiki/syntheses/ 종합 (선택)
새 source가 기존 자료와 묶여 의미 있는 종합을 만든다면 `syntheses/`에 신규 또는 갱신.
[[조인표]]의 3대 평가 기준(상용화/실증/신규성) + 사회문제 임팩트로 평가.

#### 3-5. 일정 추출 (해당 시)
원본에 **날짜가 확정된 일정**(공고 접수 마감, 발표·평가일, 회의·행사 등)이 있으면 `portal_data/schedule.json` 에 추가 —
`by: "ai"`, `source: raw/<경로>`, 스키마는 루트 [`CLAUDE.md`](../../../CLAUDE.md) 「일정」 절. 같은 제목·날짜가 이미 있으면 건너뛴다. 추가한 건수는 9단계 보고에 포함.

### 4. wiki/index.md 갱신
신규 페이지를 카테고리별 가나다/알파벳 순으로 추가. 통계(총 페이지 수, 마지막 ingest 일자) 업데이트. Lint 후보(미생성 cross-link)도 누적.

### 5. 인제스트 완료 표시 (필수)

#### markdown raw
frontmatter 갱신 (frontmatter 가 없으면 맨 위에 새로 추가 — raw 본문은 건드리지 않음):
```yaml
ingest_status: "done"          # pending → done
ingested_at: YYYY-MM-DD
wiki_source: wiki/sources/<요약페이지명>.md
```

#### binary raw
같은 폴더에 사이드카 `<원본파일명>.ingest.md` 생성:
```yaml
---
type: ingest-sidecar
binary_source: ./<원본파일명>
ingest_status: done
ingested_at: YYYY-MM-DD
wiki_source: wiki/sources/<요약페이지명>.md
extraction_method: <pdftotext|python-pptx|...>
notes: <한 줄 요약>
---

# 사이드카 — <원본 짧은 제목>
원본 바이너리(<형식>)에 대한 인제스트 추적 메타.
- **요약 페이지**: [[../../wiki/sources/<요약페이지명>]]

⚠️ 본 사이드카는 삭제하지 말 것.
```

### 6. wiki/_ingested.md 레지스트리에 한 행 추가
오늘 날짜 섹션에 `| <원본 경로> | [[<요약페이지>]] |` 행 append. 섹션이 없으면 새로 추가.

### 7. wiki/log.md에 항목 추가
형식:
```
## [YYYY-MM-DD] ingest | <짧은 제목 또는 "N개 일괄">
- 대상: <원본 경로 N개>
- 신규 페이지: sources/N, entities/N, concepts/N, topics/N, syntheses/N
- raw 상태 갱신: md N개 / binary 사이드카 N개
- Lint 후보: [[ ]] 누적
```

### 8. 그래프 자동 재빌드 (필수)

ingest 가 wiki/ 페이지를 변경했으므로 그래프도 동기화해야 함. **/graphify 스킬을 그대로 호출해 wiki/ 를 다시 빌드한다.**

- 이 단계는 **기본값**. 사용자가 "graphify 빼고", "그래프 갱신 X" 등 명시적으로 거부하지 않는 한 항상 실행.
- 호출 방식: 본 ingest 작업 끝에 `/graphify` 스킬을 그대로 invoke (인자 없으면 wiki/ 가 기본 타깃 — 루트 [`CLAUDE.md`](../../../CLAUDE.md) 참조).
- 캐시 덕분에 변경된 페이지만 재추출되므로 비용 최소.
- 빌드 결과는 `graphify-out/graph.html` — 포탈.html 의 🕸 그래프 버튼이 바로 연다.
- graphify 가 설치돼 있지 않으면 (`pip install graphifyy`) 이 단계는 건너뛰고 보고에 명시.
- 빌드 실패 시 ingest 자체는 성공으로 보고하되 graphify 실패는 명시.

### 9. 사용자에게 짧은 결과 보고
- 처리한 소스 N개
- 신규 wiki 페이지 N개 (카테고리별 분리)
- 그래프 갱신 결과 (총 노드/엣지 수, 새 god nodes 1-2개)
- Lint 시 채워야 할 cross-link 후보 수
- 일정에 추가한 항목 (있으면 날짜·제목)

## 주의

- **단일 소스가 10~15개 페이지를 건드릴 수 있다**. 누락된 cross-link을 적극 발굴.
- 페이지 길이가 너무 길어지면 하위 개념을 분리해 신규 페이지로 (cross-link 유지).
- 대량 인제스트 시 [[에이전트 최소 개입 원칙]]에 따라, 반복 작업은 한 번에 묶어 처리하고 LLM 호출 수를 최소화.
- 본인 인사이트가 더해질 만하면 **재활용 가능 자산** 섹션을 적극적으로 채울 것 (향후 [[Output]]/proposals·reports 작성 시 자기 인용 자원).
