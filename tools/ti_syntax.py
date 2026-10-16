"""Static syntax checks for this project's CE TI-BASIC instruction subset.

Checks actual token boundaries and identifier contexts, not just readable text.
This is not TI's OS parser or a calculator emulator.
"""
try:
    from tools.ce_domains import (validate_color, validate_line, validate_text,
                                  validate_window, validate_window_store)
except ModuleNotFoundError:
    from ce_domains import (validate_color, validate_line, validate_text,
                            validate_window, validate_window_store)


ALPHANUM = set(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') | {0x5b}
FIRST_NAME = set(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ') | {0x5b}
ZERO_ARGS = {'Then','Else','End','Return','Stop','ClrHome','ClrDraw','Degree','Radian',
             'Normal','Float','Real','Full','Func','FnOff','PlotsOff','AxesOff',
             'GridOff','CoordOff','ExprOff','BackgroundOff'}
FUNCTIONS = {'abs(': (1,1), 'max(': (2,2), 'min(': (2,2), 'int(': (1,1),
             'length(': (1,1), 'sub(': (3,3), 'inString(': (2,3),
             'remainder(': (2,2), 'sin(': (1,1), 'cos(': (1,1),
             'tan⁻¹(': (1,1), '√(': (1,1), 'dim(': (1,1)}
COMMAND_ARGS = {'For(': (3,4), 'Menu(': (3,15), 'Output(': (3,3),
                'Text(': (3,99), 'TextColor(': (1,1), 'Line(': (4,6),
                'Fill(': (2,2)}


def lines_of(program):
    current=[]
    for token in program:
        if token.bits==b'\x3f':
            yield current;current=[]
        else:current.append(token)
    if current:yield current


def identifier(tokens,maximum,label):
    data=b''.join(t.bits for t in tokens)
    if not 1<=len(data)<=maximum or any(b not in ALPHANUM for b in data):
        raise ValueError(f'{label}: expected {maximum}-character alphanumeric identifier; '
                         f'got tokens {data.hex()}')
    return data


def outer_arguments(tokens):
    """Split at actual top-level commas, respecting strings/lists/functions."""
    args=[];current=[];stack=[];quoted=False
    for token in tokens:
        value=token.display
        if token.bits==b'\x2a':quoted=not quoted
        if not quoted:
            if value.endswith('('):stack.append(')')
            elif value=='{':stack.append('}')
            elif value in (')','}'):
                if not stack or stack.pop()!=value:raise ValueError('unbalanced delimiters')
            elif value==',' and not stack:
                if not current:raise ValueError('empty argument')
                args.append(current);current=[];continue
        current.append(token)
    if quoted or stack:raise ValueError('unclosed string or delimiter')
    if current:args.append(current)
    elif args:raise ValueError('empty final argument')
    return args


def call_arguments(tokens):
    if not tokens or tokens[-1].bits!=b'\x11':raise ValueError('missing closing parenthesis')
    return outer_arguments(tokens[1:-1])


def scalar(tokens):
    return len(tokens)==1 and len(tokens[0].bits)==1 and tokens[0].bits[0] in FIRST_NAME


SYSTEM_VALUES={'Xmin','Xmax','Ymin','Ymax','Xscl','Yscl','Xres'}
NUMBER_BITS={bytes((n,)) for n in range(0x30,0x3b)}


def literal_number(tokens):
    """Read only actual digit/decimal tokens with optional TI negation.

    Dynamic expressions remain unknown. No source evaluation or substitution
    is used, so an unknown argument cannot hide a different invalid literal.
    """
    bits=[token.bits for token in tokens]
    negative=bool(bits) and bits[0]==b'\xb0'
    if negative:bits=bits[1:]
    if not bits or any(bit not in NUMBER_BITS for bit in bits):
        return None
    spelling=b''.join(bits).decode('ascii').replace(':','.')
    if spelling.count('.')>1 or not any(c.isdigit() for c in spelling):return None
    return -float(spelling) if negative else float(spelling)


def audit_literal_domains(command, arguments):
    """Apply project drawing guards to every statically known argument."""
    values=[literal_number(argument) for argument in arguments]
    if command=='TextColor(':
        if values[0] is not None:validate_color(values[0])
    elif command=='Line(':
        # Valid defaults stand in for unknown arguments; the known arguments
        # are still checked independently. Runtime checks cover expressions.
        defaults=[0,0,0,0,1,1]
        validate_line([default if value is None else value
                       for value,default in zip(values,defaults)])
    elif command=='Text(':
        large=values[0]==-1
        start=1 if large else 0
        row=values[start] if values[start] is not None else 0
        column=values[start+1] if values[start+1] is not None else 0
        contents=[value if value is not None else ''
                  for value in values[start+2:]]
        validate_text(([-1] if large else [])+[row,column]+contents)


def audit_known_window(values):
    if all(name in values for name in ('Xmin','Xmax','Ymin','Ymax')):
        validate_window(values)


class Expression:
    """Parse the expressions used by the project, without evaluating values."""
    OPS={'or':1,'and':2,'=':3,'≠':3,'<':3,'>':3,'≤':3,'≥':3,
         '+':4,'-':4,'*':5,'/':5,'^':6}

    def __init__(self,tokens):self.tokens=tokens;self.pos=0

    def value(self):
        if self.pos>=len(self.tokens):raise ValueError('missing operand')
        token=self.tokens[self.pos];value=token.display.strip();self.pos+=1
        if token.bits==b'\x2a':
            while self.pos<len(self.tokens) and self.tokens[self.pos].bits!=b'\x2a':self.pos+=1
            if self.pos==len(self.tokens):raise ValueError('unclosed string')
            self.pos+=1;return 'str'
        if value=='⁻':
            if self.parse(6)!='num':raise ValueError('negation requires a number')
            return 'num'
        if value=='(':
            kind=self.parse();self.close(')');return kind
        if value=='{':
            while True:
                if self.parse()!='num':raise ValueError('numeric list element required')
                if self.peek()==',':self.pos+=1;continue
                self.close('}');break
            return 'list'
        if value.isascii() and (value.isdigit() or value=='.'):
            literal=value
            while self.pos<len(self.tokens):
                more=self.peek()
                if len(more)!=1 or more not in '0123456789.':break
                literal+=more;self.pos+=1
            if literal.count('.')>1 or not any(c.isdigit() for c in literal):raise ValueError('malformed number')
            return 'num'
        if value in FUNCTIONS:
            arguments=[]
            while True:
                arguments.append(self.parse())
                if self.peek()==',':self.pos+=1;continue
                self.close(')');break
            lo,hi=FUNCTIONS[value]
            if not lo<=len(arguments)<=hi:raise ValueError(f'{value} requires {lo}..{hi} arguments')
            if value in {'length(','sub(','inString('}:
                if arguments[0]!='str':raise ValueError(f'{value} requires a string')
                expected=['str','str'] if value=='inString(' else ['str']
                if value=='sub(':expected+=['num','num']
                if value=='inString(' and len(arguments)==3:expected+=['num']
                if value=='length(':expected=['str']
                if arguments!=expected:raise ValueError(f'{value} argument type mismatch')
                return 'str' if value=='sub(' else 'num'
            if value=='dim(':
                if arguments[0] not in {'list','matrix'}:raise ValueError('dim requires list/matrix')
                return 'list' if arguments[0]=='matrix' else 'num'
            if any(a!='num' for a in arguments):raise ValueError(f'{value} requires numeric arguments')
            return 'num'
        if value.startswith('[') and value.endswith(']'):
            if self.peek()=='(':
                self.pos+=1
                if self.parse()!='num':raise ValueError('numeric matrix row required')
                self.close(',')
                if self.parse()!='num':raise ValueError('numeric matrix column required')
                self.close(')');return 'num'
            return 'matrix'
        if value.startswith('Str') and token.bits.startswith(b'\xaa'):return 'str'
        if scalar([token]) or value in SYSTEM_VALUES or value=='getKey':return 'num'
        raise ValueError(f'unexpected expression token {value!r}')

    def peek(self):
        return self.tokens[self.pos].display.strip() if self.pos<len(self.tokens) else None

    def close(self,expected):
        if self.peek()!=expected:raise ValueError(f'expected {expected!r}, got {self.peek()!r}')
        self.pos+=1

    def parse(self,minimum=0):
        left=self.value()
        while self.pos<len(self.tokens):
            operator=self.peek()
            if operator in {')','}',','}:break
            implicit=operator not in self.OPS
            if implicit:operator='*'
            precedence=self.OPS[operator]
            if precedence<minimum:break
            if not implicit:self.pos+=1
            right=self.parse(precedence+(operator!='^'))
            if operator in {'=','≠','<','>','≤','≥'}:
                if left!=right:raise ValueError('comparison type mismatch')
                left='num'
            elif operator=='+' and left==right=='str':left='str'
            elif left!=right or left!='num':raise ValueError(f'{operator} requires numeric operands')
            else:left='num'
        return left


def audit_expression(tokens):
    if not tokens:raise ValueError('empty expression')
    parser=Expression(tokens);kind=parser.parse()
    if parser.pos!=len(tokens):raise ValueError('unexpected trailing expression tokens')
    return kind


def writable(tokens):
    if scalar(tokens):return 'num'
    if len(tokens)==1 and tokens[0].display in SYSTEM_VALUES:return 'num'
    if len(tokens)==1 and tokens[0].bits.startswith(b'\xaa'):return 'str'
    if tokens and tokens[0].display.startswith('['):
        if audit_expression(tokens)!='num':raise ValueError('indexed matrix target required')
        return 'num'
    if tokens and tokens[0].display=='dim(':
        args=call_arguments(tokens)
        if len(args)!=1 or len(args[0])!=1 or not args[0][0].display.startswith('['):
            raise ValueError('matrix dimension target required')
        return 'list'
    raise ValueError('invalid assignment/input target')

def audit_program(program,name='PROGRAM',available_programs=None):
    labels={};destinations=[];calls=[];blocks=[];previous=None;statement_count=0
    known_window={}
    for number,line in enumerate(lines_of(program),1):
        if not line:continue
        statement_count+=1
        first=line[0].display.strip()
        try:
            # Constants are only propagated through straight-line blocks.
            if first in {'Lbl','Goto','If','Else','End','Repeat','For('}:
                known_window.clear()
            if first in ('Lbl','Goto'):
                destination=identifier(line[1:],2,first)
                if first=='Lbl':
                    if destination in labels:raise ValueError('duplicate label')
                    labels[destination]=number
                else:destinations.append((number,destination))
            elif first=='prgm':
                destination=identifier(line[1:],8,'prgm')
                if destination[0] not in FIRST_NAME:raise ValueError('program name must start with a letter')
                calls.append(destination.decode('ascii'))
            elif first in COMMAND_ARGS:
                arguments=call_arguments(line)
                lo,hi=COMMAND_ARGS[first]
                if not lo<=len(arguments)<=hi:raise ValueError(f'{first} requires {lo}..{hi} arguments')
                if first=='Menu(':
                    if len(arguments)%2!=1:raise ValueError('Menu requires title and option/label pairs')
                    for index,arg in enumerate(arguments):
                        if index and index%2==0:
                            destinations.append((number,identifier(arg,2,'Menu destination')))
                        else:
                            if len(arg)<2 or arg[0].bits!=b'\x2a' or arg[-1].bits!=b'\x2a':
                                raise ValueError('project Menu titles/options must be quoted strings')
                else:
                    kinds=[audit_expression(arg) for arg in arguments]
                    if first in {'For(','Line(','TextColor('} and any(kind!='num' for kind in kinds):
                        raise ValueError('numeric command arguments required')
                    if first in {'Output(','Text('}:
                        large=first=='Text(' and b''.join(t.bits for t in arguments[0])==b'\xb0\x31'
                        coordinates=3 if large else 2
                        if len(kinds)<=coordinates or kinds[:coordinates]!=['num']*coordinates or any(kind not in {'num','str'} for kind in kinds[coordinates:]):
                            raise ValueError('screen coordinates must be numeric, contents numeric/string')
                    if first=='Fill(' and (kinds[0]!='num' or kinds[1] not in {'list','matrix'}):
                        raise ValueError('Fill requires a number and list/matrix')
                    audit_literal_domains(first,arguments)
                    if first=='Line(':audit_known_window(known_window)
                if first=='For(':
                    if not scalar(arguments[0]):raise ValueError('For requires a scalar loop variable')
                    blocks.append(('For',number))
            elif first in ZERO_ARGS:
                if len(line)!=1:raise ValueError(f'{first} takes no arguments here')
                if first=='ClrDraw':audit_known_window(known_window)
                if first=='Then':
                    if previous!='If':raise ValueError('Then must follow If')
                    blocks.append(('Then',number))
                elif first=='Else':
                    if not blocks or blocks[-1][0]!='Then':raise ValueError('Else without Then')
                    blocks[-1]=('Else',blocks[-1][1])
                elif first=='End':
                    if not blocks:raise ValueError('End without a block')
                    blocks.pop()
            elif first in ('If','Repeat'):
                if audit_expression(line[1:])!='num':raise ValueError('numeric condition required')
                if first=='Repeat':blocks.append(('Repeat',number))
            elif first in ('Disp','Input'):
                arguments=outer_arguments(line[1:])
                if not arguments or (first=='Input' and len(arguments)>2):raise ValueError('invalid input/display arguments')
                for arg in arguments:audit_expression(arg)
                if first=='Input':
                    if len(arguments)==2 and audit_expression(arguments[0])!='str':raise ValueError('Input prompt must be a string')
                    writable(arguments[-1])
            elif first=='Pause':
                if len(line)>1:audit_expression(line[1:])
            else:
                # All expression statements in this project store their result.
                quoted=False;stores=[]
                for index,token in enumerate(line):
                    if token.bits==b'\x2a':quoted=not quoted
                    if not quoted and token.bits==b'\x04':stores.append(index)
                if len(stores)!=1:raise ValueError('expected an assignment or recognized command')
                at=stores[0];value_kind=audit_expression(line[:at]);target_kind=writable(line[at+1:])
                if value_kind!=target_kind:raise ValueError('assignment type mismatch')
                if len(line[at+1:])==1 and line[at+1].display in SYSTEM_VALUES:
                    target=line[at+1].display
                    value=literal_number(line[:at])
                    if value is None:known_window.pop(target,None)
                    else:
                        validate_window_store(target,value)
                        known_window[target]=value
            previous=first
        except ValueError as e:
            raise ValueError(f'{name}:{number}: {e}') from e
    if blocks:raise ValueError(f'{name}: unclosed control block {blocks[-1]}')
    for number,destination in destinations:
        if destination not in labels:raise ValueError(f'{name}:{number}: missing label {destination!r}')
    if available_programs is not None:
        for call in calls:
            if call not in available_programs:raise ValueError(f'{name}: missing called program {call}')
    return {'statements':statement_count,
            'labels':len(labels),'destinations':len(destinations),'calls':len(calls)}
