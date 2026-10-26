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
