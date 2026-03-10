---
description: Synthesize all data and generate creative briefs for ad production
---

# Creative Strategist Agent

Workflow for combining insights from Agents 1-3 and generating actionable creative briefs.

## Usage

Provide outputs from all previous agents:
- Design Analysis: `outputs/analysis/design_[timestamp].json`
- Marketing Analysis: `outputs/analysis/marketing_[timestamp].json`
- Competitor Intel: `outputs/competitor_intel/data_[timestamp].json`

## Workflow Steps

### Step 1: Load and Review Input Data

```
Load three data files:

1. **Design Analysis** (Agent 1):
   - Brand colors: [list hex codes]
   - Typography: [heading font, body font]
   - Visual style: [description]
   - Quiz flow: [number of screens]

2. **Marketing Analysis** (Agent 2):
   - Audiences: [count segments]
   - Value Props: [count VPs]
   - Pain Points: [list top 5]
   - Offers: [list offers]

3. **Competitor Intel** (Agent 3):
   - Winning creatives: [count]
   - Top hook types: [distribution]
   - Top visual styles: [distribution]
   - Reference ads: [list top performers]

Confirm all data loaded successfully.
```

### Step 2: Build Opportunity Matrix

Create combinations and score them:

```
For EACH audience segment:
  For EACH value proposition:
    For EACH winning hook type (from competitor data):
    
      Calculate opportunity score:
      
      1. Audience Size Factor (1-4 points):
         - Large market: 4 points
         - Medium market: 3 points
         - Small/niche: 2 points
         - Micro: 1 point
      
      2. Competitor Saturation (1-3 points):
         - Low saturation (gap): 3 points
         - Medium saturation: 2 points
         - High saturation: 1 point
      
      3. Hook Effectiveness (1-3 points):
         - Proven winner (>40% of competitors): 3 points
         - Moderate success (20-40%): 2 points
         - Low usage (<20%): 1 point
      
      4. Brand Fit (0-2 points):
         - Perfect alignment: 2 points
         - Good fit: 1 point
         - Stretch/off-brand: 0 points
      
      Total Score: Sum of above (1-12 points)
      
      Record:
      {
        "audience": "segment_id",
        "vp": "vp_id",
        "hook_type": "pain",
        "score": 10,
        "reasoning": "Large audience + proven hook + low saturation"
      }

Sort opportunities by score (descending).
Select top 5 for brief generation.
```

### Step 3: Select Concepts

From opportunity matrix, select briefs to create:

```
Selection criteria:

1. **Must include**: Top 3 highest scores (8-12 points)

2. **Diversity requirements**:
   - At least 2 different audience segments
   - At least 2 different hook types
   - Mix of proven approaches + gap opportunities

3. **Priority assignment**:
   - Score 10-12: High priority
   - Score 7-9: Medium priority
   - Score 4-6: Low priority

Output: List of 3-5 concepts to develop into full briefs
```

### Step 4: Generate Creative Briefs

For EACH selected concept:

