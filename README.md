# VECTOR CE — 2D vectors on the calculator

A native, unprotected **TI-BASIC** program for the **TI-84 Plus CE** and **TI-84 Plus CE Python**. The Python edition runs this in its normal PRGM menu; it does **not** use the calculator's Python app, assembly, shells, or jailbreaks. Supports up to 20 mixed polar/component vectors per session.

**Testing status:** transfer files were generated and checked, and the source-level tests pass. This release has **not** been run on a physical calculator or a calculator emulator. See [validation](docs/VALIDATION.md) for the precise checks and a calculator acceptance checklist.

## Try it and see it

- Open [the interactive demo](dist/try-vector.html) in a browser, or open `index.html` from this repository. The single-file demo works offline and includes compass entry, editing, all graph views, triangles, step-through addition, and worked calculations. Data stays in the tab; it starts with an empty list and blank inputs, and refreshing returns to that empty state. Example buttons load vectors only when you choose them.
- [Browser screenshot](docs/browser-preview.png) · [mobile screenshot](docs/browser-mobile.png)
- [Calculator layout picture](docs/calculator-preview.png): rendered from the source drawing commands with approximate fonts; **not a hardware or emulator screenshot**.

### Calculator-screen video and image collection

[Watch the 40-screen walkthrough](docs/walkthrough/vector-ce-walkthrough.mp4) · [video player](docs/walkthrough/index.html) · [all images as a ZIP](docs/walkthrough/walkthrough-images.zip) · [storyboard overview](docs/walkthrough/contact-sheet.png).

The two-minute video shows entry, review, vector addition, graph modes, triangles, calculations, compass directions and cancellation on a calculator-style screen. It is explicitly labeled a **source-layout simulation, not hardware or emulator footage**. [Media details and regeneration instructions](docs/walkthrough/README.md).

The browser version is a companion for trying the workflow. The eight `.8xp` programs are the calculator product. JavaScript uses binary64 arithmetic; TI-BASIC uses the calculator's own numeric precision.

## OS 5.8 startup syntax-error fix

If an earlier download gives **ERR:SYNTAX immediately after launch**, use the [rebuilt OS 5.8 package](dist/VECTORCE-OS58.zip). Back up your calculator, then use TI Connect CE to **replace all eight program files belonging to this app in RAM** and run VECTORCE from PRGM. The old build incorrectly encoded Pause, FnOff and PlotsOff as letters; the rebuild uses their real command tokens. Polar input also now uses TI-BASIC `int(` for angle normalization. The build audits the actual saved tokens against CE OS 5.8 metadata, in addition to checksums. Hardware/emulator execution on OS 5.8 has not been performed here.

## Transfer and run (no computer Python needed)

