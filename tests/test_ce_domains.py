"""Conservative native drawing checks, not calculator or OS emulation."""
import math
import unittest

from tools.build import tokenize_source
from tools.ce_domains import (
    CalculatorDomainError, LARGE_TEXT_ROW_MAX, SMALL_TEXT_ROW_MAX,
    validate_color, validate_line, validate_text, validate_window,
    validate_window_store,
)
from tools.ti_syntax import audit_program


class DrawingDomains(unittest.TestCase):
    def window(self, **updates):
        values = dict(Xmin=-10, Xmax=10, Ymin=-5, Ymax=5,
                      Xscl=1, Yscl=1, Xres=1)
        values.update(updates)
        return values

    def test_text_uses_project_safe_font_margins(self):
        self.assertEqual(SMALL_TEXT_ROW_MAX, 150)
        self.assertEqual(LARGE_TEXT_ROW_MAX, 140)
        validate_text([150, 264, 'SAFE'])
        validate_text([-1, 140, 264, 'SAFE'])
        for args in ([156, 6, 'R3 FOOTER'], [151, 0, 'LOW'],
                     [-1, 141, 0, 'LOW'], [-1, 156, 0, 'LOW']):
            with self.subTest(args=args):
                with self.assertRaisesRegex(CalculatorDomainError, 'safe margin'):
                    validate_text(args)

    def test_text_coordinates_require_finite_nonnegative_integers(self):
        for args in ([-2, 0, 'X'], [1.5, 0, 'X'], [0, -1, 'X'],
                     [0, 265, 'X'], [0, 1.5, 'X'], [math.nan, 0, 'X'],
                     [0, math.inf, 'X'], [10**1000, 0, 'X'],
                     ['ROW', 0, 'X'], [0, 0]):
            with self.subTest(args=args):
                with self.assertRaises(CalculatorDomainError):
                    validate_text(args)
        validate_text([0, 0, 'X=', 1.25, '  Y=', -3])
        with self.assertRaises(CalculatorDomainError):
            validate_text([0, 0, math.inf])

    def test_color_indices_are_ce_palette_integers(self):
        for color in range(10, 25):
            validate_color(color)
        for color in (0, 1, 9, 25, 12.5, math.inf, math.nan, 'BLUE'):
            with self.subTest(color=color):
                with self.assertRaises(CalculatorDomainError):
                    validate_color(color)

    def test_line_supports_draw_erase_colors_and_styles(self):
        validate_line([0, 0, 1, 1])
        for option in (0, 1, *range(10, 25)):
            validate_line([0, 0, 1, 1, option])
            for style in range(1, 5):
                validate_line([0, 0, 1, 1, option, style])
        for args in ([0, 0, 1], [0, 0, 1, 1, 10, 1, 0],
                     [0, 0, 1, 1, 2], [0, 0, 1, 1, 10.5],
                     [0, 0, 1, 1, 10, 0], [0, 0, 1, 1, 10, 5],
                     [0, 0, 1, 1, 10, 1.5], [0, 0, math.inf, 1],
                     [0, 0, 1, complex(1, 2)]):
            with self.subTest(args=args):
                with self.assertRaises(CalculatorDomainError):
                    validate_line(args)

    def test_window_requires_ordered_finite_bounds_when_drawing(self):
        validate_window(self.window())
        validate_window(self.window(Xscl=0, Yscl=0, Xres=8))
        for changes in (dict(Xmin=10), dict(Xmin=11), dict(Ymax=-5),
                        dict(Ymax=-6), dict(Xmax=math.inf),
                        dict(Ymin=math.nan), dict(Xscl=-1), dict(Yscl=-1),
                        dict(Xres=0), dict(Xres=9), dict(Xres=1.5)):
            with self.subTest(changes=changes):
                with self.assertRaises(CalculatorDomainError):
                    validate_window(self.window(**changes))
        with self.assertRaises(CalculatorDomainError):
            validate_window({'Xmin': 0})

    def test_window_stores_allow_intermediate_reversed_bounds(self):
        validate_window_store('Xmin', 100)
        validate_window_store('Xmax', -100)
        for name, value in (('Xmin', math.inf), ('Yscl', -1),
                            ('Xres', 0), ('Xres', 9), ('Xres', 1.5)):
            with self.subTest(name=name, value=value):
                with self.assertRaises(CalculatorDomainError):
                    validate_window_store(name, value)


class ActualTokenDrawingDomains(unittest.TestCase):
    def audit(self, source):
        return audit_program(tokenize_source(source, 'DOMAIN'), 'DOMAIN')

    def test_r3_footer_regression_rejected_in_actual_tokens(self):
        for source in ('Text(156,6,"R3 FOOTER")',
                       'Text(156,A,"DYNAMIC COLUMN")',
                       'Text(⁻1,141,A,"LARGE FOOTER")'):
            with self.subTest(source=source):
                with self.assertRaisesRegex(ValueError, 'DOMAIN:1:.*safe margin'):
                    self.audit(source)

    def test_safe_text_and_unknown_expressions_remain_supported(self):
        self.audit('Text(150,6,"FOOTER")\nText(⁻1,140,8,"LARGE")')
        self.audit('Text(A,B,"DYNAMIC")\nText(max(0,min(130,A)),6,"DYNAMIC")')

    def test_literal_coordinate_validation_is_independent(self):
        for source in ('Text(A,265,"BAD COLUMN")',
                       'Text(1.5,A,"BAD ROW")',
                       'Text(A,⁻1,"BAD COLUMN")',
                       'Text(⁻1,A,265,"BAD LARGE COLUMN")'):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    self.audit(source)

    def test_actual_token_colors_and_line_styles(self):
        for source in ('TextColor(9)', 'TextColor(25)', 'TextColor(12.5)',
                       'Line(A,B,C,D,9)', 'Line(A,B,C,D,10,5)',
                       'Line(A,B,C,D,E,1.5)'):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    self.audit(source)
        self.audit('TextColor(E)\nLine(A,B,C,D,E)\nLine(0,0,1,1,0,1)')

    def test_literal_window_settings_and_final_order_are_checked(self):
        for source in ('0→Xres', '9→Xres', '1.5→Xres', '⁻1→Xscl',
                       '⁻1→Yscl',
                       '1→Xmin\n0→Xmax\n0→Ymin\n1→Ymax\nClrDraw',
                       '0→Xmin\n1→Xmax\n1→Ymin\n0→Ymax\nLine(0,0,1,1)'):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    self.audit(source)
        self.audit('100→Xmin\n⁻100→Xmax\n200→Xmax\n0→Ymin\n1→Ymax\nClrDraw')
        self.audit('A→Xmin\nB→Xmax\nC→Ymin\nD→Ymax\n1→Xres\nClrDraw')


if __name__ == '__main__':
    unittest.main()