```
Create detailed creative brief:

**1. Brief Header**
---
Brief ID: brief_001
Concept Name: [Descriptive, e.g., "Pain Amplifier - Delivery Apps"]
Priority: High | Medium | Low
Target Audience: [Segment name from Agent 2]
Value Proposition: [VP headline from Agent 2]
---

**2. Strategic Context**

Why this concept:
- Audience insight: [From Agent 2]
- Competitor evidence: [From Agent 3]
- Brand alignment: [From Agent 1]

**3. Creative Direction**

**Hook** (First impression - 5-10 words):

Template based on hook type:
- Pain: "{Tired of/Struggling with/Frustrated by} {pain point}?"
- Benefit: "{Get/Achieve} {outcome} in {timeframe}"
- Curiosity: "{The secret to/How to/Discover} {benefit}"
- Social Proof: "{X users/customers} trust us for {benefit}"
- Urgency: "{Limited time/Only X spots} {offer}"

Example: "Losing customers to DoorDash?"

**Body** (Value prop + proof - 15-25 words):

Structure: Problem → Solution → Proof
- Problem: [From pain points]
- Solution: [From VP]
- Proof: [From social proof/data]

Example: "Turn one-time diners into loyal regulars with automated SMS loyalty. 10,000+ restaurants increased repeat visits by 25%."

**CTA** (Clear action - 3-5 words):

Based on offer type:
- Trial: "Start Free Trial →"
- Lead magnet: "Get Free Guide →"
- Webinar: "Save Your Spot →"
- Quiz: "Take the Quiz →"
- Demo: "Schedule Demo →"

Example: "Start Free Trial →"

**Visual Concept** (Design approach):

Based on winning visual styles from Agent 3:
- testimonial: "Customer photo with quote overlay"
- before_after: "Split screen showing transformation"
- stat_callout: "Large number with supporting visual"
- problem_solution: "Problem on left, solution on right"
- ugc_style: "Casual, phone-shot aesthetic"

Include specific imagery:
- [Image 1: description]
- [Image 2: description]
- [Image 3: description]

**Color Scheme**:

Use brand colors from Agent 1:
- Primary: [Hex from brand palette]
- Secondary: [Hex from brand palette]
- CTA/Accent: [Contrasting color for button]

Ensure WCAG AA contrast compliance.

**Typography**:

Style based on brand (Agent 1) + creative tone:
- bold: Large, impactful headlines (pain/urgency)
- elegant: Sophisticated serif (premium positioning)
- playful: Rounded, friendly (approachable brand)

**4. Variations (A/B/C Testing)**

Create 3 hook variations:

Variant A (Proven):
- Hook: [Most proven pattern from competitor data]
- Reasoning: "Used by 40% of winning ads, highest safety"

Variant B (Alternative):
- Hook: [Different angle on same pain/benefit]
- Reasoning: "Tests alternative framing, moderate risk"

Variant C (Experimental):
- Hook: [Unique angle or underutilized pattern]
- Reasoning: "Gap opportunity, higher risk but potential upside"

**5. References**

Competitor ads to reference:
- Ad ID: [From Agent 3]
- What to learn: "Effective use of testimonial visual"

- Ad ID: [From Agent 3]
- What to learn: "Strong pain-based hook resonance"

**6. Technical Specs**

Format: static (images)
Dimensions:
- 1080x1080 (Square - Feed)
- 1080x1920 (Vertical - Stories)
- (Optional) 1200x628 (Landscape - Link ads)

```

### Step 5: Validate Briefs

Check each brief:

```
For EACH brief:

✅ Required elements present:
   - Concept name
   - Target audience (from Agent 2)
   - Value proposition (from Agent 2)
   - Hook, body, CTA
   - Visual concept
   - Color scheme (from Agent 1)
   - 3 variations

✅ Data-backed decisions:
   - Hook type from winning patterns (Agent 3)
   - Visual style from competitor analysis (Agent 3)
   - Audience/VP from marketing research (Agent 2)
   - Brand colors from design analysis (Agent 1)

✅ Testability:
   - Clear hypothesis for each variation
   - Measurable differences between A/B/C

If validation fails, revise brief and re-check.
```

### Step 6: Generate Outputs

Create comprehensive output files:

