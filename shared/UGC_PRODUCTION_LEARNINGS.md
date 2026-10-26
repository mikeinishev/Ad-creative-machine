# UGC production acceptance contract — user review, 2026-10-25

Read this before briefs, storyboards, reference images, generation and final packing.
This is a reusable directing policy, not model fine-tuning or proof of conversion.

## Mandatory visual hook for every video

Each creative must select one opening hook; merely listing alternatives is insufficient.
Action is already underway at 0 seconds, its visible payoff happens by 2 seconds,
and the next spoken beat bridges that action to the owner's specific problem.
The opening must make sense with sound off. No logo intro, generic greeting or
static talking portrait. Write three distinct alternatives, rotate mechanisms
across a pack, and vary the execution rather than inserting the same gag everywhere.
For static creatives, depict one legible visual tension and one concise headline;
do not simulate a whole sequence in a cluttered image.

### Priority reference: final216 / source182, Brazilian GetReviews

Mike explicitly selected this as his favorite: dropping/catching a plate, physical
surprise/reversal and a comic line. Preserve the actual original clip as the visual
reference. His recollection «Брат, убегай» is feedback, not a verified transcript.
Reusable mechanism: immediate physical mishap → quick reaction → owner looks at
camera → product-relevant contrast. Example GetReviews bridge: “Caught the plate.
Forgot the review.” For 100+, tie the interruption to an empty seat or local demand,
not an unrelated slapstick sequence. A single feasible action is easier to render
than choreographing a fall, flip and several collisions. Keep spontaneous humor,
ordinary phone filming and causal continuity. Do not claim this hook is a measured
conversion winner: it is user-preferred, with conversion testing still required.

Other approved mechanisms: catch a tipping phone; chase a departing guest; serve
an empty chair; look under a table for guests; contrast a guest's praise with the
owner's phone; open the door and reveal an empty dining room. Every choice needs
a product-specific bridge, physical feasibility and a distinct first frame.

## Product and claim integrity

- ONE restaurant in every language and all recruitment copy, captions and CTAs.
- Demonstration from an owner's perspective, not fabricated customer testimony.
  Before/after means changed workflow unless verified results are supplied.
- Use current funnel terms and real captured product UI. No invented review count,
  ratings, revenue, guarantees, or customers materializing after connection.
- Never add on-screen recreation/demo labels. Keep provenance internal.
- Every product-bearing reference uses the actual localized complete landscape
  table-tent artwork: wheel left, headline/CTA/QR right, original photos/symbols,
  clear acrylic edges/base/reflections. No cartoon icons replacing food photos,
  wheel-only portrait cards or reinterpreted print. Pilot209/source181 is the
  quality reference. Supply a separate product photo when the action frame lacks it.

## Voice continuity and talking performance

- No music. Native speech and modest room ambience; natural skin and ordinary light.
- Establish a short voice sample before a batch. Record who accepted its timbre.
  Reuse accepted native audio from the SAME actor for identity/timbre continuity.
- Never guide a male actor with a female TTS voice. A “male voice” prompt did not
  prevent female timbre transfer in217/218. Synthetic guides also produced the
  different/robotic final voice in216. Avoid synthetic guides for final UGC.
- Separate voice identity from exact words: a timbre reference must not cause
  repetition of its dialogue. Short local-language clauses, breaths, natural pace.
  Correct malformed words in audio; captions must not conceal wrong pronunciation.
- The visible speaker must actually speak: synchronized lips/jaw, natural gestures
  and purposeful movement. A still image with narration fails talking-owner QA
  (user rejected219). Review moving playback, not only contact sheets.
- Review all joins AND the full ending for speaker changes, robotic cadence,
  truncation, pauses, level jumps and mouth synchronization. Loudness normalization
  cannot fix a different speaker. ASR agreement cannot establish naturalness.
- If audio cannot be heard in-session, record listening as unverified and request
  a short listening check; never infer acceptance from pitch or transcription.

## Surgical correction and delivery

