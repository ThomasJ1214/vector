# Vector CE calculator-screen walkthrough

**This is a source-layout simulation with approximate fonts, not a recording of a physical calculator or TI emulator.** Every frame and the video carry that label. It illustrates the TI-BASIC calculator workflow, using menus read from the source and home/graph drawing commands evaluated by the project's source harness. It does not provide evidence of successful TI firmware execution, exact OS rendering, or real execution speed.

- [Watch the silent 720p MP4](vector-ce-walkthrough.mp4) — 40 screens over approximately 2 minutes.
- [Open the video player](index.html).
- [See the whole storyboard](contact-sheet.png) or [browse the gallery](contact-sheet.html).
- [Download all 40 PNGs and their SVG sources](walkthrough-images.zip).
- [Frame directory](frames) · [captions and timing](storyboard.json).

The sequence begins with an empty session, adds (3,0) and (0,4), reviews both vectors, compares head-to-tail/common-origin views, steps through the running resultant, and shows the component sums, magnitude, angle and triangle. It then demonstrates compass wording (24 units at 30° east of north), negative components, exact cancellation, edit/delete menus, and controls. Screens with different example data are annotated as such. Arrow and angle values come from the source calculations; menu selection indicators, framing, captions, and fonts are illustrative.

Example vectors appear only within the opt-in walkthrough and example buttons. The interactive browser app itself starts with an empty list and blank fields.

The stored video/images show the earlier VECTOR CE appearance. The current VECTRA CE R3 startup and tighter graph layouts are shown in [the updated calculator picture](../calculator-preview.png). Rebuilding this generator uses the current source menus and graph layouts; the archived video has not been regenerated for R3.

## Rebuild

Install Playwright for Python, Chromium at `/usr/bin/chromium`, and FFmpeg with libx264, then from the repository root run:

```sh
python tools/walkthrough.py
```

The generator executes the source harness, renders 40 SVG/PNG frames in Chromium, writes the storyboard, and encodes those PNGs with FFmpeg. It produces H.264, 1280×720, 24 fps, yuv420p, with no audio and a fast-start MP4 header. `sequence.txt` provides editable per-image durations. To encode again after adjusting durations:

```sh
ffmpeg -f concat -safe 0 -i docs/walkthrough/sequence.txt -vf fps=24,format=yuv420p -c:v libx264 -crf 20 -movflags +faststart docs/walkthrough/custom-walkthrough.mp4
```

To check decoding:

```sh
ffmpeg -v error -i docs/walkthrough/vector-ce-walkthrough.mp4 -f null -
```

Hardware/emulator acceptance testing remains outstanding; see [the validation record](../VALIDATION.md).
