# The World in One Day — Friday 20 November 2026

[![news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/competitions/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Mansyur0523/makefun-news-image-20261120-r2/rank.svg)](https://make.fun/competitions/news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/Mansyur0523/makefun-news-image-20261120-r2/reward.svg)](https://make.fun/competitions/news-image-20261120)

A one-page newspaper front page for **Friday 20 November 2026**: 38 stories, 13
code-drawn illustrations, one giant date masthead, a six-number strip, a
seven-region bar, a numbered world map, and a DATE CHECK that names exactly
what was left out — and why.

## What it shows

- **Masthead:** the date itself is the headline — FRIDAY 20 NOVEMBER 2026.
- **Number strip (right under the masthead):** 515 weapons at Kyiv; 300,000+
  evacuated for Cyclone Akvan; −6.2% Taiwan; 2.3% Japan inflation; 118 Phillips
  runs; $3.8bn GTA VI day-one sales — every figure with its source.
- **3 big illustrated leads:** Kyiv bridges hit overnight; Cyclone Akvan lands
  in Odisha; the AI sell-off sweeps Asia.
- **10 illustrated features:** COP31 ends with no deal, the UK–EU reset, Japan
  inflation, Kenya's first oil well, Bukele's third term, Italy's general
  strike, Phillips 118, Seoul's impeachment move, Iraqi troops in Jurf
  al-Sakhar, and the missile that crashed in Poland.
- **25 one-line briefs** ("Also on Friday 20 November"), each with its source;
  unconfirmed items are tagged **CLAIM** or **FORECAST**.
- **World map** with pins 1–13 for every illustrated story.
- **DATE CHECK:** the ICJ Myanmar ruling, the Trump–Xi–Putin Shenzhen summit,
  the APEC declaration, the second COP31 draft, the Riyadh tower attack,
  Colombia tax protests and Wall Street's 2% fall were all Thursday 19 Nov —
  deliberately excluded; BepiColombo's Mercury orbit entry is Saturday 21 Nov;
  the COP31 final text and Asia's closing prices were not yet published at
  press time.

## How it is built

`main.py` (Python 3 + Pillow, standard system fonts only) draws everything
with code — layout, text and all 13 illustrations. No external assets, no
network, no random numbers, no timestamps at runtime: two runs produce a
byte-identical `entry.png`.

```sh
python3 main.py   # -> entry.png (1024x1024, RGB)
```

## Files

- `main.py` — the whole entry: data, layout, 13 illustrations, map
- `entry.png` — the rendered front page (1024×1024)
- `LICENSE` — MIT
