# UGC director — session-model workflow

Use this route for owner-style product demonstration ads with optional post captions
and real UI inserts. The legacy `video_storyboard` / Veo renderer remains separate.

```sh
# Build the full context bundle; the session model then authors the structured pack.
python3 agents/ugc_director/prepare.py SOURCE.json --out OUTPUT_DIRECTORY
# Validate the authored pack and build a local review page.
python3 agents/ugc_director/prepare.py OUTPUT_DIRECTORY/scripts.json --validate --out OUTPUT_DIRECTORY
# Reproduce the October 24 source-winner treatment (no API or image calls).
python3 agents/ugc_director/winners_20261024.py --source OLD_PACK/scripts.json --out NEW_PACK
```

Read `AGENT_PROMPT.md` and `shared/UGC_VIDEO_PLAYBOOK.md` before authoring. The source
file for the dated treatment is the eight-ID dictionary from the original Seedance
pack. Generated files are artifacts in `outputs/`, not committed source.

The validator checks timeline continuity, clip limits, dialogue density, required
scene fields, duplicate IDs, hooks and prohibited five-restaurant recruitment.
It does **not** certify factual claims, translated fluency, visual quality, audio
accuracy, platform compliance or conversion. Those need explicit human/model QA
and actual acquisition tests. Rendering the review page does not generate footage.

Place six-scene visual sheets at `boards/<source_id>.png`. Layout may be 3×2 or 2×3;
numbered panels, not CSS position, determine scene identity. Pilot start frames live
at `start_frames/<clip_id>.png`. Keep source images and generation receipts.

Generation: user-authorized Higgsfield web UI, Seedance 2.0, 720p, 9:16, native voice,
up to 15s per clip. Recheck **Generate Unlimited** after every setting or media change.
If the media picker fails, inspect page errors and refresh the same user-selected
browser; do not silently switch to billed API/CLI generation.

Pilot learning: Audio On must be verified visually and the downloaded file must contain an audio stream. Rerun plus a spinner is not a completed asset. For local multilingual captions, whisper.cpp CPU DTW (-nfa -ng) can improve alignment; inspect the result. Use explicit font-family with sans-serif fallback and inspect decoded frames, since a successful layout check can miss font substitution. Preserve source creative IDs as provenance; allocate a fresh global creative ID for the rendered adaptation.


## Hook production continuation (2026-10-25)
Canonical authored scripts, references and progress: primary checkout `outputs/storyboards/2026.10.25_ugc_hooks_v3/`. Do not overwrite these by blindly rerunning the initial authoring script.

All new ads except pilot181 use two native voiced15s Seedance2.0 clips. Production happens through the authenticated side browser with Generate Unlimited,720p,9:16,audioOn. Confirm a new history card before considering a job submitted. Wait for its playable video; disappearing Cancel alone is not completion. Download using browser media controls.

Inspect table-tent fidelity and actor continuity, decode and transcribe each clip with `process_take.py`. Build captions and composition in the dedicated worktree project; inspect snapshots and check then render. After visual and transcript review, `pack_video.py <project> --source <id> --product getreviews|customers100 --accent <hook_market> --language <locale> --visual-reviewed --transcript-reviewed` allocates the next global ID, copies the MP4 and editable project, updates manifests and refreshes the delivery index. Never use the review flags to imply native-speaker listening.

## Current acceptance contract
Read `shared/UGC_PRODUCTION_LEARNINGS.md`. New storyboards must provide `production_contract` for each creative; default validation rejects missing hooks, late payoffs, mismatched/unaccepted native voice references, synthetic guides, missing review gates, music or demo labels. `--legacy` is only for inspecting historical packs and does not certify release. This is instruction/workflow training, not model-weight fine-tuning. Hook216 is user-preferred, not a measured conversion winner.
