# Meta Ads Creative Spec — sizes by placement (2026)

Single human-readable reference for the creative sizes Agent 5 produces.
The machine-readable source of truth is [`agents/designer/meta_placements.py`](../agents/designer/meta_placements.py).

## Why two sizes per placement

We generate with **OpenAI `gpt-image-2`**, whose `size` must have **both dimensions divisible
by 16** (longest edge ≤ 3840). Meta's canonical 1080-based sizes are not divisible by 16, so we
generate at the nearest clean ÷16 size (`gen`) and **LANCZOS-downscale to Meta's exact `target`**.

## Placement table

| Placement key | Surfaces | Aspect | Meta target (upload) | gpt-image-2 gen | Notes |
|---|---|---|---|---|---|
| `feed_vertical` | Facebook Feed, Instagram Feed, Explore | 4:5 | **1080×1350** | 1088×1360 | **Recommended feed format** — more mobile screen, higher CTR |
| `feed_square` | Feed, Carousel cards, Marketplace, Search results, Messenger inbox, Right column (desktop) | 1:1 | **1080×1080** | 1088×1088 | Universal fallback. **Carousel must be 1:1** (Meta crops 4:5 → 1:1) |
| `stories_reels` | FB Stories, IG Stories, FB Reels, IG Reels | 9:16 | **1080×1920** | 1152×2048 | Full-screen. Respect safe zones (below) |
| `instream_landscape` | In-stream video, desktop/TV placements | 16:9 | **1920×1080** | 2048×1152 | Horizontal; longer/desktop content |
| `audience_network` | Audience Network native/banner, link ads | 1.91:1 | **1200×628** | 1216×640 | Standard banner/native layout |

## Stories / Reels safe zones (9:16)

Keep all critical content — **headline, logo, CTA** — inside the centre **1080×1420** area.

- **Top ~14% (~250 px)**: profile icon, username, "Sponsored" label.
- **Bottom ~20–35% (~340–670 px)**: caption, CTA button, engagement icons.

## File / quality guidance

- **Resolution**: 1080 px is fully valid; high-density displays accept up to 1440 px
  (1440×1800 vertical, 1440×1440 square).
- **Image formats**: JPG / PNG, up to 30 MB (we output optimized PNG, sRGB, < 5 MB).
- **Video**: H.264 MP4/MOV, up to 4 GB (aim < 1 GB). Reels ≤ 90 s, Stories ≤ 120 s,
  in-stream 5–15 s recommended.
- **Text-on-image**: Meta no longer hard-rejects > 20% text, but less overlay text still
  delivers better; keep it legible on mobile.

## Sources

- [Every Meta Ad Size You Need in 2026 — theoptimizer.io](https://theoptimizer.io/blog/every-meta-ad-size-you-need-in-2026-dimensions-formats-and-placements-complete-guide)
- [Meta Ad Specs 2026 — tryvizup.com](https://www.tryvizup.com/blog/meta-ad-specs-2026-every-dimension-size-you-need)
- [Meta Ads Guide — facebook.com/business/ads-guide](https://www.facebook.com/business/ads-guide)
