# samforob.github.io

Static single-page campaign site for **Sam Holland for Oak Bay Mayor**, served by
GitHub Pages.
No build step, no JavaScript.

## Files

| Path | Purpose |
| --- | --- |
| `index.html` | The whole page. |
| `style.css` | All styling. Numbered sections; tokens in `:root`. |
| `images/` | Candidate photography. Currently SVG placeholders. |
| `Transparent Logo.png` | Wordmark used in the masthead. |
| `Solid Logo.png` | Wordmark on blue; used as the Open Graph share image. |
| `Icon.png` | Favicon and apple-touch-icon. |

Note the two logo filenames contain spaces, so they are referenced as `%20` in
`index.html`.

## Local preview

```sh
python3 -m http.server 8000
```

## Layout model: panels

The page is a vertical stack of full-bleed rounded colour **panels**, each inset
`15px` from the viewport edge and floating on the cream page background. Sections
do not share a background — each section *is* a coloured container.

```
.panel                       15px radius, 15px inset, 15px gap
  .panel--blue | --bordeaux | --orange | --red
  .container                 max 1180px, centred
    .platform-card           nested card, 15px radius
    .action-card
```

Panels use `overflow: hidden` so nested cards and images clip to the corners.
Buttons are pills (`--pill: 999px`) in a filled variant (`.btn-orange`,
`.btn-bordeaux`, `.btn-cream`) and an outlined variant (`.btn-outline`, which
takes its colour from the panel via `currentColor`).

Current order: blue hero → bordeaux about → orange platform → blue get-involved
→ red donate band → bordeaux contact → bordeaux footer.

The masthead sits inside the hero panel rather than in a separate bar, and the
orange-on-blue wordmark matches `Solid Logo.png`, which is why the hero is blue.

## Colour: the palette is not interchangeable

Per the brand sheet: Persian Blue `#1A3FC7`, Strawberry Red `#F7002D`, Princeton
Orange `#FF8513`, Almond Cream `#EEE0D3`, Night Bordeaux `#45000D`. Headers in
Dela Gothic One, body in Signika.

Measured contrast against each panel colour — **check this table before putting
text on a panel**, and prefer the `--on-*` tokens over picking a hue by eye:

| Panel | Safe for body text | Headings only (3:1) | Never |
| --- | --- | --- | --- |
| Blue | white 8.1, cream 6.3 | orange 3.3 | red 1.9 |
| Bordeaux | white 16.7, cream 12.9, orange 6.8 | red 4.0 | blue 2.1 |
| Orange | **bordeaux 6.8 only** | blue 3.3 | white 2.4, cream 1.9 |
| Red | *(none)* | white 4.2 | cream 3.3, orange 1.7 |
| Cream | bordeaux 12.9, blue 6.3 | red 3.3 | orange 1.9, white 1.3 |

Consequences baked into the current design:

- The **orange panel** carries bordeaux text only. Its cards are blue with white
  text — white directly on orange is 2.4:1 and unreadable.
- The **red panel** holds a headline and a button and no body copy. White on red
  is 4.2:1, which clears the 3:1 large-text bar but not the 4.5:1 normal-text
  bar, so every string on it must stay ≥18.66px at weight 700.
- Orange is the accent on bordeaux, but on blue it appears only as a button
  *fill*, never as small text — orange-on-blue small text fails at 3.34:1.

## Verifying

Both checks below should stay clean after any style change:

- **Contrast** — every text node on the rendered page meets WCAG AA. Re-run the
  headless audit rather than eyeballing it; several brand pairings look fine and
  measure badly.
- **Overflow** — no horizontal scroll at 1280 / 860 / 390 px.

## Before going live

Everything below is marked `TODO(sam)` in `index.html`.

- **Platform copy is missing.** The four card headings are Sam's own themes,
  taken from the hero line, but the bodies read "Platform text to come." The
  template's generic policy text was removed rather than left in place, because
  it made specific commitments in a real candidate's name.
- **The contact form does not deliver.** `action` is still the placeholder
  `https://formspree.io/f/your-form-id`.
- **Campaign email and headquarters address** are placeholders.
- **Both "Donate" links** point at `actblue.com` root, not a campaign page.
- **Candidate photography** — replace `images/candidate-hero.svg` and
  `images/candidate-community.svg`, then update `src`, `width`, and `height`.
  Both use `object-fit: cover`, so keep the subject near the centre.
- The "Why I'm Running" heading is editorial, not Sam's — the upstream copy had
  no heading, and a section without one breaks the document outline.
- Confirm the footer authorisation line matches BC election-finance rules.