1. Install **TI Connect CE** for your computer from [Texas Instruments](https://education.ti.com/en/products/computer-software/ti-connect-ce-sw). Use TI Connect **CE**, not the older TI Connect application.
2. Back up your calculator with TI Connect CE first. Check that none of these program names already belongs to your work: `VECTORCE`, `VQARROW`, `VQGRAPH`, `VQMATH`, `VQNUM`, `VQPAGE`, `VQSUM`, `VQWORK`. **Do not accept an overwrite of an unrelated program.** Move/rename your existing program on the calculator first if there is a conflict. Keep the supplied names unchanged because programs call each other by name.
3. Unzip [VECTORCE.zip](dist/VECTORCE.zip). Connect and turn on the calculator using its USB cable. Open Calculator Explorer in TI Connect CE.
4. Select **all eight `.8xp` files** from the package and drag them into Calculator Explorer (or use Send to Calculators). Send them to **RAM**. Allow at least 20 KB free RAM for programs, matrix, strings, and execution; more is helpful. No App installation is required.
5. On the calculator press **PRGM**, choose **VECTORCE** under EXEC, press **ENTER**, then **ENTER** to run it. Run only VECTORCE; the other programs are helpers.
6. Read the workspace notice and press ENTER. Choose CANCEL unless matrix **[J]** can be erased. YES START begins a new empty session. This does not erase any user lists.

The program uses [J], A–Z, θ, Str1 and Str2. **Back up any values you need in these variables first.** See [variables and settings](docs/VARIABLES.md). It never creates, deletes, or replaces a program at runtime. All vectors remain in [J] after quitting, but a new run clears them after asking again; there is no session-resume feature.

## Enter “24 units, 30 degrees east of north”

Choose:

1. **ADD VECTOR → MAG / ANGLE**. Type `24`, then ENTER.
2. **COMPASS WORDS**. Type `30`, then ENTER.
3. **NORTH → EAST OF NORTH**.

The resulting vector has standard angle **60°**, x = **12**, y ≈ **20.78460969**. “East of north” starts at north and turns toward east. It is different from “north of east,” which starts at east. All eight compass forms are available: east/west of north/south and north/south of east/west. Compass angles must be 0–90° inclusive.

Enter the numeric magnitude only, without the word “units.” Use one consistent unit for all vectors (e.g. all newtons or all metres). This program does not convert units.

For a standard polar vector choose **STANDARD CCW +X**: angles are degrees, **counterclockwise from the positive x-axis**. East = 0°, north = 90°, west = 180°, south = 270°. Negative angles and multiple turns are accepted and normalized to 0–360°. Magnitudes must be nonnegative; for a reversed vector change the direction by 180°.

Choose **X / Y** to enter signed horizontal and vertical components. East/right is positive x; north/up is positive y. You may mix both input types in one list. A zero vector is allowed.

Numeric input accepts ordinary decimals, an optional leading negative sign, and at most 18 characters. Use the calculator's **(-)** key for negative values. Enter `0` or a value whose absolute value is between `0.000000001` and `1000000000`, inclusive. For example, type `0.000000001`, **not** `1E-9`. Expressions, fractions, EE notation, commas and units are rejected. Type **Q** (use ALPHA if needed, then the Q key), ENTER, to cancel any numeric prompt. A canceled add/edit leaves existing data unchanged.

## Review and controls

| Where | Controls |
|---|---|
| Main menu | Add Vector, Vectors, Results, Show Work, Graphs, Help, Quit |
| Vectors | Read the vector, then ENTER for Show Work, Triangle, Edit, Delete, Next, Previous, or Main Menu |
| Results | Immediate x/y totals, magnitude and angle; 1 or ENTER opens work, 2 opens its triangle, CLEAR returns |
| Editing | Re-enter the vector using either input type; commits only after both values and direction are valid |
| Delete | Requires YES; remaining vectors keep their order |
| Work pages | ENTER next; CLEAR back to the calling menu |
| Graph | CLEAR back; other keys leave the graph displayed |
| Step-through graph | RIGHT or ENTER adds a vector; LEFT removes the latest; endpoints stop at 0 and N |
| Any numeric prompt | Q + ENTER cancels |

Use MAIN MENU/BACK in menus to navigate. HELP is always available from the main menu. Use **QUIT** for a normal exit. ON interrupts TI-BASIC with the OS break menu; it cannot reliably restore settings or finish an in-progress edit, so use ordinary navigation when possible. If interrupted, choose Quit and use the settings instructions below. Do not edit [J] or the scalar workspace while a session is running.

## Results and work

**RESULTS** immediately shows total x, total y, magnitude, and direction together. You do not have to advance through the calculations to see the answer. Press **1** or **ENTER** for work, **2** for the resultant triangle, or **CLEAR** to return to the main menu.

**SHOW WORK** is also available directly from the main menu. Choose:

- **MAG / DIRECTION** for the magnitude formula, substituted components, quadrant rules, and direction.
- **COMPONENT SUMS** for each vector's x/y values and the running additions; finishing returns to the work topics.
- **FULL WORK** for component sums followed by magnitude and direction.

Under **VECTORS**, press ENTER for options and choose **SHOW WORK** to explain that vector, or **TRIANGLE** to open its graph immediately. **VIEW AGAIN** repeats the work, and CLEAR on any work page returns to the calling screen. Pages show formulas and substituted values separately so they fit the home screen. Component inputs show their derived polar form as a check. All polar formulas use the normalized standard angle, including vectors entered with compass words.

The calculation is:

- `x = r cos(angle)`, `y = r sin(angle)`
- `Rx = sum(x)`, `Ry = sum(y)`
- `R = sqrt(Rx^2 + Ry^2)` (implemented with a scaled equivalent to avoid unnecessary squaring of extremes)
- `atan(Ry/Rx)` with +180° when Rx < 0, then +360° if negative. Rx = 0 is handled separately: 90° for positive Ry, 270° for negative Ry.

An exact zero vector/resultant has **no defined direction**. The work pages say so instead of dividing by zero. A nonzero resultant smaller than or equal to `1e-12 * sum(magnitudes)` gets a **near-cancellation warning**, but its value and computed angle are retained. Very small residuals can reflect finite calculator precision; the warning does not silently replace them with zero. Opposite polar vectors use consistent half-turn reduction, and exact cardinal angles have their known zero component set explicitly.

The calculator keeps its native numeric precision internally; no `round(` is used in calculations or storage. Normal/Float display limits visible digits. Displayed components can therefore differ slightly from the last digits of an independently rounded calculation. The code does not offer arbitrary precision.

## Graphs

- **HEAD TO TAIL:** numbered blue arrows in input order and the red resultant from (0,0) to the last endpoint.
- **COMMON ORIGIN:** all blue vectors start at (0,0); red is the total resultant.
- **INSPECT TRIANGLE:** enter a vector number, or `0` for the resultant. The triangle opens directly; use SHOW WORK from the main menu or vector options when you want the calculations. Green is the signed horizontal component; orange is the vertical leg; blue is the vector/hypotenuse. Side values and the standard angle appear on screen. The triangle is independently scaled to the selected vector.
- **STEP THROUGH:** starts at no vectors, then adds/removes one at a time, displaying the running red resultant and count.

Axes are labeled +X and +Y. There are no numerical tick labels: the window is for shape and direction; use the numerical work pages for exact lengths. Every plot includes the origin and all relevant endpoints, with a margin. The x/y window span ratio is `264/164`, matching CE graph-pixel spans, so one horizontal unit and one vertical unit have equal screen lengths. Changing window size alone without respecting that ratio would distort angles.

Arrowheads shrink for short arrows. Zero vectors draw a point. In overview plots, identical or collinear arrows and their number labels may overlap; the red resultant is drawn last. Select their individual triangles to inspect them separately. Vectors many orders of magnitude smaller than the largest may be subpixel in an overview; triangle inspection rescales them. This is a screen-resolution limit, not lost stored precision.

## Settings and troubleshooting

Normal exit restores the initial degree/radian mode. The program sets Normal, Float and Real modes. Graphing also sets Full/Func, disables equations and stat plots, turns axes/grid/coordinates/expressions/background off, and changes the graph window. It preserves equation contents, user lists, and pictures/GDBs; it **does not** automatically restore the previous graph/display settings. It avoids a StoreGDB backup that might overwrite your existing GDB. Record your window/modes beforehand if needed.

Afterward, use MODE to restore desired display/graph modes; WINDOW for your old bounds (or ZOOM → ZStandard for the ordinary standard window); Y= to re-enable desired equations; 2nd Y= for stat plots; and 2nd ZOOM (FORMAT) for axes/background. ZStandard is a convenient reset, **not restoration of your exact previous window**.

- **ERR:UNDEFINED / a helper won't run:** ensure all eight programs are transferred under their original names, in RAM.
- **ERR:MEMORY:** back up and archive other calculator data to free RAM; don't delete work blindly.
- **ERR:SYNTAX:** replace the earlier app files using the OS 5.8 package above. Hand typing multi-character command names or a minus token in place of negation can cause syntax errors. The text sources are not directly executable files.
- **Unexpected graph:** only use the program's graph menu during a session; it sets its own window. Inspect a single triangle if arrows overlap.

## Source and development

Complete TI-BASIC source is in [src](src). The `.txt` files use Unicode TI token spellings: `→` is STO→, `⁻` is the (-) negation token, `tan⁻¹` is inverse tangent, `θ` is theta, and `[J]` is the matrix token, not three typed characters. `prgmVQ...` refers to a helper program. Text in quotes is literal text. There are no comments in executable source.

To recreate the transfer files exactly using a computer with Python 3.10+:

```sh
cd /workspace/vector  # or the folder containing this README on your computer
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python tools/build.py
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tools/standalone.py
.venv/bin/python tools/preview.py
.venv/bin/python tools/package.py
```

On Windows use `py -3 -m venv .venv` and `.venv\Scripts\python.exe` in place of `.venv/bin/python`. Send the resulting eight files in `dist/` with TI Connect CE. The ZIP is a convenience package, not a file to send directly to the calculator.

Alternatively, in TI Connect CE's Program Editor create each program using its source filename without `.txt`, insert actual calculator tokens from the editor's catalog, and copy every line from that file. Do not type Unicode command spellings as ordinary letters. Keep all eight program names and internal labels unchanged. The automated build above is the reproducible path and avoids token-entry mistakes.

Optional browser checks: run `node tests/web_math.cjs` with Node.js. To reproduce the actual desktop/mobile browser checks and screenshots, install Playwright in your Python environment and Chromium, then run `python tools/browser_check.py` (uses `/usr/bin/chromium`). These checks serve files temporarily on a local port and shut the server down after success. They do not test TI firmware.

See [research and compatibility](docs/RESEARCH.md), [variables](docs/VARIABLES.md), and [validation](docs/VALIDATION.md).
