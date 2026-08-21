# samforob.github.io

Static single-page campaign site for **Sam Holland for Oak Bay Mayor**, served by
GitHub Pages.
No build step, no JavaScript.

## Files

| Path | Purpose |
| --- | --- |
| `index.html` | The whole page. |
| `style.css` | All styling. Numbered sections; tokens in `:root`. |
| `assets/` | All media. |

| Asset | Use |
| --- | --- |
| `assets/logo-transparent.png` | Wordmark in the masthead. |
| `assets/logo-solid.png` | Wordmark on blue; Open Graph share image. |
| `assets/icon.png` | Favicon and apple-touch-icon. |
| `assets/candidate-hero.svg` | Hero portrait. Placeholder. |
| `assets/candidate-community.svg` | Community photo. Placeholder. |

The three logo files were uploaded to the repo root with spaces in their names
(`Solid Logo.png`), which forced `%20` in every reference. They are now in
`assets/` under lowercase kebab-case names. Re-uploading through the GitHub web
UI will drop new copies at the root rather than replacing these — move and
rename them, or update the paths in `index.html`.

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
orange-on-blue wordmark matches `logo-solid.png`, which is why the hero is blue.

The hero itself follows the reference layout: the wordmark set large in the
left column beside the portrait, with the tagline demoted beneath it. The `h1`
*is* the wordmark image — the page's main heading is the candidate's name — so
the smaller masthead copy is marked `alt=""` with an `aria-label` on its link,
to avoid announcing the same name twice.

## Hard shadow

Every panel and card carries a **hard shadow** — a `box-shadow` with zero blur
in a solid colour, the same device the wordmark uses for its red edge. Measured
off `Icon.png`, that offset runs **down and to the right** at ~2% of the mark's
size, so the site matches that direction. To move it to the left instead, flip
the sign on both offsets:

```css
--shadow-x: -8px;  --shadow-x-hover: -14px;
```

The colour is per-surface, because a shadow has to be visible against whatever
it falls on. Bordeaux is the default; **bordeaux surfaces switch to red**, since
a bordeaux shadow on a bordeaux panel is invisible.

Offsets run in three tiers, so a nested card reads as sitting above its panel:

| Tier | Rest | Hover | Travel |
| --- | --- | --- | --- |
| Panels, footer | 4px | — | — |
| Cards | 8px | 11px | 3px |
| Contact card | 4px | — | — |
| Buttons (`.btn-shadow`) | 4px | 6px | 2px |

Cards and buttons grow their shadow on hover and translate back by the same
delta, so they appear to rise rather than to stretch; buttons also press flat on
`:active`. The contact card is the exception — it wraps a form rather than
acting as a target, so it stays static and nothing shifts under the cursor
while someone is filling the fields. Full-width panels take the static shadow but no hover — a hover
target spanning the whole viewport fires whenever the cursor crosses that band,
which reads as flicker rather than feedback.

Because cards sit *inside* panels, they would inherit the panel's halved offset;
they restate `--shadow-x`/`--shadow-y` to avoid that.

Note that `--shadow-x`/`--shadow-y` are consumed as **longhand at each use
site**, not pre-composed into a single `--hard-shadow` token. A custom property
whose value contains `var()` is substituted where it is *declared*, then
inherits already-resolved — so a composed token on `:root` would ignore every
per-panel `--shadow-color` override.

## Underline that grows into a highlight

In-content and nav links use `.link-highlight`: one `linear-gradient` anchored
to `0 100%`, `2px` tall at rest so it reads as an underline, animated to
`100% 100%` on hover so it reads as a marker highlight.

The text colour must flip at the same time. White text on a filled orange
highlight is 2.4:1 and effectively disappears, so `:hover` also sets
`--hl-text` (bordeaux on orange, 6.8:1).

Resting thickness is `--hl-size`, `2px` by default for nav and prose links.

The `.hl-display` variant on the hero headline sets it to a **percentage of the
line box** (`38%`) rather than a fixed length. That is what makes the band ride
up over the bottom of the glyphs like a marker stroke instead of sitting clear
underneath them — the detail that separates the reference effect from an
ordinary underline. Past roughly 44% it starts eating the letterforms.

## Heading colour

**No heading anywhere is white.** Colour is assigned per surface, using red
wherever it clears contrast and the nearest non-white brand hue where it does
not:

| Heading sits on | Colour | Ratio |
| --- | --- | --- |
| Bordeaux panel | **red** | 3.97 |
| Cream card | **red** | 3.25 |
| Blue panel or blue card | orange | 3.34 |
| Orange panel | bordeaux | 6.84 |
| Red panel | bordeaux | 3.97 |

Red is not usable on blue (1.94) or orange (1.73) — both fall under even the
3:1 large-text floor, and red on blue visibly vibrates. That three-way split is
a contrast constraint, not a preference.

All of these clear 3:1 rather than 4.5:1, which is only valid because every
heading qualifies as *large text*. `h3` is therefore set at a minimum of
`1.55rem` (~25px): Dela Gothic One ships at weight 400 only, so it cannot reach
the 18.66px-bold threshold and must clear 24px instead. Dropping `h3` back below
24px would silently invalidate the orange and red card headings.

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
- **Candidate photography** — replace `assets/candidate-hero.svg` and
  `assets/candidate-community.svg`, then update `src`, `width`, and `height`.
  Both use `object-fit: cover`, so keep the subject near the centre.
- The "Why I'm Running" heading is editorial, not Sam's — the upstream copy had
  no heading, and a section without one breaks the document outline.
- Confirm the footer authorisation line matches BC election-finance rules.
