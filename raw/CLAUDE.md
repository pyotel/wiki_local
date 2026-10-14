---
scope: raw/
purpose: 원본 소스 보관소 — AI는 읽기 전용
---

# raw/ — 불변 원본

## 절대 규칙
- **AI는 이 폴더 안의 파일을 절대 수정/삭제/이동하지 않는다.**
- 원본은 사용자가 직접 추가/제거한다.
- AI는 읽고, 인용하고, `wiki/sources/`에 요약 페이지를 만들 뿐이다.
- ⚠️ `raw/reports/`(우리 팀 작성물)와 `Output/reports/`(AI 생성물)는 **다른 계층**이다. 절대 섞지 말 것.

## 하위 폴더 (인풋 채널별)

> 폴더는 미리 만들지 않는다 — 포탈 Raw 탭의 "+ 폴더" 로 필요할 때 만든다. 아래는 권장 채널명.

| 폴더 | 무엇을 담나 | 일반적 형식 | 클리퍼 템플릿 |
|---|---|---|---|
| `youtube/` | 유튜브 영상 메모·자막·요약 | `.md` | `youtube.json` |
| `podcasts/` | 팟캐스트 에피소드 메모·트랜스크립트 | `.md` | `podcast.json` |
| `books/` | 도서 메타·독서 메모 | `.md` | `book.json` |
| `papers/` | 학술 논문 (국제·국내) PDF·요약 | `.pdf`, `.md` | `research.json` (영문), `paper_kor.json` (국내) |
| `patents/` | 국내·국제 특허 (KIPRIS, Google Patents 등) | `.md`, `.pdf` | `patent.json` |
| `rfp/` | 과제 RFP / 사업 공고 / 과제 개요서 | `.md`, `.pdf`, `.hwp` | `rfp.json` |
| `gov_docs/` | 정부 공문·공지·고시 | `.md`, `.pdf`, `.hwp` | `gov_doc.json` |
| `reports/` | **우리 팀이 직접 작성한** 보고서 (사업계획서, 중간/최종 보고서, 결과보고서, 백서 등) | `.md`, `.hwpx`, `.hwp`, `.pdf`, `.docx` | `report.json` |
| `geeknews/` | [geeknews](https://news.hada.io) 등 트렌드 기사 클립 | `.md` | (article.json 후 수동 이동) |
| `meetings/` | 회의록·녹취 요약 | `.md` | _(직접 업로드)_ |
| `web_clips/` | 일반 웹 검색 결과·블로그·기술 문서 | `.md` | `article.json` |
| `conversations/` | 동료·전문가와의 대화 메모 | `.md` | _(직접 업로드)_ |
| `ideas/` | 자유 형식의 본인 메모·번뜩임 | `.md` | _(직접 업로드)_ |
| `assets/` | 이미지·첨부파일 (Obsidian 첨부 폴더) | `.png`, `.jpg`, ... | _(자동)_ |

## 파일명 규약
- 날짜 prefix 권장: `YYYY-MM-DD_제목.md` (예: `2026-05-03_수소누출_논문리뷰.md`)
- 한국어 파일명 허용

## Ingest 트리거
사용자가 "이 파일 ingest" / "이거 정리해줘" / "위키에 반영"이라고 말하면 `/ingest` 스킬(`.claude/skills/ingest/`)을 따른다.

## 인제스트 상태 관리 프로토콜

### 1. Markdown 원본 (frontmatter 보유)
인제스트 완료 시 AI가 frontmatter를 다음과 같이 갱신:
```yaml
ingest_status: done            # pending → done
ingested_at: YYYY-MM-DD        # 신규 추가
wiki_source: wiki/sources/<요약페이지>.md   # 신규 추가
```

### 2. Binary 원본 (PDF/PPTX/HWP/HWPX/DOCX 등, frontmatter 불가)
같은 폴더에 **사이드카 파일** `<원본파일명>.ingest.md` 생성:
```yaml
---
type: ingest-sidecar
binary_source: ./<원본파일명>
ingest_status: done
ingested_at: YYYY-MM-DD
wiki_source: wiki/sources/<요약페이지>.md
---
```
원본 바이너리 자체는 손대지 않는다.

### 3. 레지스트리
모든 인제스트는 [[../wiki/_ingested]] 에 한 줄 추가된다 (append-only). 다중 안전장치.

---

## 미인제스트 검색

판정 규칙과 탐지 스크립트는 `.claude/skills/ingest/SKILL.md` 1단계가 단일 진실 (포탈 홈의 "인제스트 대기" 와 동일):
- md: `ingest_status: done` 이 없으면 대기 (frontmatter 없는 md 포함 — 완료 시 frontmatter 를 맨 위에 추가)
- 그 외 모든 파일 (txt·csv·xlsx 포함): `<파일명>.ingest.md` 사이드카가 없으면 대기
