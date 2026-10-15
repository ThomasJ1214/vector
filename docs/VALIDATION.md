# Validation record

## Executed in this environment

- Installed pinned `tivars==1.1.1` in a local virtual environment.
- Generated all eight unprotected `.8xp` files from complete TI-BASIC source using the CE token table, with tokenization warnings treated as failures.
- Checked each TI container signature, declared length and 16-bit payload checksum.
- Detokenized and retokenized each generated program and compared token bytes.
- Ran **77 automated tests**, covering source behavior, actual calculator tokens, and static instruction syntax, including many data cases, via `python -m unittest discover -s tests -v`.
- Checked internal labels for uniqueness/length, branch destinations and helper file presence.

The custom test harness reads the actual `.txt` source, follows menus/branches/loops/calls, parses decimal input, and executes arithmetic with Python binary64. The expanded harness also evaluates drawing coordinates, text and window settings, checks matrix indices and screen rows/columns, and tracks degree/radian mode. It records drawing/display commands; the separate preview generator renders approximate layouts from those commands, without emulating the TI display. It is **not a TI calculator emulator**, does not use TI's BCD arithmetic, and cannot establish that every TI OS parser/layout/keyboard behavior is correct. Generated-file checks establish token/container integrity, not successful calculator execution.

No hardware tests or CEmu tests were run. CEmu is not installed and no user calculator ROM is provided. A native TI-BASIC build is delivered; actual calculator runtime validation remains outstanding.

## Expanded review and browser validation

The second pass fixed a zero-vector list screen that previously displayed a placeholder angle as though it were defined. It also bounded normalized output angles to below 360°, aligned numerical work pages using fixed home-screen positions, added magnitude to review, reserved graph title/footer areas, and avoided needless redraws on unrelated or out-of-range step keys.

The 29 source tests include 600 seeded random Cartesian cases, angle-wrap extremes, compass boundary angles (0°/90°) and out-of-range retries, cancellation at every entry stage, declined deletion, representation-changing edits, list wrapping, startup workspace preservation, degree/radian restoration, long invalid-input recovery, graph-coordinate containment and equal unit scaling, independent tiny-triangle scaling, step limits, CLEAR from every work page, menu limits and home-text widths.

The browser companion has separate tests:

- `node tests/web_math.cjs`: **6,023 numerical assertions**, plus validation, exact zero, cancellation and quadrant checks. Includes 2,000 seeded random polar vectors.
- `python tools/browser_check.py`: actual headless **Chromium** interactions covering example buttons, graph modes, step controls and limits, inspect/edit/cancel/delete, negative magnitude, malformed input, zero-vector direction, capacity, every compass form, mobile width, standalone demo loading, and absence of JavaScript page errors.
- Desktop/mobile images are actual browser screenshots. Calculator pictures are explicitly labeled source-layout previews with approximate fonts. Neither is a TI emulator result.

## Known examples checked against the source

| Inputs | Expected result |
|---|---|
| Polar (3, 0°), Cartesian (0, 4) | Rx=3, Ry=4, R=5, angle ≈53.13010235° |
| Cartesian (3, 4) | R=5, angle ≈53.13010235° |
| Cartesian (-3, 4) | R=5, angle ≈126.86989765°, 53.13010235° north of west |
| Cartesian (-3, -4) | R=5, angle ≈233.13010235° |
| Cartesian (3, -4) | R=5, angle ≈306.86989765° |
| (0,2), (0,-2), (2,0), (-2,0) individually | 90°, 270°, 0°, 180° respectively |
| Polar (10, 0°) + (10, 180°) | exact (0,0), R=0, undefined direction |
| Polar (24, -330°) + (24, 210°) | opposite vectors cancel using common half-turn evaluation |
| 24 at 30° east of north | angle=60°, x=12, y≈20.78460969 |
| 30° in all eight compass forms | standard angles 60,120,300,240,30,330,150,210° |
| (0,0) | R=0, no defined angle, no divide-by-zero |
| (1e9,1e9) | finite magnitude; all graph control branches execute in source harness |
| Tiny components (1e-18,-1e-18), supplied directly to math helper | finite magnitude, angle=315° |
| Near cancellation (1e9,0)+(-1e9+.001,0) | nonzero retained; precision warning flag, not zeroed |

