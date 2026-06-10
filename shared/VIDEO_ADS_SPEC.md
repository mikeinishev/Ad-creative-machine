# Video Ads Spec & Playbook (2026)

Reference for **Agent 6 (Video Storyboard)**. Specs verified against official platform docs
(June 2026). Machine-readable source of truth: [`agents/video_storyboard/video_specs.py`](../agents/video_storyboard/video_specs.py).
Full research playbook: [`shared/video_ad_playbook.json`](video_ad_playbook.json).

## Platform specs (video ads)

| Platform | Placement | Aspect | Resolution | Ideal duration | Max | Container / codec |
|---|---|---|---|---|---|---|
| **TikTok** | In-Feed / Spark | 9:16 | 1080×1920 (min 540×960) | **9–15s** (24–38s completion lane); hook in 3s | ≤ 500 MB; ≤ 10 min | MP4/MOV · H.264 · ~30fps · bitrate ≥516kbps |
| **YouTube** | Shorts ad | 9:16 | 1080×1920 | **10–30s** (<60s); only first 60s plays in feed | ≤ 256 GB (≈250 MB advisory); 3 min | MP4 Fast-Start · H.264 High (HEVC ok) |
| **Meta** | Reels (FB+IG) | 9:16 | 1080×1920 (1440×2560 rec) | **15–30s** conversion (7–15s reach); hook ~1.5s | ≤ 4 GB; ~90s | MP4/MOV · H.264 |
| **Meta** | Stories | 9:16 | 1080×1920 | **6–15s** per card | ≤ 4 GB; 120s | MP4/MOV · H.264 |
| **Meta** | Feed (4:5) | 4:5 | 1080×1350 (1440×1800 rec) | 15–30s; hook ~3s | ≤ 4 GB | MP4/MOV · H.264 |
| **Meta / YouTube** | In-stream | 16:9 | 1920×1080 (min 1080×1080) | 5–15s; brand first ~5s | ≤ 4 GB / 256 GB | MP4 · H.264 |

**Cross-platform safe zone:** keep faces / burned-in text / logos / CTA inside the **central
≈900×1400 box** of a 1080×1920 canvas — clear of the **bottom ~35%** (caption/CTA/handle UI) and
the **right rail**. Always shoot native 9:16 (non-9:16 ≈ 35% lower dwell).

## Google Veo 3 (renderer — next series)

- **8 seconds max per clip** (selectable 4/6/8; 8s unlocks 1080p/4K + extension). **24 fps.**
- Resolutions: 720p (default), 1080p, 4K (1080p/4K need an 8s clip). **9:16 & 16:9 native**
  (no native 1:1 → centre-crop a master).
- **Native audio** (48kHz stereo, prompt-driven, PER clip): synced dialogue (lip-sync), `SFX:`,
  ambience, music. Dialogue in quotes, label SFX, describe ambience, request a music cue.
- Each shot prompt is **self-contained** (no memory across shots — restate character/set/style/
  audio). Lock identity with up to **3 reference images** reused across shots.
- **Never render brand text/logos in Veo** (unreliable) → all typography is a **post overlay**
  (Agent 5's layer). 15s ad ≈ 2 clips (8s+~7s); 30s ≈ 4 clips.

## Script & retention best practices (what converts in 2026)

**Hook (first 1–3s) — land by ~2.5s, 80%+ hold at 3s.** Layer 3 channels at once: a disruptive
**visual** first frame (motion / reaction / prop reveal / 0.3s flash of the result), one bold
**spoken** line (~10–14 words), and a burned-in **text** caption. Best archetypes: contrarian
claim, mistake/warning, list tease, problem/pain, self-identifying question (map the
`audience_callout` → "Restaurant owners — …"). Test 5–10 hook variants by swapping only the first 3s.

**Body — default to PAS** (Problem → Agitate → Solution): name the pain in the customer's words,
agitate the real cost 3–5s *without insulting* ("nobody told you about this"), then reveal the
product. Alternatives: BAB (before-after-bridge, good for transformation/income), Hook-Story-Offer
(founder/narrative), DR formula, founder-to-camera, testimonial/UGC, listicle/open-loop.

**Pacing:** pattern interrupt every **2–3s (TikTok) / 3–5s (Reels)**, *varied* spacing (not
metronomic); rotate angles every 5–8s; recover the mid-video dip with an interrupt at ~25–35s.
3+ native edits ≈ +84% watch time / ~2.1× conversions (TikTok). **Engineer a seamless loop** —
rewatch/replay is the most heavily weighted signal.

**Captions & sound:** design **sound-OFF first** (up to 85% muted). Burn captions (4–6 words/line,
≥2s, high-contrast) — adds 12–40% watch time. Layer sound-on (VO/SFX/ambience/music) for lift; on
Veo request audio per shot, swap trending audio in post (trend lift fades after ~7 days).

**CTA (last 3–5s):** action verb + tangible outcome + low-commitment timeframe; reinforce across
voiceover + on-screen text + a visual tap cue (cursor/finger). Pre-empt one objection (guarantee /
"cancel anytime" / "takes 30 seconds"). Keep it out of the bottom-35% UI band.

**Format:** native/UGC beats polished for DR (~1.8% vs ~1.1% CTR, ~64% lift, 20–40% lower CPI);
run ~60/40 UGC-to-polished.

## Per-platform tuning

- **TikTok** (9:16): 9–15s (or 24–38s value lane), cut every 2–3s, native/UGC founder look,
  trending audio in post, seamless loop. Most retention-demanding; completion is the #1 metric.
- **YouTube Shorts** (9:16): 10–30s, **satisfying final frame + loop** (rewards completion-to-
  last-frame + staying in feed). The auto CTA chip appears ~3s in — don't fight it.
- **Meta Reels** (9:16): 15–30s (7–15s reach lane), hook by ~1.5s, cut every 3–5s, add a
  **"save this"** prompt (saves/DM-sends per reach outweigh raw retention on Reels).

## Sources

Meta Ads Guide / Business Help Center; Google Ads & YouTube Help (Shorts ads, video specs);
TikTok Ads Manager Help; Google DeepMind / Gemini Veo 3 docs — see `shared/video_ad_playbook.json`
`sources[]` for the full cited list gathered during research.
