# Storyboard Example (English)

Short 4-cut sitcom-style dialogue rendered with the `storyboard` template.
The humor leans on the pictogram's unchanging face — Bob's every "reaction"
lands on the same flat silhouette, and the speech bubble carries all the
tone.

## Scene

**The Box** — Alice fakes a confession to get a reaction out of her deadpan
husband Bob. When she admits she was joking, Bob lets slip exactly how much
of a disaster it would have been — and accidentally outs the real secret he
was guarding.

| Cut | Speakers | Duration | Beat |
|:---:|:---|:---:|:---|
| C-001 | Alice | 6 s | Setup — "brace yourself". |
| C-002 | Alice / Bob | 10 s | The bomb drops; Bob's flat reaction. |
| C-003 | Alice / Bob | 8 s | Prank revealed; Bob involuntarily confesses his panic. |
| C-004 | Alice / Bob | 8 s | Alice presses; Bob caves. Anticlimactic reveal. |

Total screen time: **32 s**.

## Files

| File | Purpose |
|------|---------|
| [`data.yml`](data.yml) | Source data for the scene (characters, cuts, bubbles). |
| [`storyboard.kata.md`](storyboard.kata.md) | Rendered storyboard document. |
| [`images/storyboard/characters/`](images/storyboard/characters/) | Character avatars (`alice.png`, `bob.png`). |
| [`images/storyboard/`](images/storyboard/) | Cut placeholder images (`C-001.jpg` … `C-004.jpg`). |

## Multiple speakers per cut

C-002, C-003, and C-004 use the `lines[]` field to let multiple speakers
take turns within a single cut. Each entry renders as its own bubble with
the speaker's avatar below it. The first character in the `characters`
array is rendered on the **left** (with a left-tailed bubble); all others
are rendered on the **right** (with a right-tailed bubble).

```yaml
cuts:
  - id: C-002
    lines:
      - speaker: alice
        text: Actually, I opened "that box" in your room today.
      - speaker: bob
        text: "…Wow. I'm shocked."
```

Single-speaker cuts keep using the simpler `dialogue: [...]` field (see C-001).

## How to regenerate

```bash
gospelo-kata build storyboard data.yml -o storyboard.kata.md
```

## Image path convention

All image references in `data.yml` use the `./images/storyboard/…`
namespace, matching the layout that `gospelo-kata init --type storyboard
--with-assets` produces inside a real project. That keeps assets from
different templates isolated if you later install more templates in the
same workspace.

## Data ↔ Document round-trip

The rendered `storyboard.kata.md` is LiveMorph-compatible:

```bash
# Extract data back from spans
gospelo-kata extract storyboard.kata.md

# Sync edits in the rendered view back into the Data block + re-render
gospelo-kata sync to-data storyboard.kata.md
```

Only values wrapped in `<span data-kata="…">` are surfaced by `extract`.
Everything else (image src attributes, icons, etc.) is preserved across
sync round-trips — `merge_extracted_into_data` applies the extract as a
patch on top of the existing Data block rather than replacing it wholesale.