Other checks: malformed decimals and expressions rejected; minimum/maximum allowed decimal inputs accepted; leading (-) and minus accepted; Q cancellation; canceled edit preserves original components; 20-vector capacity; deletion shifts rows; result pages; graph return/step keys; individual triangle calls. Error recovery in the source numeric loop completes For/End before retrying rather than jumping out and retaining an unfinished loop frame.

## Calculator / CEmu acceptance checklist (not yet executed)

1. Back up calculator data. Transfer all eight files to a TI-84 Plus CE or CE Python, in RAM. Launch VECTORCE via PRGM, not the Python app.
2. Verify the startup notice appears before the [J] consent menu. CANCEL must leave [J] unchanged. YES START should clear only the disclosed workspace.
3. Enter the examples above using calculator keys. Confirm all visible results, page pagination, direction wording, Q cancel, and CLEAR back.
4. Enter 24 → COMPASS WORDS → 30 → NORTH → EAST OF NORTH. Review should show 60° and the components above.
5. Exercise NEXT/PREVIOUS, change polar to Cartesian in an edit, cancel after the first edited value, and delete a middle vector.
6. Plot (3,0),(0,4). Check a 3-by-4 right triangle with undistorted unit scales, two arrowheads, sequence numbers, axes, and the red resultant.
7. Check common-origin, identical vectors, opposite vectors, all-zero vectors, large/small mixed values, and each independently scaled triangle. Confirm triangle side/angle text does not clip on the target OS.
8. Step from 0 to N and back. Verify running resultant endpoint, key codes, no out-of-range matrix accesses, and CLEAR return.
9. Check an initial Radian mode is restored by QUIT; check the documented graph/display changes and that user lists/equation contents/pictures/GDBs remain intact.
10. Repeat on both requested model variants, or with appropriately owned ROMs in CEmu. Record OS versions and any failures before calling the release hardware-tested.

To test in CEmu, follow its built-in ROM-dump wizard using your calculator, load that ROM, import all eight `.8xp` files, and follow the same checklist. Source-level tests are supplemental, not a substitute for that process.

## Add button regression

Reproduced a failure in Chromium with the single-file demo inside an iframe using `sandbox="allow-scripts"` without `allow-forms`: clicking the old submit button left the vector count unchanged and logged a blocked form submission. The add/save button now uses a direct click action; Enter in an input invokes the same action without submitting the form. Added browser regression checks for polar/component additions, Enter adding exactly once, editing, and invalid-input preservation inside that restricted preview. Previews that disable JavaScript altogether still require opening the downloaded HTML in a browser.

## Empty launch and walkthrough media

The browser checks assert that the source page and bundled demo start at 0/20, with zero totals, no defined direction and blank fields. They exercise the first manual addition and verify that reload clears the list; example buttons load data only after a click.

The repository also contains a 40-frame source-layout walkthrough: individual SVGs/PNGs, a contact sheet, a timed storyboard, an image archive, and a silent 1280×720 H.264 MP4. These images are generated by the source harness and Chromium, with a visible simulation disclaimer; they are not calculator/emulator captures. The generator asserts known values for the 3–4–5 example, compass input, and exact cancellation. Media verification checks file counts, MP4 dimensions/codec/duration, and full-stream decoding. Chromium also verified playback and seeking in the video player.

## Native calculator UI update

The calculator now separates immediate RESULTS from SHOW WORK. Results display x/y totals, magnitude, and direction on one home screen, with 1/ENTER for calculations, 2 for the triangle and CLEAR for the main menu. Work topics let the student inspect magnitude/direction alone, component sums alone, or the full sequence. Individual vector options and the graph picker open triangles directly. Existing videos and browser UI are retained as earlier companion material, rather than regenerated by this update.

Ten new source-level tests cover immediate answers without work pages, short work routes, component topics, result shortcuts, direct vector/graph triangles, undefined zero direction, repeating/canceling work, and viewing the magnitude of a 20-vector result without traversing every term. All 39 source tests passed. New calculator containers passed token and checksum checks. No physical-calculator or TI emulator run has been performed.

