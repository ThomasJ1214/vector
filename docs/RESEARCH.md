# Command research and compatibility decisions

This is TI-BASIC, not TI-Python. Both requested CE models support TI-BASIC programs through PRGM. No native executable or Python APIs are needed. Color/graph features target the CE family; monochrome TI-83/84 calculators are not supported by this screen layout.

## References inspected

1. [TI Toolkit token sheets](https://github.com/TI-Toolkit/tokens/blob/41d03530594431a2a4eb213bbc01883df0be0528/8X.xml), revision `41d03530594431a2a4eb213bbc01883df0be0528`. The XML records calculator/OS introduction and spellings for commands. Checked Menu, Input, Output, getKey, dim, Fill, If/Then/Else, For, Repeat, Line, Text, TextColor, BackgroundOff, graph mode commands, strings, trig and numeric functions. All used tokens predate or belong to the CE's inherited command set; no recent `toString(` dependency was introduced.
2. [ClrHome command catalog](https://github.com/clrhome/catalog/blob/8465d2505ac5b7f0f247be295a025ee7c9f31f00/src/catalog.xml). Inspected TI-BASIC syntax for Input, Menu (up to seven options), Output, getKey, matrix dim assignment, For, Repeat, trig, Text and Line. This catalog also includes Axe/Grammer entries; those are **not** used. Its monochrome pixel bounds and monochrome Line optional argument are **not** treated as CE color specifications.
3. [CE Pong example](https://github.com/Witchtel01/ti84-plusCE-pong/tree/857b9d0babeee6708516f135c8fe3daad2b14d09). Inspected its actual tokenized TI-BASIC program using tivars, confirming CE usage of `TextColor`, `Text(row,column,...)`, and `Line(x1,y1,x2,y2,color)`. No source was copied into this project.
4. [CE TI-BASIC ray tracing example](https://github.com/TheScienceElf/TiBASIC-Raytracing/tree/0ad64058333ff46aae3e1c2876b90185e39b605e). Inspected its tokenized CE program, including the 264/164 graph span relationship and colored pixel use. The program here uses the corresponding CE logical graph space (265 × 165 positions), not the physical 320 × 240 LCD dimensions.
5. [TI Toolkit tivars library](https://github.com/TI-Toolkit/tivars_lib_py), installed package **tivars 1.1.1**. Used for model-aware tokenization, TI program containers, and checksums. Tokenization success does not constitute TI-BASIC syntax execution or on-device testing.
6. [CEmu README](https://github.com/CE-Programming/CEmu/blob/7c4aa0b9e83434e2b4d31d5c21166e9954a7416e/README.md). CEmu is suitable for TI-84 Plus CE testing but requires a ROM dumped from the user's own calculator. No such ROM is available in this workspace. No ROM was downloaded and no emulator test was claimed.
7. [CE OS color definitions](https://github.com/CE-Programming/toolchain/blob/master/src/ce/include/ti/ui.h). Checked the OS palette for the graphical UI: navy is 17 (blue 10, red 11, black 12, green 14, orange 15, gray 23). The existing pinned ClrHome catalog explicitly documents `Text({-1,}row,column,...)`; the current splash uses the unary-negation token in `Text(⁻1,80,78,"VECTRA CE")` to select large text. Titles use colored text on the plain background so readability does not depend on transparent text rendering.
8. [TI-Basic Developer static backup](https://github.com/tibasicdev/tibasicdev.github.io/tree/b77c24c293a3b368ce39fc37e43ae62992e673fc), specifically [Text](https://github.com/tibasicdev/tibasicdev.github.io/blob/b77c24c293a3b368ce39fc37e43ae62992e673fc/docs/text.md), [TextColor](https://github.com/tibasicdev/tibasicdev.github.io/blob/b77c24c293a3b368ce39fc37e43ae62992e673fc/docs/textcolor.md), [Line](https://github.com/tibasicdev/tibasicdev.github.io/blob/b77c24c293a3b368ce39fc37e43ae62992e673fc/docs/line.md), and system variables. Retrieved through GitHub during R4 diagnosis after the live site was blocked. Text requires integral, in-range coordinates; TextColor accepts integral indices 10–24; Xres accepts integers 1–8. The Text page mixes monochrome and color bounds/font descriptions, so its full pixel rectangle is not treated as a guarantee that text can safely start on the last pixel rows.
9. [BasicNote CE](https://github.com/Michael2-3B/BasicNoteCE/tree/c19d24bcac6f9b005f98c555b2b4ece80e36db67), an independent pure TI-BASIC editor with calculator screenshots. Reviewed its `Text(150,...)` footers, text spacing and actual CE font appearance; no source code was copied. This showed that the former preview's approximately six-pixel text was far too small. R4 uses conservative project limits of row 150 for small text and row 140 for large text. These are layout guardrails, not a claim about an exact firmware error boundary.

## Official documentation access limit

Attempts to retrieve the [TI-84 Plus CE reference guide](https://education.ti.com/html/eguides/graphing/84PlusCE/EN/Subsystems/ti_84_ce_ref/Content/M_Ref/Programming/Programm.htm) and TI's reference PDF returned HTTP 403 from this environment's network route. Direct TI-Basic Developer requests were also blocked. The conclusions above use the accessible token tables, catalog and CE programs, rather than pretending those official pages were read. The official TI Connect CE download page is linked in the README for the user.

## Implementation choices

- TI's angle mode controls trig; the program explicitly uses Degree and restores the initial angle mode on normal exit.
- Quadrant handling is implemented with inverse tangent and explicit axis cases rather than relying on an unsupported `atan2` spelling.
- Every Menu has at most seven choices and every label has at most two characters. Helpers are ordinary unprotected programs with names of at most eight characters.
- Inputs are captured as strings and parsed as decimal digits. They are not passed to `expr(`, preventing malformed expressions from causing evaluation errors or modifying workspace variables.
- Matrix [J] holds data after visible consent, leaving user lists alone. No automatic GDB/picture backup can overwrite existing files.
- Lines and short angled line segments make arrows. Color constants are numeric: blue 10, red 11, black 12, green 14, orange 15, gray 23.
- All code is tokenized against the CE model. The latest required token family according to tivars' minimum-OS metadata is inherited color-84 functionality; CE support is an intended compatibility target, pending calculator/emulator acceptance testing.

## OS 5.8 syntax repair

A later audit of the actual shipped bytes found a tokenizer spelling issue in tivars 1.1.1: commands with optional arguments use canonical spellings with trailing spaces. Bare source `Pause`, `FnOff` and `PlotsOff` had been encoded as letter tokens, rather than D8, 97 and EA. The builder now supplies the canonical spellings internally and verifies the exact opcodes on every affected source line. It also rejects unexpected lowercase executable characters outside quoted strings.

The original angle normalization used `floor(`, which is not a TI-BASIC function. It now uses `int(` (B1), defined by the pinned ClrHome catalog as the largest integer less than or equal to its argument. `iPart(` instead truncates toward zero; the source harness was corrected to distinguish these functions. Negative angle-wrap checks pass with the supported function.

All used commands have token minimum-version metadata compatible with TI-84 Plus CE OS 5.8. The build checks numeric version components for the CE model, including the distinction between 5.8 and 5.10. This confirms command availability and repaired encoding, not execution on a 5.8 calculator or emulator.

## Identifier context / Finance PV collision

The token sheets identify `63 2D` as the Finance variable `PV`. The first tokenizer audit missed it because it is a valid uppercase system-variable token, while TI-BASIC label operands require one or two individual label characters. A native label search crosses this malformed label on the Add Vector route. R2 renames it P1 and validates actual bytes for every Lbl, Goto, Menu destination and program call. Expression and statement grammar checks supplement availability/checksum checks. This repairs a definite invalid label; the runtime route remains subject to testing on the user's calculator.
