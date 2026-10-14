# 개발용 E2E 체크: OPFS 를 볼트 대신 물려 portal.html 전 기능 검증.  python dev/test_portal.py . out.png  (playwright 필요)
import sys, threading, functools, http.server, socketserver, json
from playwright.sync_api import sync_playwright
root = sys.argv[1]
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=root)
srv = socketserver.TCPServer(('127.0.0.1', 0), H); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
PNG = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
SEED = """async ([png]) => {
  const root = await navigator.storage.getDirectory();
  ROOT = root;
  const files = {
    'wiki/concepts/RAG.md': '---\\ntype: concept\\ntags: [llm, 검색]\\nupdated: 2026-10-13\\n---\\n# RAG\\n[[LLM]] 과 [[없는페이지]] 그리고 14:00~15:30\\n\\n![[diag.png]]\\n\\n[상대](../entities/LLM.md)',
    'wiki/entities/LLM.md': '# LLM\\nRAG 의 생성기',
    'wiki/log.md': '# Log\\n\\n## [2026-10-13] init | 생성\\n- a\\n\\n## [2026-10-14] ingest | 테스트\\n- b',
    'raw/a.pdf': 'x', 'raw/b.pdf': 'y', 'raw/b.pdf.ingest.md': '---\\ningest_status: done\\n---', 'raw/memo.md': '그냥 메모',
  };
  for (const [p, t] of Object.entries(files)) await writeFile(p, t);
  await writeFile('wiki/assets/diag.png', Uint8Array.from(atob(png), c => c.charCodeAt(0)));
  await connect(root);
}"""
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    pg.on('console', lambda m: m.type == 'error' and errs.append(m.text)); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f'http://127.0.0.1:{port}/portal.html')
    pg.evaluate(SEED, [PNG]); pg.wait_for_timeout(500)
    stats = pg.inner_text('#stats'); print('STATS', stats.replace('\n', ' '))
    assert '인제스트 대기' in stats
    pend = pg.inner_text('#pendingList'); print('PENDING', pend.replace('\n', ' | '))
    assert 'raw/a.pdf' in pend and 'raw/memo.md' in pend and 'b.pdf' not in pend
    assert '테스트' in pg.inner_text('#logBody')
    pg.evaluate("go('#wiki=' + encodeURIComponent('wiki/concepts/RAG.md'))"); pg.wait_for_timeout(500)
    body = pg.inner_html('#viewBody')
    assert 'class="wikilink" data-path="wiki/entities/LLM.md"' in body, body
    assert 'wikilink missing' in body and '<del>' not in body and 'badge">concept' in body
    assert pg.eval_on_selector('#viewBody img', 'i => i.src.startsWith("blob:") && i.complete && i.naturalWidth === 1')
    assert pg.is_visible('[data-file="wiki/concepts/RAG.md"].selected')
    pg.click('#viewBody a[data-path="wiki/entities/LLM.md"].wikilink'); pg.wait_for_timeout(300)
    assert pg.inner_text('#viewTitle') == 'wiki/entities/LLM.md'
    pg.go_back(); pg.wait_for_timeout(300); assert pg.inner_text('#viewTitle').endswith('RAG.md')
    pg.click('#viewBody a:has-text("상대")'); pg.wait_for_timeout(300); assert pg.inner_text('#viewTitle') == 'wiki/entities/LLM.md'
    pg.fill('#wikiSearch', '생성기'); pg.wait_for_timeout(700)
    assert 'LLM' in pg.inner_text('#wikiTree') and '1건' in pg.inner_text('#wikiTree')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300); assert '📂' in pg.inner_text('#wikiTree')
    # raw: upload + memo
    pg.evaluate("go('#raw')"); pg.wait_for_timeout(400)
    assert '대기' in pg.inner_text('#rawList') and '반영됨' in pg.inner_text('#rawList') and 'ingest.md' not in pg.inner_text('#rawList')
    pg.set_input_files('#upFiles', files=[{'name': '보고서.txt', 'mimeType': 'text/plain', 'buffer': '내용'.encode()}])
    pg.fill('#upDesc', '1차 보고서'); pg.click('#upBtn'); pg.wait_for_timeout(500)
    meta = json.loads(pg.evaluate("readText('portal_data/raw_meta.json')")); print('META', meta)
    assert meta['raw/보고서.txt']['description'] == '1차 보고서' and '1차 보고서' in pg.inner_text('#rawList')
    pg.click('#memoBtn'); pg.fill('#memoTitle', '아이디어'); pg.fill('#memoBody', '본문'); pg.click('#memoSave'); pg.wait_for_timeout(500)
    memo = [l for l in pg.inner_text('#rawList').split('\n') if '아이디어' in l]; assert memo, pg.inner_text('#rawList')
    pg.click('tr[data-p$="보고서.txt"]'); pg.wait_for_timeout(300); assert '내용' in pg.inner_text('#rawView')
    # issues
    pg.evaluate("go('#issues')"); pg.wait_for_timeout(300)
    pg.fill('#isTitle', '첫 이슈'); pg.fill('#isBody', '**굵게**'); pg.fill('#isDue', '2020-01-01'); pg.click('#isAdd'); pg.wait_for_timeout(400)
    t = pg.inner_text('#issueList'); assert '첫 이슈' in t and '초과' in t and pg.inner_html('#issueList').count('<strong>굵게</strong>') == 1
    pg.select_option('#issueList select', 'done'); pg.wait_for_timeout(400); assert '이슈 없음' in pg.inner_text('#issueList')
    # schedule: 빈 칸 클릭 → 등록 → 칩 클릭 → 수정 → 삭제, 이슈 기한 표시, 월 이동, .ics
    pg.evaluate("writeJSON(ISSUES, [{id: 7, title: '기한이슈', due: addDays(today(), 2), status: 'open', created: 1}])")
    pg.evaluate("go('#schedule')"); pg.wait_for_timeout(400)
    d = pg.evaluate("addDays(today(), 3)")
    assert '🐛 기한이슈' in pg.inner_text('#cal')
    pg.click(f'#cal [data-day="{d}"]'); assert pg.input_value('#seDate') == d
    pg.fill('#seTitle', '공고 마감'); pg.fill('#seTime', '18:00'); pg.fill('#sePlace', '온라인'); pg.click('#seSave'); pg.wait_for_timeout(500)
    sched = json.loads(pg.evaluate("readText('portal_data/schedule.json')")); print('SCHED', sched)
    assert sched[0]['title'] == '공고 마감' and sched[0]['by'] == 'user' and '18:00 공고 마감' in pg.inner_text(f'#cal [data-day="{d}"]')
    assert 'D-3' in pg.inner_text('#schedUpcoming')
    pg.click('#cal [data-ev="1"]'); assert pg.input_value('#seTitle') == '공고 마감' and pg.is_visible('#seDel')
    pg.fill('#seTitle', '공고 마감(수정)'); pg.click('#seSave'); pg.wait_for_timeout(500)
    assert '공고 마감(수정)' in pg.inner_text('#cal') and len(json.loads(pg.evaluate("readText('portal_data/schedule.json')"))) == 1
    ym = pg.evaluate("calMonth"); pg.click('[data-cal="1"]'); pg.wait_for_timeout(300)
    assert pg.evaluate("calMonth") != ym and '#schedule=' in pg.url
    pg.click('[data-cal="0"]'); pg.wait_for_timeout(300)
    with pg.expect_download() as dl: pg.click('#icsBtn')
    ics = open(dl.value.path(), encoding='utf-8').read(); assert 'SUMMARY:공고 마감(수정)' in ics and 'LOCATION:온라인' in ics, ics
    pg.on('dialog', lambda dg: dg.accept())
    pg.click('#cal [data-ev="1"]'); pg.click('#seDel'); pg.wait_for_timeout(500)
    assert pg.evaluate("readText('portal_data/schedule.json')").strip() == '[]'
    pg.evaluate("go('#home')"); pg.wait_for_timeout(500)
    print('STATS2', pg.inner_text('#stats').replace('\n', ' '))
    pg.screenshot(path=sys.argv[2], full_page=True)
    b.close()
print('ERRORS', errs); assert not errs
print('ALL OK')
