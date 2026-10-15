"""Build a silent calculator-screen storyboard video from TI-BASIC source commands.
Requires Playwright, Chromium and ffmpeg. NOT a calculator emulator recording.
"""
from pathlib import Path
import json
import sys
import subprocess
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from zipfile import ZipFile, ZIP_DEFLATED
from html import escape
from playwright.sync_api import sync_playwright
from preview import screen, text
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests'))
from basic_harness import Machine
OUT=ROOT/'docs/walkthrough'
SCENES=[]

def scene(title,caption,key,m,graph=False,commands=None,duration=3):
    SCENES.append(dict(title=title,caption=caption,key=key,duration=duration,body=screen(m,graph,commands)))

def menu(title_fragment,selected,title,caption):
    for line in (ROOT/'src/VECTORCE.txt').read_text(encoding='utf-8').splitlines():
        if line.startswith('Menu('):
            args=Machine.split(line[5:-1]); heading=args[0].strip('"')
            if heading==title_fragment:
                labels=[args[i].strip('"') for i in range(1,len(args),2)]
                assert selected in labels
                cmds=[('Output',1,1,heading),('Output',2,1,'-'*26)]
                for i,label in enumerate(labels):cmds.append(('Output',i+3,1,f'{">" if label==selected else " "}{i+1}:{label}'))
                scene(title,caption,selected,Machine(),commands=cmds,duration=2.5)
                return
    raise AssertionError(title_fragment)

def enter(label,value,caption):
    m=Machine(inputs=[value]);m.home=[('Disp',label)];m.run('VQNUM')
    assert m.v['F']==1
    scene('Enter '+label.lower(),caption,'Type '+value+' / ENTER',m,commands=[*m.home,('Disp','? '+value)],duration=2.5)

def main_machine(menus,inputs=(),keys=()):
    m=Machine(menus,map(str,inputs),keys);m.run('VECTORCE')
    assert not m.menus and not m.inputs and not m.keys
    return m

def vector_machine(vectors):
    m=Machine();m.v['N']=len(vectors)
    for i,(x,y) in enumerate(vectors):
        m.v.update(A=x,B=y);m.run('VQMATH');m.m[i][:5]=[x,y,m.v['R'],m.v['T'],2]
    m.run('VQSUM');return m

def graph(vectors,mode,selected,title,caption,keys=(45,)):
    m=vector_machine(vectors);m.v.update(G=mode,L=selected);m.keys.extend(keys);m.run('VQGRAPH')
    if mode==4:
        for i,frame in enumerate(m.frames):scene(f'{title} / {i}',caption[i],['RIGHT','RIGHT','CLEAR'][i],m,True,frame)
    else:scene(title,caption,'CLEAR: back',m,True,duration=4)