Preserve original accepted visuals and favorite hooks byte-for-byte before repair.
For216, retain the video and replace only defective ending audio; verify timing
against the preserved lip movements. Do not silently replace the approved picture.
Retain rejected takes. Never freeze-pad to hit an arbitrary length. Update actual
captions, timings and final transcript after edits. New exports receive fresh
monotonic creative IDs; original IDs are permanent. Technical export success,
visual approval, voice approval and performance acceptance are separate statuses.

Use only authorized Seedance2.0 web Generate Unlimited, Audio On, checked after
settings/media changes. Save settings/receipt; match a history job before retrying.
No paid API fallback. Every new storyboard carries `production_contract` below;
Never use the history **Rerun** control for a free-only task: it can immediately
submit a credit-priced repeat even when the original job was Unlimited. Verify
the current draft has Unlimited enabled and effective cost zero immediately before
submission. A model's UNLIMITED badge alone is insufficient. Where Higgsfield's
WebMCP submission opens a user-only approval dialog, leave that confirmation to
the user; do not bypass it through another submission path. On an accidental
paid submission, cancel immediately, report the incident, and distinguish confirmed
cancellation from an unverified credit refund.
`prepare.py --validate` enforces its presence and objective timing/identity fields.
Semantic fidelity, natural speech and conversion still require real review/testing.

```json
{
  "production_contract": {
    "hook": {
      "variant": "A",
      "mechanism": "plate_catch",
      "starts_at": 0,
      "payoff_by": 2,
      "bridge": "Caught the plate; forgot to ask for the review.",
      "evidence": "user_preferred_216"
    },
    "voice": {
      "speaker_id": "owner_br_182",
      "actor_voice": "male",
      "reference_voice": "male",
      "reference_kind": "approved_native",
      "reference": "path-to-approved-native-sample",
      "acceptance": "user_accepted",
      "dialogue_mode": "on_camera_lip_sync"
    },
    "music": false,
    "on_screen_demo_label": false,
    "recruitment_count": 1,
    "product_reference": "path-to-complete-localized-product-photo",
    "review_required": ["hook_playback", "product_fidelity", "full_audio", "speaker_continuity", "lip_sync", "ending"]
  }
}
```
For a new untested speaker use `reference_kind: native_probe`,
`reference_voice: none`, `acceptance: pending`, and `reference: pending_probe`.
This authorizes planning a test, not claiming voice acceptance or batch propagation.

## Follow-ups from the 2026-10-26 production run

- A click on Generate Unlimited is not a job receipt. Require a new history card
  with the matching prompt and duration. If no matching card appears, inspect
  current history before retrying. A normal page reload can restore a stale form,
  but it also resets Unlimited to OFF: enable it again and verify effective cost
  zero. Do not restart an existing job because its spinner or observation timed out.
- Inspect the frames around every phone turn. A prompt requesting an unreadable
  screen can still produce a visible synthetic interface. Replace that visual
  interval with a genuine captured screen while preserving native speech, or
  regenerate the shot with the display out of view. Do not present a generated
  review, map, dashboard or result as the product.
- Repeated ASR disagreement or an unexpected verb form calls for review, not an
  automatic corrected subtitle. When a line remains unclear, simplify the spoken
  wording without changing its meaning and regenerate the take. Do not globally
  ban a word on the basis of one model's transcription.
- A localized product reference may exist inside an earlier static creative even
  when a dedicated plate is missing. Use only its product artwork as reference;
  do not inherit old advertising overlays, recruitment counts or result claims.
  Inspect the full acrylic base, food photographs, main print and edge margins.
- When the user explicitly requests autonomous continuation without review stops,
  keep listening and subjective voice acceptance marked unverified and continue
  authorized production. That instruction does not turn a new voice into an
  accepted voice, authorize a paid route, or remove an actual browser approval gate.

### Confirmed free concurrency · 2026-10-26
Higgsfield displayed the explicit rate-limit notice: only one Unlimited video/image/audio generation at a time. Preparing a second draft is allowed, but clicking while another is active does not enqueue it. Wait for the matching existing job, then submit the prepared next take after checking effective0 credits. Never switch to credit-based generation to raise concurrency. A missing receipt is not a second running job.

