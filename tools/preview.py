"""Render source-command layout previews as SVG; not an emulator screenshot."""
from pathlib import Path
from html import escape
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests'))
from basic_harness import Machine
COLORS={10:'#3264b7',11:'#c4483b',12:'#182922',14:'#408756',15:'#c88335',17:'#1c315c',20:'#ffffff',23:'#bcc8bc'}
def number(x):return format(x,'.10g') if isinstance(x,(int,float)) else str(x)
def text(x,y,s,color='#182922',size=6.5):return f'<text xml:space="preserve" x="{x}" y="{y}" fill="{color}" font-size="{size}" font-family="monospace">{escape(s)}</text>'

def home_page(m,title,occurrence=0):
    pages=[page for page in m.pages if any(cmd[0]=='Output' and cmd[1:3]==(1.,1.) and cmd[3]==title for cmd in page)]
    return pages[occurrence]
def home_screen(commands):
    cells=[[' ']*26 for _ in range(10)]
    cursor=0
    for cmd in commands:
        if cmd[0]=='Output':
            _,row,col,value=cmd
            for i,ch in enumerate(number(value)):
                if col+i<=26:cells[int(row)-1][int(col)-1+i]=ch
        elif cmd[0]=='Disp':
            if cursor>=10:
                cells.pop(0);cells.append([' ']*26);cursor=9
            value=number(cmd[1])[:26]
            cells[cursor]=list(value.ljust(26));cursor+=1
    return ''.join(text(3,14+row*16,''.join(chars),size=15.5) for row,chars in enumerate(cells))

def screen(m,graph,commands=None):
    pieces=['<rect width="265" height="165" fill="#fcfdf6"/>']
    if graph:
        v=m.v
        X=lambda x:264*(x-v['Xmin'])/(v['Xmax']-v['Xmin'])
        Y=lambda y:164*(v['Ymax']-y)/(v['Ymax']-v['Ymin'])
        for command in m.graph if commands is None else commands:
            if command[0]=='Line':
                _,x1,y1,x2,y2,c=command
                pieces.append(f'<line x1="{X(x1)}" y1="{Y(y1)}" x2="{X(x2)}" y2="{Y(y2)}" stroke="{COLORS[c]}" stroke-width=".8"/>')
            else:
                _,c,*args=command
                large=args[0]==-1
                y,x,*values=args[1:] if large else args
                pieces.append(text(x,y+(14 if large else 6),''.join(map(number,values)),COLORS[c],size=15.5 if large else 6.5))
    else:
        pieces.append(home_screen(home_page(m,'VECTOR LIST') if commands is None else commands))
    return ''.join(pieces)
def main():
    scenes=[]
    m=Machine(['YES START','QUIT']);m.run('VECTORCE')
    scenes.append(('A new name and startup screen',screen(m,True,m.paused_graphs[1])))
    for mode,label,vectors in [(1,'Fit to the complete addition',[(10,0),(0,4)]),(2,'Compare from a common origin',[(6,2),(-3,4),(1,-3)]),(3,'Inspect one component triangle',[(6,4)])]:
        m=Machine(keys=[45]);m.v.update(N=2,G=mode,L=0)
        m.v['N']=len(vectors)
        for i,(x,y) in enumerate(vectors):m.m[i][:5]=[x,y,(x*x+y*y)**.5,0,2]
        m.run('VQGRAPH')
        scenes.append((label,screen(m,True)))
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="820" viewBox="0 0 1120 820"><rect width="1120" height="820" fill="#f4f5ed"/>',text(32,34,'VECTRA CE / NATIVE CALCULATOR',size=20)]
    for i,(label,body) in enumerate(scenes):
        x=32+(i%2)*550
        y=80+(i//2)*355
        out.extend([text(x,y-12,label,size=14),f'<rect x="{x}" y="{y}" width="506" height="320" rx="14" fill="#25352f"/>',f'<svg x="{x+14}" y="{y+14}" width="478" height="292" viewBox="0 0 265 165">{body}</svg>'])
    out.extend([text(32,799,'Source-layout preview. Fonts approximate; not a photograph or a calculator-emulator capture.',size=12),'</svg>'])
    (ROOT/'docs/calculator-preview.svg').write_text(''.join(out),encoding='utf-8')
    print('Calculator source-layout preview generated')
if __name__=='__main__':main()
