# Workspace and settings

Back up calculator data in TI Connect CE before installing. Decline program overwrite prompts for unrelated programs. Startup explicitly asks permission to erase **matrix [J]**. No named lists, L1–L6, other matrices, strings beyond Str1/Str2, pictures, or GDBs are used as storage. Expressions such as `{20,7}` are temporary list literals, not stores to user lists.

## Persistent session data

[J] is 20 rows × 7 columns. Only rows 1 through N are active. Deleting shifts rows upward; inactive rows may contain old data. Starting another session clears every row after the startup consent menu. Quitting leaves the matrix intact for manual recovery/export, but does not implement automatic resumption.

| Column | Meaning |
|---|---|
| 1 | x component |
| 2 | y component |
| 3 | entered polar magnitude, or derived magnitude for component entry |
| 4 | normalized standard angle, 0–360° CCW from +x (placeholder 0 for a zero vector) |
| 5 | input type: 1 polar/compass, 2 components |
| 6 | running x sum through this row; refreshed before work/graphs |
| 7 | running y sum through this row; refreshed before work/graphs |

A zero vector's column 4 is only a storage placeholder, **not a defined direction**. Compass wording is converted to its standard angle; the original wording is not retained. Use the same units across entries. All columns store calculator numeric precision without display rounding.

## Globals shared by helper programs

TI-BASIC has global variables; do not call helpers directly or interrupt a session to use the workspace for another calculation.

| Variables | Use |
|---|---|
| A,B | math inputs, arrow start, temporary previous sums |
| C,D | new magnitude/angle or arrow endpoint |
| E | input type or drawing color |
| F | numeric/pager success flag |
| G | graph type (1 head-to-tail, 2 origin, 3 triangle, 4 step) |
| H | scaled magnitude intermediate / arrow length |
| I | list selection or work-term index |
| J,K | parser, key, deletion, graph and summation loop scratch |
| L | inspected vector; 0 means resultant |
| M | edit destination or step-through count |
| N | active vector count |
| O,P,Q | arrowhead size/direction |
| R,T | computed magnitude and standard angle |
| S | graph half-height after margin |
| U,V | decimal parser factor/value |
| W | parser flag or sum of magnitudes |
| X,Y | total components |
| Z | parser digit index or cancellation flag: 0 ordinary, 1 exact zero, 2 near cancellation |
| θ | original angle-mode flag: 1 degrees, 0 radians |
| Str1,Str2 | input text and single-character scratch |

## Settings

Startup records degree/radian mode by testing sin(90), then sets Degree, Normal, Float, Real. QUIT/CANCEL restore radians if it was originally active; degree mode otherwise remains active. θ must not be altered during execution.

Graphing sets Full/Func, FnOff, PlotsOff, AxesOff, GridOff, CoordOff, ExprOff, BackgroundOff, the x/y window bounds and scales, Xres=1, and TextColor. These settings are not restored. No equations are erased, and stat list data is unchanged. The graph drawing buffer and home screen are cleared. Previous drawings are not retained. No StoreGDB/StorePic is used, to avoid overwriting users' graph databases/pictures.

Restore your recorded settings with MODE, WINDOW, Y=, 2nd Y= and FORMAT after quitting. A break/error can prevent normal angle restoration; set Degree/Radian in MODE manually in that case. The in-program notice and README disclose these effects.
