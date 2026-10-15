"""Optional Chromium functional checks. Requires playwright and a Chromium binary.
Run with: python tools/browser_check.py (not a TI emulator test).
"""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/'
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1080},device_scale_factor=1)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(base+'index.html')
    assert page.locator('#count').inner_text()=='1 / 20'
    assert abs(float(page.locator('#rx').inner_text())-12)<1e-8
    assert page.locator('#resultAngle').inner_text()=='60°'
    page.screenshot(path=str(ROOT/'docs/browser-preview.png'),full_page=True)
    page.locator('#example345').click()
    assert page.locator('#resultMagnitude').inner_text()=='5'
    for view in ['origin','triangle','step']:
        page.locator(f'[data-view="{view}"]').click()
        assert page.locator('#plot path, #plot line').count()>0
    assert page.locator('#stepLabel').inner_text()=='0 / 2 vectors'
    page.locator('#next').click();assert page.locator('#rx').inner_text()=='3'
    page.locator('#next').click();assert page.locator('#ry').inner_text()=='4'
    assert page.locator('#next').is_disabled()
    page.locator('#previous').click();assert page.locator('#ry').inner_text()=='0'
    page.locator('#exampleCancel').click()
    assert page.locator('#resultMagnitude').inner_text()=='0'
    assert page.locator('#resultAngle').inner_text()=='Undefined'
    page.locator('[aria-label="Inspect vector 1"]').click()
    assert page.locator('#inspect').input_value()=='0'
    page.locator('[aria-label="Edit vector 1"]').click()
    page.locator('#magnitude').fill('-1');page.locator('#saveVector').click()
    assert 'nonnegative' in page.locator('#error').inner_text()
    page.locator('#cancelEdit').click();assert page.locator('#count').inner_text()=='2 / 20'
    page.locator('[aria-label="Edit vector 1"]').click()
    page.locator('[data-type="xy"]').click()
    page.locator('#xInput').fill('-3');page.locator('#yInput').fill('4');page.locator('#saveVector').click()
    assert page.locator('#rx').inner_text()=='-3' # selected vector, not total
    assert page.locator('#xLabel').text_content()=='Vector x'
    page.locator('[aria-label="Delete vector 1"]').click();assert page.locator('#count').inner_text()=='1 / 20'
    page.locator('#exampleCompass').click()
    page.locator('#magnitude').fill('0');page.locator('#angle').fill('90');page.locator('#saveVector').click()
    page.locator('[aria-label="Inspect vector 2"]').click()
    assert page.locator('#resultAngle').inner_text()=='Undefined'
    # Invalid numeric input never changes the list.
    page.locator('#magnitude').fill('2+3');page.locator('#saveVector').click()
    assert page.locator('#error').inner_text();assert page.locator('#count').inner_text()=='2 / 20'
    page.on('dialog',lambda d:d.accept())
    page.locator('#clearAll').click();assert page.locator('#count').inner_text()=='0 / 20'
    page.locator('#magnitude').fill('1');page.locator('#angle').fill('0');page.locator('#direction').select_option('standard')
    for _ in range(20):page.locator('#saveVector').click()
    assert page.locator('#count').inner_text()=='20 / 20'
    page.locator('#saveVector').click();assert 'full' in page.locator('#error').inner_text()
    # Small decimal input remains editable without changing it into forbidden EE notation.
    page.locator('#clearAll').click()
    page.locator('[data-type="xy"]').click()
    page.locator('#xInput').fill('0.000000001');page.locator('#yInput').fill('-0.000000001');page.locator('#saveVector').click()
    page.locator('[aria-label="Edit vector 1"]').click()
    assert page.locator('#xInput').input_value()=='0.000000001'
    page.locator('#saveVector').click();assert not page.locator('#error').inner_text()
    # All compass choices and mobile layout.
    page.locator('[data-type="polar"]').click()
    page.locator('#clearAll').click()
    for direction in ['EN','WN','ES','WS','NE','SE','NW','SW']:
        page.locator('#magnitude').fill('24');page.locator('#angle').fill('30');page.locator('#direction').select_option(direction);page.locator('#saveVector').click()
    assert page.locator('#count').inner_text()=='8 / 20'
    page.set_viewport_size({'width':390,'height':844});page.locator('#exampleCompass').click()
    assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
    assert page.locator('.logo').bounding_box()['height']<80
    assert page.locator('#plot').get_attribute('viewBox')=='0 0 390 390'
    page.screenshot(path=str(ROOT/'docs/browser-mobile.png'),full_page=True)
    page.set_viewport_size({'width':1440,'height':1080})
    page.goto(base+'dist/try-vector.html')
    assert page.locator('#count').inner_text()=='1 / 20'
    assert page.locator('#resultAngle').inner_text()=='60°'
    # Previews may allow scripts while blocking native form submission.
    # Exercise the actual single-file artifact inside that restricted frame.
    page.set_content('<iframe sandbox="allow-scripts" src="'+base+'dist/try-vector.html" style="width:1100px;height:1000px"></iframe>')
    frame=page.frame_locator('iframe')
    assert frame.locator('#count').inner_text()=='1 / 20'
    frame.locator('#magnitude').fill('5');frame.locator('#angle').fill('0')
    frame.locator('#direction').select_option('standard')
    frame.locator('#saveVector').click()
    assert frame.locator('#count').inner_text()=='2 / 20'
    assert frame.locator('#rx').inner_text()=='17'
    frame.locator('#angle').press('Enter')
    assert frame.locator('#count').inner_text()=='3 / 20'
    assert frame.locator('#rx').inner_text()=='22'
    frame.locator('[data-type="xy"]').click()
    frame.locator('#xInput').fill('-2');frame.locator('#yInput').fill('3')
    frame.locator('#saveVector').click()
    assert frame.locator('#count').inner_text()=='4 / 20'
    frame.locator('[aria-label="Edit vector 4"]').click()
    frame.locator('#xInput').fill('-4');frame.locator('#saveVector').click()
    assert frame.locator('#count').inner_text()=='4 / 20'
    assert '-4' in frame.locator('#vectors').inner_text()
    frame.locator('#xInput').fill('2+3');frame.locator('#saveVector').click()
    assert frame.locator('#error').inner_text()
    assert frame.locator('#count').inner_text()=='4 / 20'
    page.goto(base+'docs/calculator-preview.svg')
    page.locator('svg').first.screenshot(path=str(ROOT/'docs/calculator-preview.png'))
    assert not errors,errors
    browser.close()
server.shutdown()
server.server_close()
print('Chromium: examples, views, steps, edit/cancel/delete, zero, invalid input, capacity, all compass choices, mobile layout, and restricted-preview click/Enter add/edit validation passed')
