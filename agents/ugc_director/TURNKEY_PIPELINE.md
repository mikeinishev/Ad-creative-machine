# UGC video creative — turnkey pipeline (learned 2026-10-24 … 2026-10-30)

From "make videos like winner X for markets Y" to a reviewed, captioned 9:16 master, without
asking Mike for anything except the decisions marked **ASK**. Read `AGENT_PROMPT.md` and
`shared/UGC_PRODUCTION_LEARNINGS.md` first; this file is the operating sequence and tool
reference on top of them. Commands run from the repo root; image/edit scripts that need
Pillow run with `.venv/bin/python`. All artifacts live in `outputs/` (gitignored).

Reference implementation of every stage: the 220-pattern pack (MX/CO/CL/PE/TR × local /
same-220 actor) in the primary checkout:
`outputs/storyboards/2026.10.28_220_pattern_markets/` (scripts, casting, storyboard, TZ.md) and
`outputs/videos/2026.10.28_220_pattern_markets/` (220_mx_local on Seedance 2.0 free,
220_mx_local_sd25 on Seedance 2.5 paid, both assembled).

## 0. Inputs and decisions

- Source winner: the actual video file, its Stripe sales/spend (verify with a fresh pull, never
  from memory), market, funnel. A winner transferred to new markets is a hypothesis.
- Which funnel: a getreviews story (tent → spin → optional Google review) does not fit 100plus
  (promise of guests, client ad budget). One funnel per script; state it at the top of the TZ.
- **ASK** (one AskUserQuestion, batched): markets; casting variants (local look-alike and/or the
  same actor as the winner); funnel if ambiguous; free vs paid generation if paid is on the table.

## 1. Script pack (session model, no API)

Author `scripts.json` in the pack folder, then validate:
`python3 agents/ugc_director/prepare.py PACK/scripts.json --validate --out PACK`.

Formula that reproduced winner 220 (BR plate catch, 6 sales / ROAS 2.06 on 26–28.10):
1. Hook 0–3 s: physical mishap already underway in frame one (plate slipping off the counter),
   caught by 1.5 s, wide-eyed "phew", deadpan look at the colleague filming. Line ties the catch to
   the forgotten task: "El plato, lo salvé. La reseña… se me olvidó." Hook title "¿Y la reseña?".