def build_scenes():
    m=main_machine(['CANCEL'])
    scene('Welcome to Vector CE','Native TI-BASIC workflow for TI-84 Plus CE and CE Python.','PRGM / VECTORCE / ENTER',m,commands=m.pages[0],duration=4)
    menu('USE/ERASE [J]?','YES START','Choose the session workspace','Back up matrix [J] and the documented variables before starting.')
    menu('VECTOR CE','ADD VECTOR','Start with an empty vector list','Vectors are loaded only when you enter them. There are no default vectors.')
    menu('INPUT TYPE','MAG / ANGLE','Vector 1 / polar input','First enter 3 units pointing along the positive x-axis.')
    enter('MAGNITUDE >= 0','3','The magnitude uses your chosen consistent units.')
    menu('DIRECTION STYLE','STANDARD CCW +X','Choose a direction convention','Standard angles are measured counterclockwise from +x.')
    enter('ANGLE IN DEGREES','0','Zero degrees points east or to the right.')
    m=main_machine(['YES START','ADD VECTOR','MAG / ANGLE','STANDARD CCW +X','VECTORS','MAIN MENU','QUIT'],[3,0])
    scene('Review vector 1','The calculator stores x=3, y=0 and magnitude 3.','ENTER: vector options',m,commands=m.pages[1])
    menu('INPUT TYPE','X / Y','Vector 2 / component input','Mix input types: add an upward vector using its components.')
    enter('HORIZONTAL X','0','The second vector has no horizontal component.')
    enter('VERTICAL Y','4','Its positive vertical component points north or up.')
    m=main_machine(['YES START','ADD VECTOR','X / Y','ADD VECTOR','X / Y','VECTORS','NEXT','MAIN MENU','QUIT'],[3,0,0,4])
    scene('Review vector 2','The second vector is 4 units at 90 degrees.','ENTER: vector options',m,commands=m.pages[2])
    menu('GRAPHS','HEAD TO TAIL','Choose a graph view','Head-to-tail shows the actual order of addition.')
    graph([(3,0),(0,4)],1,0,'Head to tail / 3 plus 4','Blue arrows add in sequence. Red joins the origin to the final endpoint.')
    graph([(3,0),(0,4)],2,0,'Compare at a common origin','The same two vectors are drawn from one starting point.')
    graph([(3,0),(0,4)],4,0,'Step through addition',['Start at zero. No vectors have been added yet.','Add vector 1: the running resultant is (3,0).','Add vector 2: the running resultant is (3,4).'],keys=[26,26,45])
    m=vector_machine([(3,0),(0,4)]);m.v['L']=0;m.keys.extend([105]*11);m.menus.extend(['FULL WORK','BACK']);m.run('VQWORK')
    titles=['Total components','Vector 1 components','Add the first x component','Add the first y component','Vector 2 components','Add the next x component','Add the next y component','Resultant magnitude','Handle the correct quadrant','Substitute the components','Resultant direction']
    captions=['Rx=3 and Ry=4. The stored values retain native precision.','Vector 1 contributes x=3, y=0.','The running x sum becomes 3.','The running y sum remains 0.','Vector 2 contributes x=0, y=4.','Add zero: the x total is still 3.','Add four: the y total becomes 4.','sqrt(3 squared + 4 squared) = 5 units.','Axis cases and negative x values have explicit handling.','Use atan(4/3), then apply the appropriate quadrant correction.','53.13010235 degrees CCW; equivalently north of east.']
    assert len(m.pages)==len(titles)
    assert m.v['R']==5
    for title,caption,commands in zip(titles,captions,m.pages):scene(title,caption,'ENTER: next / CLEAR: back',m,commands=commands)
    graph([(3,0),(0,4)],3,0,'Inspect the resultant triangle','Green x=3 and orange y=4 form a right triangle with hypotenuse R=5.')
    menu('DIRECTION STYLE','COMPASS WORDS','Use a compass description','Example: 24 units at 30 degrees east of north.')
    menu('MEASURE FROM','NORTH','Start from north','The first reference direction is north, not east.')
    menu('ANGLE OF NORTH','EAST OF NORTH','Turn toward east','30 degrees east of north converts to 60 degrees CCW from +x.')
    m=main_machine(['YES START','ADD VECTOR','MAG / ANGLE','COMPASS WORDS','NORTH','EAST OF NORTH','VECTORS','MAIN MENU','QUIT'],[24,30])
    assert abs(m.m[0][0]-12)<1e-10
    scene('Review a compass vector','x=12; y is approximately 20.78460969; magnitude=24.','ENTER: options',m,commands=m.pages[1],duration=4)
    graph([(-3,4)],3,1,'Negative components / quadrant II','A negative x component points west. The direction is 126.86989765 degrees.')
    m=vector_machine([(3,0),(-3,0)]);m.v['L']=0;m.keys.extend([105]*9);m.menus.extend(['FULL WORK','BACK']);m.run('VQWORK')
    assert m.v['R']==0
    scene('Opposite vectors cancel','The resultant is zero. Its direction is undefined, not zero degrees.','ENTER: next / CLEAR: back',m,commands=m.pages[-1],duration=4)
    graph([(3,0),(-3,0)],1,0,'Cancellation / head to tail','The final endpoint returns to the origin.')
    menu('VECTOR OPTIONS','EDIT','Edit without restarting','An edit replaces the selected vector only after all values are valid.')
    menu('DELETE VECTOR?','YES','Delete with confirmation','Delete shifts the remaining vectors while keeping their order.')
    m=main_machine(['YES START','HELP','QUIT'])
    scene('Controls are always available','Return to the main menu to review conventions and input limits.','ENTER / main menu',m,commands=m.pages[1])

