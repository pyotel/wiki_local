---
name: lint
description: LLM Wiki 도서관 정리 — wiki/ 전체에서 깨진 위키링크·고아 페이지·미생성 cross-link·stale 주장·frontmatter 누락·index 누락·인제스트 누락 등을 찾아 보고하고, 사용자 승인 하에 수정한다. 사용자가 "/lint" 또는 "위키 점검·정리해줘"라고 말하거나, 큰 ingest 후 정기 점검 시 사용.
---

# /lint — LLM Wiki 도서관 정리

> Karpathy LLM Wiki의 lint 단계. 위키가 커질수록 cross-reference·일관성이 무너지므로 정기적으로 healthcheck하고 수선한다.

## 절대 원칙
- **분석은 전수**, **수정은 명시적 승인 후**. 발견을 먼저 보고하고, 무엇을 어떻게 고칠지 사용자 승인을 받은 뒤 적용.
- 단, 명백한 frontmatter 누락(필수 필드 자동 추가)·index.md 누락 등 **무손실 수정**은 보고와 동시에 적용해도 OK.
- raw/는 절대 손대지 않는다 (단, ingest_status 기준 검사는 OK).

## 점검 항목 (전수)

### A. 위키링크 무결성
1. `grep -rn "\[\[" wiki/` 로 모든 위키링크 추출
2. 각 링크 타깃 파일 존재 여부 확인
3. **broken link**: 타깃 없음 → 보고 (생성 권장 또는 오타 의심)
4. **case/공백 불일치**: 파일명과 미세 차이 → 보고

### B. 고아(Orphan) 페이지
1. `find wiki -name "*.md"` 로 모든 wiki 페이지 수집
2. 각 페이지에 대해 `grep -rln "[[<basename>]]" wiki/` 로 inbound link 카운트
3. inbound link == 0 인 페이지 = orphan → 보고 (link 추가 또는 archive 검토)
4. 예외: `index.md`, `log.md`, `_ingested.md`, `CLAUDE.md`

### C. 미생성 Cross-link (Lint 후보)
1. `wiki/index.md`의 "Lint 후보" 섹션 + 본문 위키링크 중 타깃 없는 것 = 미생성 페이지 후보
2. 후보별로: 본문에서 등장하는 횟수 (`grep -c`) → 빈도 높은 순 정렬
3. ≥ 2회 등장하는 후보는 페이지 신규 생성 권장 (사용자 승인 후 진행)

### D. Frontmatter 무결성
각 wiki/ 페이지에 대해:
- `type` 필드 존재? (`source`, `entity`, `concept`, `topic`, `synthesis`, `meta` 중 하나)
- `created`, `updated` 날짜 존재?
- `source` 페이지: `sources` (raw 경로) 존재?
- `synthesis` 페이지: `status` (draft/reviewed) 존재?
- 누락 시 자동 보강 (값 추정 가능한 경우만)

### E. Stale 주장 / 모순
1. `grep -rn "⚠️ 충돌" wiki/` — 명시된 충돌이 해결됐는지 검토
2. 같은 entity·concept을 다루는 여러 페이지 간 사실 차이 검색 (예: "ST-GNN 정확도" 같은 수치)
3. 새 source ingest로 stale 된 주장: source 페이지의 `ingested` 날짜와 entity/concept의 `updated` 비교

### F. 인제스트 추적 무결성
1. **Pending 잔존**:
   ```bash
   grep -rln "ingest_status: pending" raw/ --exclude=CLAUDE.md
   find raw -type f \( -name "*.pdf" -o -name "*.pptx" -o -name "*.hwp" -o -name "*.hwpx" -o -name "*.docx" \) \
     -not -name "*.ingest.md" \
     | while read f; do [ -f "$f.ingest.md" ] || echo "PENDING: $f"; done
   ```
2. **레지스트리 정합성**: `wiki/_ingested.md`에 등록된 모든 wiki/sources/ 파일이 실제 존재? raw 경로가 실제 존재?
3. **goofy 짝꿍 누락**: wiki/sources 페이지의 `sources` frontmatter가 가리키는 raw 파일이 실제 존재?

### G. index.md 누락
1. `find wiki -name "*.md"` 로 모든 페이지 vs `wiki/index.md` 등재 페이지 비교
2. 미등재 페이지를 카테고리별로 자동 추가 (단, meta 파일은 제외)

### H. 데이터 갭 (선택 — 사용자에게 제안)
- 주요 entity 페이지가 source 1개에만 의존 → 추가 정보원 검색 권장
- topic 페이지에 syntheses가 없음 → 종합 작성 권장
- syntheses 페이지에 `status: draft` 인 채로 30일 경과 → 검토 요청

## 출력 형식 (보고서)

```
# Lint Report — YYYY-MM-DD

## A. 위키링크 무결성
- broken: N개  → [목록]
- 미세 차이: N개

## B. 고아 페이지: N개

## C. 미생성 cross-link (≥2회 등장): N개

## D. Frontmatter 누락: N개  (자동 보강 가능 N개 / 수동 검토 N개)

## E. Stale·모순: N개

## F. 인제스트 누락: pending md N / pending binary N / 레지스트리 mismatch N

## G. index 누락: N개  (자동 추가 가능)

## H. 데이터 갭 제안: N개

---
## 자동 적용 가능 (승인 요청)
- [ ] index.md에 미등재 N개 페이지 추가
- [ ] frontmatter 누락 자동 보강 N개

## 수동 결정 필요 (사용자 검토)
- broken link <X>: 오타? 신규 생성?
- orphan <Y>: archive? 또는 link 보강?
...
```

## 적용 후 처리

수정 적용 후:
1. `wiki/log.md`에 항목 추가:
   ```
   ## [YYYY-MM-DD] lint   | <범위>
   - 점검: A~H 전체
   - 자동 수정: index 등재 N, frontmatter 보강 N
   - 수동 결정 적용: <목록>
   - 다음 lint 권장 시점: <날짜 또는 조건>
   ```
2. `wiki/index.md`의 통계·"마지막 lint" 갱신

## 주의

- **수정 폭이 큰 항목(고아 archive, 모순 해결)은 반드시 사용자 승인 후 진행**.
- 한국어 페이지 검색 시 영문 변형도 동시 매칭 (예: "온디바이스 AI" ↔ "on-device AI" ↔ "OnDeviceAI").
- 페이지 길이가 비정상적으로 길어진 페이지(>500줄)는 분리 권장 (cross-link 유지).