2. Pain + product: busy, asking gets postponed; "look how Boomerang works" while lifting the tent.
3. Mechanism through the guest: over-shoulder, guest points phone at the QR and plays (screen away).
4. Objection: the Google review is optional ("si quiere") — the prize never depends on a review.
5. Before/after of the WORKFLOW (asked by word → the invitation stands on the table), not results.
6. CTA: "We're looking for ONE restaurant. Check if yours can take part." + CTA overlay above tent.
Two clips of 12 s (Spanish) or 13 s (Turkish, longer morphology); ~2–2.5 words/s.
Three distinct A/B/C hooks per market from local objects (glass of agua fresca, napkin dispenser,
juice, completo…), each with its own bridge line. Keep the exclusivity CTA ("solo un restaurante
por zona") as an alternative only while the landing page does not promise exclusivity.

Clip prompt structure (one block per clip; it worked on Seedance 2.0 and 2.5):
`BASE` (raw 9:16 phone UGC, natural skin, mixed light, deep focus; no beauty filter, grade, slow
motion, bokeh, added titles/subtitles, invented UI, labels or music; speech + room ambience only)
→ `CASTING` (exact look and wardrobe) → `ARCHETYPE` (personality only: mobile eyebrows, deadpan
comic timing, sly half-smile) → `VENUE` (ordinary local place, named, no flags/sombreros/tourist
props) → model/format line → `Shot n (t0–t1 s): action. Says: "line"` ×3 → `Language:` →
`REFERENCES:` (role of each attached image, in order) → `PRODUCT LOCK` (complete landscape tent,
wheel LEFT, headline/CTA/QR RIGHT, real acrylic holder, no simplified artwork).

## 2. Casting stills (local ChatGPT subscription)

`python3 agents/ugc_director/image_frames.py --from-scripts PACK/scripts.json --kind casting --out PACK/casting`
- Local look-alike = same ARCHETYPE, a DIFFERENT face. Do not pass the winner's actor frames as a
  reference: v1 of the 220 casting copied the 220 face in every market and was rejected. Describe a
  distinct local face per market (MX maroon polo + walrus moustache; CO glasses on head; CL bald +
  grey beard; PE white shirt + goatee; TR bushy moustache) and attach only the product.
- Same-actor version: attach 2 frames of the winner's actor and say "the EXACT same man".

## 3. Storyboard frames (local ChatGPT subscription)

`python3 agents/ugc_director/image_frames.py --from-scripts PACK/scripts.json --kind storyboard --out PACK/storyboard`
(key frames only for a second casting: `--scenes s01 s06`).
- Engine: `codex exec -m gpt-6-astra -c model_reasoning_effort="xhigh" -s read-only --skip-git-repo-check --json`
  with the built-in image tool and `referenced_image_paths`; the PNG is taken from
  `~/.codex/generated_images/<thread_id>/`. No API key, no API billing; uses Codex subscription quota.
  ~1–3 min per frame, 4–6 in parallel. No quality switch exists: ask for maximum detail in the prompt.
- References per frame: casting still first, product LAST, roles stated in the prompt.
- Harness gotcha: backgrounded long runs were killed (exit 143/144). Run in the foreground,
  `timeout 580` per pass, and rerun; finished frames are skipped.
- Inspect every frame (casting continuity, complete tent with QR, no invented text). Regenerate
  a bad frame by deleting it and rerunning; keep rejected images in `_rejected/`.

## 4. Production brief (TZ)

`python3 agents/ugc_director/build_tz.py PACK/scripts.json --frames storyboard --title "ТЗ: …" --intro "…"`
Russian TZ.md: common requirements table, acceptance checklist, per creative the reference images,
scene table with frames, on-screen text, A/B/C hooks and the exact clip prompts + reference files
in `<details>`. Rebuild after frames finish. Show Mike every frame inline (numbered) + links.

## 5. Generation

Default: **free** Higgsfield web UI, Seedance 2.0, Generate Unlimited, 720p, 9:16, Audio On, one job
at a time; follow the web-UI gates in `AGENT_PROMPT.md` (verify the final button says Generate
Unlimited, speaker On, matching history card, playable asset). Free generations come first
(Mike, 29.10) even though 2.5 looks better.

Paid: Seedance 2.5 via CLI, **only after Mike approves credits for named clips** (**ASK** with the
estimate). `higgsfield_render.py --estimate` → AskUserQuestion with credits and balance →
`higgsfield_render.py --approved-credits N`. 2.5 result on 220_mx_local (29.10): both transcripts
verbatim (2.0 had a repeated "mira"), one consistent owner across both clips with casting +
product attached in `omni_reference`, faithful tent, plate caught by 0.5 s. Mike: "качество лучше".
A whole 2-clip 720p video = 168 credits.

## 6. Take inspection

`python3 agents/ugc_director/inspect_take.py OUT/c01.mp4 --lang es` per clip, then LOOK at
`_contact.jpg`, `_hook.jpg`, `_layout.jpg` and compare `_asr.txt` with the script.
Reject: no audio stream; hook payoff after ~1.5 s; owner changes between shots (seen with the
same-220 casting on 2.0 — the referenced man turned into a younger man in a cap); simplified tent
or missing QR; malformed or repeated words that cannot be cut cleanly. Keep rejected takes.
`process_take.py` remains the alternative probe with a second recognizer for disputed speech.

## 7. Edit

1. `compose_edit.py edit.json --offsets` → clip start times on the master timeline.
2. Caption cues from `_words.json` (word timestamps + offset), split at sentence/comma pauses,
   ≤2 lines, the words actually spoken (normalize the brand spelling only).
3. Place each item from `_layout.jpg` + `_cuts.json`: never over the face or the tent; when a hard
   cut moves the tent, split the caption at the cut with a new `y`. On 220_mx_local_sd25: hook title
   y=420 (chest), captions 930/940 while the tent stands mid-frame, 520 while the tent is on the
   counter low, 930 on the guest shot, final shot CTA y=430 + captions y=600 above the tent.
4. `.venv/bin/python agents/ugc_director/compose_edit.py edit.json` → master MP4 (H.264 crf 18,
   24 fps, AAC 192k, faststart), SRT, `_contact.jpg`. Look at the contact sheet; fix and rerender.
No music, no demo labels, hard cuts only, natural length (24.128 s here, not padded to 30).

## 8. Report and handoff

- Show Mike: the master as a link + `open` command, the final contact sheet and clip contact sheets
  inline, numbered. State what was verified (decode, ASR vs script, visuals) and what was not
  (native-speaker listening, lip-sync by ear).
- Do not touch another session's tracker files; write `QA.json` in the clip folder
  (jobs, credits, refs, checks, limitations).
- Packing (.seq) and Meta upload only on Mike's explicit command.
- Log the outcome to project memory and gbrain (see global instructions).
