# Agent 4: Creative Strategist - Quick Start

## Purpose
Synthesize all intelligence from Agents 1-3 and generate actionable creative briefs for ad production.

## How to Use

### 1. Prepare Your Inputs

You need outputs from all previous agents:
- **Design Analysis** (Agent 1): Brand colors, typography, visual style
- **Marketing Analysis** (Agent 2): Audiences, value propositions, pain points, offers
- **Competitor Intel** (Agent 3): Winning patterns, reference creatives

### 2. Run the Workflow

Use the workflow: `/agent4-creative-strategist`

The agent will:
1. Load all data from Agents 1-3
2. Build opportunity matrix (score all combinations)
3. Select top 3-5 concepts
4. Generate full creative briefs
5. Create 3 variations (A/B/C) per brief
6. Output structured briefs + summary report

### 3. Review Output

Find your briefs in:
```
outputs/briefs/
├── individual/
│   ├── brief_001.json
│   ├── brief_002.json
│   └── brief_003.json
├── creative_briefs_[timestamp].json     # Master file
└── creative_briefs_[timestamp]_summary.md # Human-readable
```

## What You'll Get

### Creative Briefs (3-5 concepts)
Each brief contains:
- **Strategic context**: Why this concept, backed by data
- **Target audience**: Specific segment from Agent 2
- **Value proposition**: From Agent 2, proven effective
- **Creative direction**:
  - Hook (attention grabber)
  - Body (problem → solution → proof)
  - CTA (clear action)
  - Visual concept (design approach)
  - Colors (from brand palette)
  - Typography style
  - Imagery requirements
- **3 Variations**: A (proven), B (alternative), C (experimental)
- **Reference creatives**: Competitor examples
- **Priority**: High/Medium/Low based on opportunity score

### Opportunity Matrix
Ranked list of all combinations with scores:
- Audience + VP + Hook combination
- Score (1-12 points)
- Reasoning

## Understanding Opportunity Scoring

Each concept scored on 4 factors (1-12 total):

**1. Audience Size (1-4 points)**
- Large market: 4 pts
- Medium: 3 pts
- Niche: 2 pts
- Micro: 1 pt

**2. Competitor Saturation (1-3 points)**
- Low saturation (gap opportunity): 3 pts
- Medium: 2 pts
- High (crowded): 1 pt

**3. Hook Effectiveness (1-3 points)**
- Proven winner (>40% usage): 3 pts
- Moderate success: 2 pts
- Untested (<20%): 1 pt

**4. Brand Fit (0-2 points)**
- Perfect alignment: 2 pts
- Good fit: 1 pt
- Off-brand: 0 pts

**Priority Assignment:**
- Score 10-12: **High** (proven + unsaturated)
- Score 7-9: **Medium** (proven but competitive)
- Score 4-6: **Low** (experimental or saturated)

## Brief Structure Explained

### Hook (First Impression)
**Purpose**: Grab attention in 1-2 seconds

**Format by hook type:**
- Pain: "Losing customers to DoorDash?"
- Benefit: "Get 25% more repeat visits"
- Curiosity: "The secret to loyal customers"
- Social Proof: "10,000+ restaurants trust us"
- Urgency: "Limited time: First month free"

### Body (Value Communication)
**Structure**: Problem → Solution → Proof

**Example**:
"Turn one-time diners into loyal regulars with automated digital loyalty. 10,000+ restaurants increased repeat visits by 25%."

### CTA (Call to Action)
**Format**: Clear, direct, action-oriented

**By offer type:**
- Trial: "Start Free Trial →"
- Lead magnet: "Get Free Guide →"
- Webinar: "Save Your Spot →"  
- Quiz: "Take the Quiz →"
- Demo: "Schedule Demo →"

### Visual Concept
**Based on winning patterns from competitors:**
- Before/after split: Shows transformation
- Testimonial: Customer photo + quote
- Stat callout: Large number with supporting visual
- Problem/solution: Side-by-side comparison

### Variations (A/B/C Testing)

**Variant A (Proven)**: 
- Uses most common pattern
- Lowest risk
- Baseline for comparison

**Variant B (Alternative)**:
- Different angle on same concept
- Moderate risk
- Tests hypothesis

**Variant C (Experimental)**:
- Gap opportunity or unique angle
- Higher risk
- Potential upside

## Common Creative Concepts

### 1. Pain Amplifier
- Hook: Direct pain point question
- Target: Main audience segment
- Best for: Aware audience with known problem

### 2. Benefit Spotlight
- Hook: Outcome promise
- Target: Solution-seeking audience
- Best for: Competitive differentiation

### 3. Social Proof Builder
- Hook: User statistics or testimonial
- Target: Skeptical audience
- Best for: Trust building

### 4. Curiosity Driver
- Hook: "How to" or "Secret" format
- Target: Unaware audience
- Best for: Cold traffic

### 5. Urgency Creator
- Hook: Limited time or scarcity
- Target: Warm leads
- Best for: Conversion optimization

## Use Cases

### For Agent 5 (Designer)
Briefs become design instructions:
- Visual concept → Design approach
- Colors → Exact hex codes
- Typography → Font selection
- Imagery → Asset requirements
- Variations → A/B/C test creatives

### For Campaign Planning
- High priority briefs → Launch first
- Medium priority → Second wave
- Low priority → Future testing

### For Testing Strategy
- Run all variations simultaneously
- Measure: CTR, CPL, conversion rate
- Scale winners, iterate losers

## Tips for Best Results

1. **Trust the data**:
   - Briefs are backed by competitor evidence
   - Hook types proven in market
   - Audience/VP validated by research

2. **Test all variations**:
   - Don't pick favorites
   - Let data decide winners
   - Variant C might surprise you

3. **Maintain brand consistency**:
   - Colors from Agent 1 (brand palette)
   - Typography matches quiz funnel
   - Visual style aligns with brand

4. **Prioritize high-impact**:
   - Start with high-priority briefs
   - Large audience + proven hook = safer bet
   - Gap opportunities = higher upside

## Example Brief Snippet

```
Brief 001: Pain Amplifier - Delivery App Competition
Priority: High (Score: 11/12)

Target: Independent Restaurant Owners
VP: Turn one-time diners into loyal regulars

Hook: "Losing customers to DoorDash?"
Body: "Turn one-time diners into loyal regulars with automated 
       digital loyalty. 10,000+ restaurants increased repeat 
       visits by 25%."
CTA: "Start Free Trial →"

Visual: Split screen - frustrated owner left, happy returning 
        customer right

Colors: #FF6B35 (primary), #004E89 (secondary), #28A745 (CTA)

Variations:
A: "Losing customers to delivery apps?" (proven)
B: "Tired of customers who never come back?" (emotional)
C: "What if every customer returned 3x more often?" (benefit)

References: Ads #123456, #789012 (testimonial style)
```

## Next Steps

After getting creative briefs:
1. Review opportunity matrix to understand prioritization
2. Validate briefs align with brand and strategy
3. Feed high-priority briefs to Agent 5 for design
4. Plan testing strategy (which variations to run)

## Files Reference

- **Workflow**: `.agent/workflows/agent4-creative-strategist.md`
- **System Prompt**: `agents/creative_strategist/AGENT_PROMPT.md`
- **Python Utils**: `agents/creative_strategist/synthesis_utils.py`
- **Output Schema**: `shared/schemas/creative_brief.json`