### Native speech and physical prop QA · 227, 2026-10-26
The first closing take pronounced the conditional as si quieran (both local ASR models agreed) and laid the acrylic stand flat while removing a receipt. Reject the take; do not conceal malformed speech with corrected captions. A revised native take used the simpler explicit sentence Opinar en Google es opcional and kept hands clear of the secured upright stand; both ASR models matched all words and the full motion sheet retained the upright prop. Check the complete action interval, not only poster frames. Keep the old source/QA. Trim quiet gaps only with word handles and visible action continuity. Gain-only level matching preserves native voice; it does not prove timbre continuity or human listening approval.

### Short phone turns can evade sparse review · 228–229, 2026-10-27
A1fps sheet missed a synthetic phone screen exposed for roughly half a second at the start
of228body. A snapshot found it. For every pickup, rotation, placement or camera-facing phone
movement, inspect a dense local interval at8–10fps in addition to whole-take motion sheets.
Source228's first16bodyframes were reframed to a moving close-up of the real plate/forearm
from that same take, with all native speech retained. The first scale2 crop still exposed
the screen edge and was rejected; a tighter plate crop passed proof frames and final decoded
motion review. This treatment is only valid when the crop fully excludes the fake interface,
preserves an intelligible action, and does not hide a needed product demonstration.
Otherwise use a genuine source-captured product insert or regenerate. Keep the face out of
such speech-over-B-roll crops, do not invent a phone back or UI, and inspect the return cut.
Source229body's pickup was reviewed at8fps and stayed back-facing. No subjective voice
approval follows from these visual checks.

### Describe only props actually visible in a take · 230, 2026-10-27
The first phone/sticky-note hook230 had exact speech in both ASR models, but generated two
unrelated printed wheel/sign props and cropped the top of the owner’s head in its first
second. The input reference had no tent. The shared prompt still described the complete
product “whenever present”; remove that product paragraph entirely from a product-free hook.
Specify only the actual phone/notes, full head and hands, and fixed framing. Preserve the
rejected take; regenerate rather than covering an incorrect product with captions. A
matching transcript never overrides failed visual fidelity.

### Check country identity in the product artwork · PE, 2026-10-27
The older product_PE reference incorrectly copied Colombian Doña Rosa Arepería from178.
Peru’s existing localized product is El Muelle Cevichería from static180: blue landscape
insert, ceviche and purple chicha photographs, original prize wheel left, headline/CTA/QR
right and complete acrylic base. Use only the product from that old static ad; never copy
its five-restaurant,10X,star or footer overlays. Correct reference and production
plans238/239/262/263 before generation. Existing raster storyboards are not silently
corrected by changing a reference file; flag them for refresh. Keep the mistaken reference
archived, not active.

### Provenance stays internal
Legacy generators must not reintroduce on-screen production labels. Store provenance as
internal metadata and retain a claim/evidence ledger; the validator must not require a
display-label field. The current production contract still requires
on_screen_demo_label=false. Removing a display label never authorizes fabricated customer
outcomes or unsupported claims.

### Inspect readable print and design the shot around it · 230
Both230body and first closing had correct main brand/headline/QR layout but corrupted small
printed prize labels when the model moved into a close-up. Wide contact sheets alone missed
how readable the nonsense became. Inspect full-resolution frames whenever a stand approaches
camera. Exclude a corrupted close-up even if speech passes ASR. The revised closing uses a
fixed medium shot with the entire face visible, the stand stationary, no
lifting/sliding/finger tracing and no product-only cutaway; it also carries the short brand
line, so the earlier late body close-up can be removed completely. This is a reshoot
strategy, not proof that the revised shot has passed; inspect its actual result before
release.

