"""Regress actual CE program tokens; source math is insufficient to test encoding."""
from pathlib import Path
import unittest
from tivars import TIProgram
from basic_harness import Machine, ROOT
from tools.build import BARE_COMMANDS, TARGET_OS, tokenize_source, validate_tokens, token_lines, supports_target_os

class CalculatorTokens(unittest.TestCase):
    def test_optional_argument_commands_are_real_opcodes(self):
        for spelling,opcode in BARE_COMMANDS.items():
            with self.subTest(command=spelling):
                program=tokenize_source(spelling,'TEST')
                self.assertEqual(bytes(program.data),opcode+b'\x3f')

    def test_old_letter_encodings_fail_even_when_round_trip_passes(self):
        for bad in ['Pause','FnOff','PlotsOff','floor(D/360)']:
            with self.subTest(source=bad):
                program=TIProgram();program.load_string(bad)
                other=TIProgram();other.load_string(program.string())
                self.assertEqual(bytes(program.data),bytes(other.data))
                with self.assertRaisesRegex(ValueError,'executable character'):
                    validate_tokens(program)

    def test_unsupported_floor_cannot_enter_the_build(self):
        with self.assertRaisesRegex(ValueError,'executable character'):
            tokenize_source('D-360floor(D/360)→D','TEST')

    def test_string_characters_are_not_executable(self):
        tokenize_source('Disp "Pause floor FnOff PlotsOff"','TEST')

    def test_ti_int_and_ipart_have_their_actual_meanings(self):
        m=Machine()
        self.assertEqual(m.expr('int(⁻.5)'),-1)
        self.assertEqual(m.expr('iPart(⁻.5)'),0)
        with self.assertRaises(KeyError):m.expr('floor(1.5)')

    def test_normalization_uses_int_opcode(self):
        p=tokenize_source('D-360int(D/360)→D','TEST')
        self.assertIn(b'\xb1',bytes(p.data))
        self.assertEqual(bytes(p.data).count(b'\xb1'),1)

    def test_os_version_comparison_is_numeric(self):
        from tivars.models import TI_84PCE
        self.assertTrue(supports_target_os(TI_84PCE.OS('5.8.0')))
        self.assertFalse(supports_target_os(TI_84PCE.OS('5.8.1')))
        self.assertFalse(supports_target_os(TI_84PCE.OS('5.10')))

    def test_saved_files_pass_ce_58_token_audit(self):
        for path in (ROOT/'dist').glob('*.8xp'):
            with self.subTest(program=path.stem):
                p=TIProgram.open(str(path));validate_tokens(p,path.stem)
                self.assertLessEqual(p.get_min_os(),TARGET_OS)

    def test_real_command_tokens_at_each_affected_source_line(self):
        for name in ['VECTORCE','VQGRAPH']:
            source=(ROOT/'src'/f'{name}.txt').read_text(encoding='utf-8').strip().splitlines()
            saved=TIProgram.open(str(ROOT/'dist'/f'{name}.8xp'))
            encoded=token_lines(saved)
            self.assertEqual(len(source),len(encoded))
            count=0
            for line,data in zip(source,encoded):
                if line in BARE_COMMANDS:
                    self.assertEqual(data,BARE_COMMANDS[line]);count+=1
            self.assertEqual(count,6 if name=='VECTORCE' else 2)

if __name__=='__main__':unittest.main()