```
1. **Individual Brief Files**
   For each brief, save separate JSON:
   File: outputs/briefs/brief_001.json
   
   {
     "id": "brief_001",
     "concept_name": "...",
     "priority": "high",
     ... [full brief]
   }

2. **Master Briefs File**
   File: outputs/briefs/creative_briefs_[timestamp].json
   
   {
     "metadata": {
       "generated_at": "[ISO timestamp]",
       "total_briefs": 5,
       "input_sources": {
         "design": "outputs/analysis/design_*.json",
         "marketing": "outputs/analysis/marketing_*.json",
         "competitor": "outputs/competitor_intel/data_*.json"
       }
     },
     "opportunity_matrix": [
       {
         "audience": "...",
         "vp": "...",
         "hook": "...",
         "score": 10
       },
       ... top 10 opportunities
     ],
     "creative_briefs": [
       ... all 3-5 briefs
     ]
   }

3. **Summary Markdown**
   File: outputs/briefs/creative_briefs_[timestamp]_summary.md
   
---
# Creative Strategy Summary
Date: [timestamp]
Total Briefs: 5

## Data Sources
- Design: Boomerang quiz funnel (6 screens, orange/navy palette)
- Marketing: 2 audiences, 2 VPs, 5 pain points
- Competitors: 20 winning ads analyzed, pain hooks dominant

## Opportunity Matrix (Top 10)

| Rank | Audience | VP | Hook | Score | Reasoning |
|------|----------|----|----|-------|-----------|
| 1 | Indie Restaurants | VP1 | Pain | 11 | Large market + proven hook + gap |
| ... |

## Creative Briefs

### Brief 1: Pain Amplifier - Delivery Apps (Priority: High)

**Target**: Independent Restaurant Owners
**VP**: Turn one-time diners into regulars
**Hook Type**: Pain-based (proven in 40% of winners)

**Creative Direction**:
- Hook: "Losing customers to DoorDash?"
- Body: "Turn one-time diners into loyal regulars..."
- CTA: "Start Free Trial →"
- Visual: Split screen (frustrated owner vs. returning customer)
- Colors: #FF6B35, #004E89, #28A745

**Variations**:
- A: "Losing customers to delivery apps?" (proven)
- B: "Tired of customers who never come back?" (emotional)
- C: "What if every customer returned 3x more often?" (benefit-curiosity)

**References**: Ads #123456, #789012 (testimonial style)

---

[Repeat for each brief]

## Testing Recommendation
1. Launch Brief 1 & 2 (High priority) first
2. Test all variations simultaneously
3. Measure CTR, CPL, conversion
4. Scale winners, iterate losers
---

4. **Create reference board** (optional):
   File: outputs/briefs/references/
   Copy top competitor ad images for easy reference
```

## Expected Output

### Brief Structure Example
```json
{
  "id": "brief_001",
  "concept_name": "Pain Amplifier - Delivery App Competition",
  "target_audience": "independent_restaurant_owners",
  "value_proposition": "vp_1",
  "priority": "high",
  "format": "static",
  "dimensions": ["1080x1080", "1080x1920"],
  "creative_direction": {
    "hook": "Losing customers to DoorDash?",
    "body": "Turn one-time diners into loyal regulars with automated digital loyalty. 10,000+ restaurants increased repeat visits by 25%.",
    "cta": "Start Free Trial →",
    "visual_concept": "Split screen: frustrated restaurant owner on left, happy returning customer on right",
    "color_scheme": ["#FF6B35", "#004E89", "#28A745"],
    "typography_style": "bold",
    "imagery": [
      "restaurant_owner_looking_concerned",
      "smartphone_showing_loyalty_card",
      "customer_walking_into_restaurant_smiling"
    ]
  },
  "variations": [
    {
      "variant": "A",
      "hook_variation": "Losing customers to delivery apps?",
      "reasoning": "Direct pain point, question format (proven pattern)"
    },
    {
      "variant": "B",
      "hook_variation": "Tired of customers who never come back?",
      "reasoning": "Emotional pain amplification, broader scope"
    },
    {
      "variant": "C",
      "hook_variation": "What if every customer returned 3x more often?",
      "reasoning": "Benefit-curiosity hybrid, gap opportunity"
    }
  ],
  "reference_creatives": ["ad_123456", "ad_789012"],
  "reasoning": "Targets largest segment (indie restaurants), uses #1 VP (customer retention), leverages proven pain-based hook (40% of winning ads), addresses specific competitor (DoorDash) from pain points"
}
```

## Output Location

```
outputs/briefs/
├── brief_001.json
├── brief_002.json
├── brief_003.json
├── creative_briefs_[timestamp].json     # Master file
├── creative_briefs_[timestamp]_summary.md
└── references/                           # Competitor ad images
    ├── ad_123456.jpg
    └── ad_789012.jpg
```