## Startup ERR:SYNTAX and OS 5.8 audit

The earlier tests were insufficient: the source harness treated Pause/FnOff/PlotsOff as commands, but the generated binaries contained ordinary letters. Even detokenization/retokenization reproduced those invalid executable sequences, so the round trip passed. The first bad Pause occurred immediately after the splash. The audit also found unsupported `floor(` in polar-angle conversion.

The corrected build emits D8 for all six Pause sites, 97 for FnOff, EA for PlotsOff, and B1 for `int(` normalization. Tests now examine exact opcodes in saved `.8xp` files, reject old letter encodings even when their round trips pass, allow ordinary text within strings, verify TI int/iPart semantics, and check numeric OS version ordering. Every generated file passes the CE OS 5.8 token-availability check and its checksum/round-trip checks. All 48 automated tests pass. The named OS58 ZIP and standard ZIP contain the same rebuilt files. Native OS 5.8 execution remains untested here.

## R2 Add Vector syntax repair and whole-project static audit

The remaining bad label was `PV`: the tokenizer selected the Finance present-value token `63 2D`, rather than the two label letters. Both `Lbl PV` and the PREVIOUS menu destination contained that token. This malformed label lies in the source area searched when Add Vector jumps to its input menu, matching the reported immediate failure. It was renamed to `P1`, and the saved binary now contains `D6 50 31` for the label and `50 31` for the menu destination. R2 is identified on the startup screen.

`tools/ti_syntax.py` now statically audits all **779 statements across eight saved programs**. It validates the actual label/program-name character bytes, all jump and menu destinations, menu pair counts, called-program presence, command/function argument counts, expression operands and delimiters, scalar/string/matrix targets and types, and balanced conditional/loop blocks. Sixteen added regression tests reject the old Finance-token label and malformed expressions, stores, loops, matrices, calls and command arguments. All 64 tests pass.

This validator is explicitly for the instruction subset used by this project. It is not TI's firmware parser and does not establish hardware/emulator execution. The two independent read-only audits and new static checks found no other R2-project syntax defect. At R2, the standard, OS58 and OS58-r2 ZIPs contained identical binaries.

## VECTRA CE R3 fit and graphical UI

R3 retains the eight program names, with VECTORCE as the launcher, and displays VECTRA CE. The graphical loading page starts only after workspace consent, initializes an empty matrix/session, and uses documented large `Text(⁻1,...)` syntax. Normal exit still restores the initial angle mode. The startup splash now changes the disclosed graph/display settings even if no graph is subsequently opened; CANCEL before initialization leaves graph settings alone.

The graph fitter uses only the visible view's data: origin and cumulative endpoints for head-to-tail/step, origin/individual endpoints/resultant for common-origin, and the chosen vector/resultant for triangle inspection. It centers their bounding box in a reserved 240-by-98-pixel plot area, adds a 16% margin, and uses the same units per pixel on both axes. Step mode keeps the complete path's fitted window unchanged during addition/undo. Arrowheads are six pixels or one-quarter of the vector length, whichever is smaller. Navy text and colored rules use a plain background; text transparency is not assumed.

Nine new graph tests check endpoint containment, useful plot occupancy, centering, repeated-vector resultants, cancellation excursions, view-specific bounds, tiny selected/resultant triangles beside large vectors, zero/axis/extreme data, equal unit scales and a window snapshot on every step/undo key. Startup tests check the empty session, graphical name/READY screen, and declined-consent preservation. Token and grammar tests check the large-text negation flag and its required numeric row/column arguments. All **77 tests** pass; the builder audits all **863 statements in eight saved programs**, plus OS 5.8 token availability, checksums and token round trips.

The updated calculator PNG/SVG was rendered and visually inspected from the source commands with approximate fonts. No physical calculator or TI emulator test of R3 was run. The user's report confirmed the preceding R2 calculator build works well; that report is not a hardware test of the new R3 changes. VECTORCE.zip, VECTORCE-OS58.zip and VECTRA-CE-OS58.zip contain the current build; VECTORCE-OS58-r2.zip is retained unchanged as the previous build.
