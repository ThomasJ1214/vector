"""Actual-token structural/grammar checks, including the PV label regression."""
import unittest
from tivars import TIProgram
from basic_harness import ROOT
from tools.build import tokenize_source
from tools.ti_syntax import audit_program, lines_of

class NativeSyntax(unittest.TestCase):
    def parse(self,source,available=None):
        return audit_program(tokenize_source(source,'TEST'),'TEST',available)

    def test_finance_variable_cannot_be_a_label(self):
        for source in ['Lbl PV','Goto PV','Menu("M","PREVIOUS",PV)\nLbl P1']:
            with self.subTest(source=source):
                with self.assertRaisesRegex(ValueError,'identifier'):self.parse(source)

    def test_real_label_uses_character_bytes(self):
        p=tokenize_source('Lbl P1\nGoto P1')
        self.assertEqual([b''.join(t.bits for t in line) for line in lines_of(p)],
                         [b'\xd6P1',b'\xd7P1'])
        self.parse('Menu("M","PREVIOUS",P1)\nLbl P1\nStop')

    def test_finance_token_not_mistaken_for_scalar_product(self):
        with self.assertRaisesRegex(ValueError,'expression token'):self.parse('PV→A')
        self.parse('P*V→A')

    def test_finance_text_in_menu_is_allowed(self):
        self.parse('Menu("PV","PV",P1)\nLbl P1')

    def test_command_argument_counts(self):
        for source in ['Line(0,0,1)','Output(1,1)','Fill(0)','TextColor(1,2)',
                       'Menu("T","X")','For(A,1)\nEnd']:
            with self.subTest(source=source):
                with self.assertRaises(ValueError):self.parse(source)

    def test_large_text_requires_row_column_and_contents(self):
        self.parse('Text(⁻1,80,87,"VECTRA CE")')
        for source in ['Text(⁻1,80,"BAD","X")','Text(⁻1,80,87)']:
            with self.subTest(source=source):
                with self.assertRaises(ValueError):self.parse(source)

    def test_incomplete_and_malformed_expressions(self):
        for source in ['1+→A','If 1=','sin(1+)→A','(1+2→A','1..2→A','-1→A']:
            with self.subTest(source=source):
                with self.assertRaises(ValueError):self.parse(source)

    def test_function_arity_and_types(self):
        for source in ['abs(1,2)→A','sub("A",1)→Str1','inString("A")→A','length(3)→A','sin("X")→A']:
            with self.subTest(source=source):
                with self.assertRaises(ValueError):self.parse(source)

    def test_only_valid_writable_targets(self):
        for source in ['1→1','1→A+B','1→sin(A)','Input 3','For(3,1,2)\nEnd']:
            with self.subTest(source=source):
                with self.assertRaises(ValueError):self.parse(source)

    def test_matrix_index_count(self):
        for source in ['[J](1)→A','[J](1,2,3)→A','1→[J](1)']:
            with self.subTest(source=source):
                with self.assertRaises(ValueError):self.parse(source)
        self.parse('[J](1,2)→A\nA→[J](2,3)')

    def test_control_blocks(self):
        for source in ['Else','End','Then','If 1\nThen','Repeat 1','For(A,1,2)']:
            with self.subTest(source=source):
                with self.assertRaises(ValueError):self.parse(source)
        self.parse('If 1\nThen\nFor(A,1,2)\n1→B\nEnd\nElse\nRepeat B=1\n1→B\nEnd\nEnd')

    def test_duplicate_and_missing_destinations(self):
        for source in ['Lbl A\nLbl A','Goto A','Menu("T","GO",A)']:
            with self.subTest(source=source):
                with self.assertRaises(ValueError):self.parse(source)

    def test_missing_called_program(self):
        with self.assertRaisesRegex(ValueError,'missing called program'):
            self.parse('prgmMISSING',set())
        self.parse('prgmVQNUM',{'VQNUM'})

    def test_conditions_and_commands_have_valid_types(self):
        for source in ['If "X"','Repeat "X"\nEnd','Line("A",0,1,1)','Output("A",1,1)','Fill(0,1)']:
            with self.subTest(source=source):
                with self.assertRaises(ValueError):self.parse(source)

    def test_string_input_and_dimension_assignment(self):
        self.parse('Input Str1\nsub(Str1,1,1)→Str2\n{20,7}→dim([J])\nFill(0,[J])')

    def test_audit_counts_every_statement(self):
        result=self.parse('Menu("T","GO",A)\nLbl A')
        self.assertEqual(result['statements'],2)
        self.assertEqual(result['labels'],1)
        self.assertEqual(result['destinations'],1)

    def test_all_saved_programs_and_calls(self):
        names={p.stem for p in (ROOT/'src').glob('*.txt')}
        count=0
        for path in (ROOT/'dist').glob('*.8xp'):
            p=TIProgram.open(str(path));report=audit_program(p,path.stem,names)
            source=(ROOT/'src'/f'{path.stem}.txt').read_text(encoding='utf-8')
            self.assertEqual(report['statements'],len([s for s in source.splitlines() if s]))
            count+=report['statements']
        self.assertEqual(count,863)

if __name__=='__main__':unittest.main()
