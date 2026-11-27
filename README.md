# The World in One Page — 26 November 2026

[![news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/akbare12/news-26-b115-numbers/rank.svg)](https://make.fun/bounty/news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/akbare12/news-26-b115-numbers/reward.svg)](https://make.fun/bounty/news-image-20261126)

One image summing up Thursday 26 November 2026: **50 stories, 10 regions**.

## The three biggest stories

1. **Macy's 100th Thanksgiving Parade postponed** — the first weather
   postponement in the parade's 100-year history. A nor'easter grounded
   the balloons with gusts up to 60 mph and a high wind warning for New
   York City from 10:00 Thursday; the parade moves to Saturday
   28 November, 08:30 ET. Philadelphia's parade was cancelled too. [C]
2. **IRGC claims 2 tankers hit by mines in Hormuz** — Tehran says a
   supertanker carrying 2 million barrels was among the vessels mined
   near Khasab. The claim is unverified; UKMTO confirmed a projectile
   blast 50 nm west of Dubai with the crew safe. [CL]
3. **Trump tariffs: markets rebound** — STOXX 600 +1.6% and MSCI +0.4%
   as traders judge the 14-partner salvo (China 20%, EU 15%) not as bad
   as feared; the levies would not stack on July rates. [C]

## Layout (V111)

Masthead → hero 1 full-width with balloon art on the right → DATE CHECK
(seven stories deliberately excluded because they happened on 22–25 Nov)
→ heroes 2 and 3 in two columns → full-width world map with 10 region
dots → ten story cards in a 5×2 grid → ALSO, 37 more stories in three
columns → hour-by-hour timeline → footer with sources.

Every card and every ALSO item carries a literal tag: [C] confirmed,
[R] reported, [CL] claim.

## How it is built

- `gen.py` renders `entry.png` (1024×1024, under 1 MiB) with Pillow at
  build time. It asserts its own layout: text stays inside its box with
  no word dropped, map dots sit on land (point-in-polygon), dots are at
  least 18 px apart, labels are at least 9 px with no overlap, the map
  header is drawn after the polygons, and the timeline fits.
- `main.py` is standard-library only: it copies `entry.png` into
  `MAKEFUN_OUTPUT_DIR`. Run it with `python3 main.py`.

## Sources

Reuters, AP, BBC, CNN, UKMTO, ONS, KCNA, FCC. All facts were checked
against live reporting for 26 November 2026. Stories from 22–25 November
(COP31, Shenzhou-24, the Cairo tanker fire, the Cartagena hostages, the
Australia–Solomon pact, UK energy prices, the Huawei verdict) appear only
in the DATE CHECK strip, never as 26 November news.
