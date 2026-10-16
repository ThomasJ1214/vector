"""Small source-level TI-BASIC test harness, NOT a calculator emulator.

Runs this project's control flow and expressions with Python binary64 numbers.
Drawing/display commands are recorded, not rendered; OS/token semantics are not
validated by this harness. Binary generation is checked separately.
"""
import math
import re
from collections import deque
from pathlib import Path
try:
    from tools.ce_domains import (WINDOW_VALUES, validate_color, validate_line,
                                  validate_text, validate_window,
                                  validate_window_store)
except ModuleNotFoundError:
    from ce_domains import (WINDOW_VALUES, validate_color, validate_line,
                            validate_text, validate_window,
                            validate_window_store)

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r'"[^"]*"|Xmin|Xmax|Ymin|Ymax|Xscl|Yscl|Xres|iPart|inString|Str[12]|\[J\]|tan⁻¹|[a-z]+|\d*\.\d+|\d+|[A-Zθ]|[^\s]')

class Machine:
    def __init__(self, menus=(), inputs=(), keys=(), initial_angle="Degree"):
        self.v = {chr(i): 0.0 for i in range(65, 91)}
        self.v.update({'θ': 0., 'Str1': '', 'Str2': ''})
        self.m = [[0.] * 7 for _ in range(20)]
        self.menus, self.inputs, self.keys = map(deque, (menus, inputs, keys))
        self.output = []
        self.steps = 0
        self.stopped = False
        self.angle = initial_angle
        self.graph = []
        self.frames = []
        self.home = []
        self.pages = []
        self.paused_graphs = []
        self.text_color = 12
        self.v.update(dict.fromkeys(("Xmin","Xmax","Ymin","Ymax","Xscl","Yscl","Xres"),0.))

    def matrix_read(self, i, j):
        assert i==int(i) and j==int(j)
        assert 1<=i<=len(self.m) and 1<=j<=len(self.m[0]), (i,j)
        return self.m[int(i)-1][int(j)-1]

    def expr(self, source):
        tokens = TOKEN.findall(source.strip())
        pos = 0
        funcs = {'abs': abs, 'max': max, 'min': min,
                 'int': math.floor, 'iPart': math.trunc, 'length': len,
                 'sin': lambda x: math.sin(math.radians(x) if self.angle=="Degree" else x),
                 'cos': lambda x: math.cos(math.radians(x) if self.angle=="Degree" else x),
                 'tan⁻¹': lambda x: math.degrees(math.atan(x)) if self.angle=="Degree" else math.atan(x),
                 '√': math.sqrt, 'remainder': lambda x,y: x % y,
                 'sub': lambda s,i,n: s[int(i)-1:int(i)-1+int(n)],
                 'inString': lambda s,t: s.find(t)+1,
                 '[J]': self.matrix_read}
        prec = {'or':1, 'and':2, '=':3, '≠':3, '<':3, '>':3, '≤':3,
                '≥':3, '+':4, '-':4, '*':5, '/':5, '^':6}
        ops = {'or':lambda a,b:bool(a or b), 'and':lambda a,b:bool(a and b),
               '=':lambda a,b:a==b, '≠':lambda a,b:a!=b, '<':lambda a,b:a<b,
               '>':lambda a,b:a>b, '≤':lambda a,b:a<=b, '≥':lambda a,b:a>=b,
               '+':lambda a,b:a+b, '-':lambda a,b:a-b, '*':lambda a,b:a*b,
               '/':lambda a,b:a/b, '^':lambda a,b:a**b}
        def parse(level=0):
            nonlocal pos
            t=tokens[pos]; pos+=1
            if t in ('⁻','-','+'):
                a=parse(6); a=-a if t!='+' else a
            elif t=='(':
                a=parse(); assert tokens[pos]==')'; pos+=1
            elif t.startswith('"'):
                a=t[1:-1]
            elif re.fullmatch(r'\d*\.?\d+',t):
                a=float(t)
            elif t in funcs:
                assert tokens[pos]=='('; pos+=1
                args=[parse()]
                while tokens[pos]==',':
                    pos+=1; args.append(parse())
                assert tokens[pos]==')'; pos+=1
                a=funcs[t](*args)
            else:
                a=self.v[t]
            while pos<len(tokens):
                op=tokens[pos]
                implicit=op not in prec and op not in (')',',','}')
                if implicit: op='*'
                if op not in prec or prec[op]<level: break
                if not implicit: pos+=1
                b=parse(prec[op]+(op!='^'))
                a=ops[op](a,b)
            return a
        ans=parse()
        assert pos==len(tokens), (source,tokens[pos:])
        return ans

    @staticmethod
    def split(text):
        # Split command arguments outside strings and nested parentheses.
        parts=[]; start=0; depth=0; quoted=False
        for i,c in enumerate(text):
            if c=='"': quoted=not quoted
            if not quoted:
                if c in '({': depth+=1
                if c in ')}': depth-=1
                if c==',' and depth==0:
                    parts.append(text[start:i]); start=i+1
        return parts+[text[start:]]

    def run(self,name):
        lines=[s.strip() for s in (ROOT/'src'/f'{name}.txt').read_text(encoding="utf-8").splitlines() if s.strip()]
        labels={s[4:]:i for i,s in enumerate(lines) if s.startswith('Lbl ')}
        assert len(labels)==sum(s.startswith('Lbl ') for s in lines), name+' duplicate labels'
        ends={}; stack=[]
        for i,s in enumerate(lines):
            if s=='Then' or s.startswith(('For(','Repeat ')): stack.append(i)
            elif s=='Else': ends[stack[-1]]=i; stack[-1]=i
            elif s=='End': ends[stack.pop()]=i
        assert not stack
        loops={}; pc=0
        while pc<len(lines) and not self.stopped:
            self.steps+=1
            assert self.steps<200000, 'source loop did not terminate'
            s=lines[pc]; nxt=pc+1
            if s.startswith('If '):
                good=self.expr(s[3:])
                if lines[nxt]=='Then':
                    if not good: nxt=ends[nxt]+1
                elif not good: nxt+=1
            elif s=='Else': nxt=ends[pc]+1
            elif s.startswith('For('):
                args=self.split(s[4:-1]); var=args[0]
                start,end=map(self.expr,args[1:3]); step=self.expr(args[3]) if len(args)>3 else 1
                self.v[var]=start
                if (start>end if step>0 else start<end): nxt=ends[pc]+1
                else: loops[ends[pc]]=(pc,var,end,step)
            elif s.startswith('Repeat '):
                loops[ends[pc]]=(pc,s[7:])
            elif s=='End' and pc in loops:
                loop=loops[pc]
                if len(loop)==2:
                    if not self.expr(loop[1]): nxt=loop[0]+1
                else:
                    begin,var,end,step=loop; self.v[var]+=step
                    if self.v[var]<=end if step>0 else self.v[var]>=end: nxt=begin+1
            elif s.startswith('Goto '): nxt=labels[s[5:]]
            elif s=='Return': return
            elif s=='Stop': self.stopped=True
            elif s.startswith('prgm'): self.run(s[4:])
            elif s.startswith('Menu('):
                args=self.split(s[5:-1]); choice=self.menus.popleft()
                options={args[i].strip('"'):args[i+1] for i in range(1,len(args),2)}
                assert choice in options,(choice,options)
                nxt=labels[options[choice]]
            elif s.startswith('Input '): self.v[s[6:]]=self.inputs.popleft()
            elif '→' in s:
                source,target=s.split('→')
                if target=='dim([J])':
                    n,m=map(int,source.strip('{}').split(',')); self.m=[[0.]*m for _ in range(n)]
                elif target.startswith('[J]('):
                    i,j=map(self.expr,self.split(target[4:-1])); self.matrix_read(i,j); self.m[int(i)-1][int(j)-1]=self.expr(source)
                elif target in self.v:
                    if source=='getKey':
                        self.frames.append(list(self.graph))
                        self.pages.append(list(self.home))
                        self.v[target]=self.keys.popleft()
                    else:
                        value=self.expr(source)
                        if target in WINDOW_VALUES:
                            validate_window_store(target,value)
                        self.v[target]=value
                else: raise AssertionError('Unknown store: '+s)
            elif s.startswith('Fill('):
                for row in self.m: row[:]=[0.]*len(row)
            elif s in ('Degree','Radian'): self.angle=s
            elif s=='ClrHome': self.home=[]
            elif s=='ClrDraw':
                validate_window(self.v)
                self.graph=[]
            elif s=='Pause':
                self.pages.append(list(self.home))
                self.paused_graphs.append(list(self.graph))
            elif s.startswith('Disp '):
                self.output.append(s)
                for value in self.split(s[5:]): self.home.append(('Disp',self.expr(value)))
            elif s.startswith('Output('):
                self.output.append(s)
                row,col,value=map(self.expr,self.split(s[7:-1]))
                assert row==int(row) and col==int(col) and 1<=row<=10 and 1<=col<=26, s
                self.home.append(('Output',row,col,value))
            elif s.startswith('TextColor('):
                color=self.expr(s[10:-1])
                validate_color(color)
                self.text_color=color
            elif s.startswith('Text('):
                args=list(map(self.expr,self.split(s[5:-1])))
                validate_window(self.v)
                validate_text(args)
                self.graph.append(('Text',self.text_color,*args))
                self.output.append(s)
            elif s.startswith('Line('):
                args=list(map(self.expr,self.split(s[5:-1])))
                validate_window(self.v)
                validate_line(args)
                assert len(args)==5
                assert all(math.isfinite(x) for x in args)
                self.graph.append(('Line',*args))
                self.output.append(s)
            elif s.startswith('Lbl ') or s in ('Then','End','Normal','Float','Real','Full','Func','FnOff','PlotsOff','AxesOff','GridOff','CoordOff','ExprOff','BackgroundOff'):
                pass
            else: raise AssertionError('Unsupported command: '+s)
            pc=nxt
