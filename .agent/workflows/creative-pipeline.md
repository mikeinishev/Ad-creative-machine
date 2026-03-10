---
description: Run the complete creative production pipeline from design analysis to final creatives
---

# Creative Pipeline Workflow

This workflow runs all 5 agents in sequence to produce ad creatives from a quiz funnel design.

## Prerequisites
- Figma access token (for Figma designs)
- Apify token (for competitor research)
- Landing page URL

## Steps

### 1. Design Analysis (Agent 1)
**Input**: Figma URL, PDF, or landing page URL
**Output**: `outputs/analysis/design_[timestamp].json`

```
Analyze the design at [INPUT_URL/FILE]:
1. Identify all quiz screens (welcome, questions, results, offer)
2. Extract headlines, CTAs, and visual elements
3. Map the user flow
4. Extract brand colors and typography
5. Save structured output to outputs/analysis/
```

### 2. Marketing Analysis (Agent 2)
**Input**: Landing page URL + Design analysis
**Output**: `outputs/analysis/marketing_[timestamp].json`

```
Analyze the landing page at [URL]:
1. Extract all headlines and copy
2. Identify pain points and benefits mentioned
3. Define 2-3 audience segments
4. Extract 2-3 value propositions
5. Analyze the offer structure
6. Save structured output to outputs/analysis/
```

### 3. Competitor Research (Agent 3)
**Input**: Value propositions from Agent 2
**Output**: `outputs/competitor_intel/`

```
For each value proposition:
1. Generate 2-3 search queries
2. Search Meta Ads Library (US, CA)
3. Filter for niche relevance
4. Score by duration (>14 days = winning)
5. Download top 20 creatives per query
6. Analyze patterns (hooks, styles, CTAs)
7. Generate competitor report
```

// turbo
### 4. Creative Strategy (Agent 4)
**Input**: All previous agent outputs
**Output**: `outputs/briefs/`

```
Synthesize all data:
1. Build opportunity matrix (audience × VP × competitor gap)
2. Prioritize top 5 creative concepts
3. For each concept, create detailed brief:
   - Hook (3 variations: A/B/C)
   - Body copy
   - CTA
   - Visual direction
   - Color scheme
   - Reference creatives
4. Save briefs as JSON files
```

### 5. Creative Design (Agent 5)
**Input**: Creative briefs from Agent 4
**Output**: `outputs/creatives/`

```
For each brief:
1. Generate base creative for each variation (A/B/C)
2. Create formats:
   - 1080x1080 (Feed)
   - 1080x1920 (Stories)
3. Save with metadata
4. Create visual summary
```

## Quick Run

To run the full pipeline:
```bash
# Set environment variables
export FIGMA_ACCESS_TOKEN="your_token"
export APIFY_TOKEN="your_token"

# Provide inputs
DESIGN_INPUT="https://figma.com/file/..."
LANDING_URL="https://example.com/quiz"

# Run each agent in sequence (manually for now)
```

## Output Structure

```
outputs/
├── analysis/
│   ├── design_20240115.json
│   └── marketing_20240115.json
├── competitor_intel/
│   ├── creatives/
│   ├── report_20240115.md
│   └── data_20240115.json
├── briefs/
│   ├── brief_001.json
│   ├── brief_002.json
│   └── summary.md
└── creatives/
    ├── brief_001/
    │   ├── variant_A/
    │   ├── variant_B/
    │   └── metadata.json
    └── brief_002/
        └── ...
```