### Keep short hook speech concurrent with the action
230hookv2 preserved the visual action and exact words, but DTW placed its eight-word line
around2.2–3.8seconds in a4second clip. Keep the first-second paper action unobscured and
begin its captions at actual speech. For new longer hook lines, explicitly ask speech to
begin within0.3seconds while the practical action happens, rather than after a silent two-
second action. Otherwise extend the take or shorten the line; never fix rushed speech with
an unverified synthetic replacement. Planning word counts do not prove the actual delivery
timing.

### Brand pronunciation and whole-sentence editorial cuts · 230
Closing230v2 held the medium framing, but both local ASR models recognized its opening
brand as Get Reports. Do not burn GetReviews over that spoken phrase as if it were an
accurate subtitle. The whole opening sentence was removed with a checked word handle;
both models independently matched the remaining mechanism, optional-review condition and
CTA. The product remains visible and a separate accurate GetReviews title identifies it.
A whole-sentence cut is valid only when the remaining story is coherent and still
contains the required product mechanism and CTA. It does not justify removing an essential
offer or changing the meaning. Verify the actual trimmed audio, every seam and final tail.
For subsequent brand speech, supply a pronunciation hint and inspect the result; a hint
is not evidence of correct pronunciation.

### Reconcile an unchanged history card before a long wait · 231
Repeated live AX reads showed Cancel/spinner for231hook; one normal page reload then
showed the completed asset. Its actual completion time is unknown. After several minutes
of an unchanged history card, preserve the next draft prompt/reference/duration and
reconcile with one normal reload before extending the wait. Never restart an unknown job.
After reload, Unlimited may be OFF: restore it and verify effective zero credits again
before any new submission. A configured Start slot also does not prove pixel-locked
framing:231 kept the identity/venue/props but rendered a wider view. Inspect actual output.

### Assets can resolve an ambiguous creation-history spinner · 231
Even after reload, the creation page showed a spinner without an accessible asset or
Cancel control for231body. The regular Assets library search by its distinctive prompt
found a playable11second result. Opening Info confirmed the exact prompt, input image,
720x1280 size and creation time; the normal Download button saved the original. Use this
read-only fallback before concluding that a job is stalled or restarting it. A search
thumbnail alone is insufficient: match the opened asset metadata and downloaded file.
Keep only one active Unlimited generation and never use history Rerun to retry.

### Apply product framing constraints to body shots as well as endings
231body pronounced GetReviews correctly in both ASR models, but its permissive handheld
camera instruction produced a push-in and readable invented prize labels. Fix framing
in every product-bearing take, not only the CTA. Keep the owner upright behind a stable
stand, full head and hands visible, no leaning/push-in/lifting/sliding. Inspect actual
print at full resolution before selecting the take. The231bodyv2 reshoot is a plan,
not a passed take until downloaded and reviewed.

### MX reference correction
Both older product_MX references still contained the English Philly example. Active MX
references now use the complete Spanish El Comal Taquería prop already used by226–227
and prepared250. Preserve the old English reference in an archive, and label historical
raster boards that still show it; updating a reference does not update old boards. For
local251 use its own actor identity with the correct El Comal product, not the older
English card or the male product-reference model.

### A face reframe can preserve a complete product story · 231
The original231body had exact native speech including GetReviews in both ASR models,
but an unwanted product push-in. Its whole head remained inside a360x640 crop at180,0.
A2x digital reframe excluded the corrupted printed prop completely while retaining the
owner's moving lips and native speech.4fps whole-source review verified the head/cap
throughout; an idle first second was removed and both models matched the trimmed speech.
The final keeps the COMPLETE physical product and optional-review mechanism in the
separate closing, so the demonstration was not lost. All15 composition snapshots,
whole-final motion, first/last frames and both whole-final transcripts were checked.
Use this only when the full face survives, the reframed resolution is acceptable and
the required product/action proof is genuinely present elsewhere. Never crop away a
required demonstration, hide malformed words, fake a product or replace the native voice.
Retain the uncropped source and record the digital reframe; do not claim native uncropped
resolution. A later steadier body take was kept as an unused alternative, not called
a rejected voice: editorial framing variety was the reason for selecting the face shot.