def svg_for(item,index,total):
    return ''.join(['<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">','<rect width="1280" height="720" fill="#f4f5ed"/>',text(46,40,'VECTOR CE / CALCULATOR WALKTHROUGH',size=19),text(1115,40,f'{index:02d} / {total:02d}',size=19),'<rect x="192" y="70" width="896" height="548" rx="20" fill="#25352f"/>',f'<svg x="216" y="80" width="848" height="528" viewBox="0 0 265 165">{item["body"]}</svg>',text(46,650,item['title'],size=23),text(46,678,item['caption'],size=17),text(46,707,'SOURCE-LAYOUT SIMULATION / APPROXIMATE FONTS / NOT HARDWARE OR EMULATOR FOOTAGE',size=13),text(1110,97,'KEY / ACTION',size=11),text(1110,119,item['key'][:20],size=11),'</svg>'])

class Handler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def main():
    build_scenes();frames=OUT/'frames';frames.mkdir(parents=True,exist_ok=True)
    # Keep reruns from retaining stale frames from an older storyboard.
    for p in frames.glob('frame-*'):
        if p.suffix in ('.svg','.png'):p.unlink()
    manifest=[];timestamp=0
    for i,item in enumerate(SCENES,1):
        stem=f'frame-{i:03d}'
        (frames/(stem+'.svg')).write_text(svg_for(item,i,len(SCENES)),encoding='utf-8')
        manifest.append(dict(frame=i,png='frames/'+stem+'.png',start_seconds=timestamp,**{k:v for k,v in item.items() if k!='body'}));timestamp+=item['duration']
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}/docs/walkthrough/'
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':1280,'height':720})
            for i in range(1,len(SCENES)+1):
                page.goto(base+f'frames/frame-{i:03d}.svg')
                page.locator('svg').first.screenshot(path=str(frames/f'frame-{i:03d}.png'))
            # Contact sheet: the full sequence at a glance.
            html='<!doctype html><html><head><meta charset="utf-8"><title>Vector CE storyboard</title></head><body style="margin:0;padding:20px;background:#f4f5ed;font-family:monospace"><h2>VECTOR CE / SOURCE-LAYOUT WALKTHROUGH</h2><p>Simulated screens, not TI firmware execution. Read the README before using this as a reference.</p><main style="display:grid;grid-template-columns:repeat(5,240px);gap:14px">'
            for item in manifest:html+=f'<div><img style="width:240px" src="{item["png"]}"><div>{item["frame"]:02d}. {escape(item["title"])}</div></div>'
            html+='</main></body></html>'
            (OUT/'contact-sheet.html').write_text(html,encoding='utf-8')
            page.set_viewport_size({'width':1300,'height':900});page.goto(base+'contact-sheet.html');page.locator('img').last.wait_for()
            page.evaluate('Promise.all([...document.images].map(i=>i.decode()))')
            page.screenshot(path=str(OUT/'contact-sheet.png'),full_page=True)
            browser.close()
    finally:server.shutdown();server.server_close()
    (OUT/'storyboard.json').write_text(json.dumps(dict(kind='source-layout simulation, NOT emulator or hardware footage',width=1280,height=720,duration_seconds=timestamp,frames=manifest),indent=2)+'\n',encoding='utf-8')
    (OUT/'sequence.txt').write_text(''.join(f"file 'frames/frame-{i:03d}.png'\nduration {item['duration']}\n" for i,item in enumerate(SCENES,1))+f"file 'frames/frame-{len(SCENES):03d}.png'\n",encoding='utf-8')
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(OUT/'sequence.txt'),'-vf','fps=24,format=yuv420p','-c:v','libx264','-preset','medium','-crf','20','-movflags','+faststart','-t',str(timestamp),str(OUT/'vector-ce-walkthrough.mp4')],check=True)
    with ZipFile(OUT/'walkthrough-images.zip','w',compression=ZIP_DEFLATED) as z:
        for p in sorted(frames.glob('*')):z.write(p,p.relative_to(OUT))
        z.write(OUT/'storyboard.json','storyboard.json')
    print(f'{len(SCENES)} source-derived frames; {timestamp:g} seconds; MP4 and image ZIP generated')

if __name__=='__main__':main()
