"""Shared conservative drawing guards for the project's CE TI-BASIC subset.

These checks are deliberately stricter than the graph's full pixel rectangle.
In particular, the text margins leave room for the calculator's font height;
they are project layout limits, not a claim about an exact OS error boundary.
This module is not an implementation of TI's parser or drawing engine.
"""
import math
from numbers import Real


SMALL_TEXT_ROW_MAX = 150
LARGE_TEXT_ROW_MAX = 140
TEXT_COLUMN_MAX = 264
WINDOW_VALUES = frozenset(('Xmin', 'Xmax', 'Ymin', 'Ymax',
                           'Xscl', 'Yscl', 'Xres'))


class CalculatorDomainError(ValueError):
    """An argument violates this project's conservative calculator limits."""


def _real(value, label):
    try:
        finite = isinstance(value, Real) and math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        raise CalculatorDomainError(f'{label} must be a finite real number')
    return value


def _integer(value, minimum, maximum, label):
    _real(value, label)
    if value != int(value) or not minimum <= value <= maximum:
        raise CalculatorDomainError(
            f'{label} must be an integer from {minimum} to {maximum}')
    return value


def validate_color(value):
    """Check a CE graph color index, from BLUE (10) to DARKGRAY (24)."""
    _integer(value, 10, 24, 'color')


def validate_text(args):
    """Check Text([negative-one,] row, column, content...) arguments.

    The safe top-row limits reserve space below text. They intentionally reject
    R3's row-156 footer even though that row lies inside the pixel rectangle.
    """
    args = list(args)
    large = bool(args) and args[0] == -1
    coordinates = args[1:] if large else args
    if len(coordinates) < 3:
        raise CalculatorDomainError('Text requires row, column, and contents')
    maximum = LARGE_TEXT_ROW_MAX if large else SMALL_TEXT_ROW_MAX
    _integer(coordinates[0], 0, maximum,
             'large Text row (project safe margin)' if large else
             'Text row (project safe margin)')
    _integer(coordinates[1], 0, TEXT_COLUMN_MAX, 'Text column')
    for value in coordinates[2:]:
        if not isinstance(value, str):
            _real(value, 'Text numeric contents')


def validate_line(args):
    """Check endpoints, optional draw/erase or color, and optional line style."""
    args = list(args)
    if not 4 <= len(args) <= 6:
        raise CalculatorDomainError('Line requires four to six arguments')
    for value in args[:4]:
        _real(value, 'Line endpoint')
    if len(args) >= 5:
        option = args[4]
        _real(option, 'Line draw/erase or color')
        if option not in (0, 1):
            validate_color(option)
    if len(args) == 6:
        _integer(args[5], 1, 4, 'Line style')


def validate_window_store(name, value):
    """Validate one window value, allowing temporarily reversed bound stores.

    TI-BASIC assigns these fields one at a time. Checking their ordering during
    each store would reject valid transitions between two graph windows.
    """
    if name not in WINDOW_VALUES:
        raise CalculatorDomainError(f'unknown window setting {name!r}')
    _real(value, name)
    if name in ('Xscl', 'Yscl') and value < 0:
        raise CalculatorDomainError(f'{name} must be nonnegative')
    if name == 'Xres':
        _integer(value, 1, 8, 'Xres')


def validate_window(values):
    """Check a complete set of graph bounds before a drawing command.

    Scale/resolution settings are checked when supplied. Other calculator
    variables may be present in the mapping and are ignored.
    """
    for name in ('Xmin', 'Xmax', 'Ymin', 'Ymax'):
        if name not in values:
            raise CalculatorDomainError(f'missing graph bound {name}')
    for name in WINDOW_VALUES:
        if name in values:
            validate_window_store(name, values[name])
    if not values['Xmin'] < values['Xmax']:
        raise CalculatorDomainError('graph window requires Xmin < Xmax')
    if not values['Ymin'] < values['Ymax']:
        raise CalculatorDomainError('graph window requires Ymin < Ymax')
