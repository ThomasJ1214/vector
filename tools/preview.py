"""Render source-command layout previews as SVG; not an emulator screenshot."""
from pathlib import Path
from html import escape
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests'))
from basic_harness import Machine
COLORS={10:'#3264b7',11:'#c4483b',12:'#182922',14:'#408756',15:'#c88335',23:'#bcc8bc'}
def number(x):return format(x,'.10g') if isinstance(x,(int,float)) else str(x)
def text(x,y,s,color='#182922',size=5):return f'<text xml:space="preserve" x="{x}" y="{y}" fill="{color}" font-size="{size}" font-family="monospace">{escape(s)}</text>'
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
                _,c,y,x,*values=command
                pieces.append(text(x,y+5,''.join(map(number,values)),COLORS[c]))
    else:
        pieces.append(home_screen(m.pages[1] if commands is None else commands))
    return ''.join(pieces)
def main():
    scenes=[]
    m=Machine(['YES START','ADD VECTOR','MAG / ANGLE','COMPASS WORDS','NORTH','EAST OF NORTH','LIST / EDIT','MAIN MENU','QUIT'],['24','30']);m.run('VECTORCE')
    scenes.append(('Review your vector',screen(m,False)))
    for mode,label in [(1,'Head to tail'),(3,'Inspect a component triangle')]:
        m=Machine(keys=[45]);m.v.update(N=2,G=mode,L=0)
        m.m[0][:5]=[3,0,3,0,2];m.m[1][:5]=[0,4,4,90,2];m.run('VQGRAPH')
        scenes.append((label,screen(m,True)))
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="355" viewBox="0 0 1100 355"><rect width="1100" height="355" fill="#f4f5ed"/>',text(32,33,'VECTOR CE / CALCULATOR LAYOUT',size=18)]
    for i,(label,body) in enumerate(scenes):
        x=32+i*358
        out.extend([text(x,68,label,size=13),f'<rect x="{x}" y="85" width="320" height="216" rx="14" fill="#25352f"/>',f'<svg x="{x+14}" y="99" width="292" height="188" viewBox="0 0 265 165">{body}</svg>'])
    out.extend([text(32,333,'Source-layout preview. Fonts approximate; not a photograph or a calculator-emulator capture.',size=12),'</svg>'])
    (ROOT/'docs/calculator-preview.svg').write_text(''.join(out),encoding='utf-8')
    print('Calculator source-layout preview generated')
if __name__=='__main__':main()
