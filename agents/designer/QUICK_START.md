# Agent 5: Designer - Quick Start

## Purpose
Generate production-ready Meta Ads creative images from strategic briefs with A/B/C variations.

## How to Use

### 1. Prepare Your Input

You need creative briefs from Agent 4:
- **Creative Briefs**: `outputs/briefs/creative_briefs_[timestamp].json`
- Or **Individual Brief**: `outputs/briefs/individual/brief_001.json`

### 2. Run the Workflow

Use the workflow: `/agent5-designer`

The agent will:
1. Parse creative brief specifications
2. Create detailed image generation prompts
3. Generate images for all variations (A/B/C)
4. Generate both formats (square + vertical)
5. Create metadata and summary report

### 3. Review Output

Find your creatives in:
```
outputs/creatives/
├── brief_001/
│   ├── variant_A_1080x1080.png      # Feed (square)
│   ├── variant_A_1080x1920.png      # Stories (vertical)
│   ├── variant_B_1080x1080.png
│   ├── variant_B_1080x1920.png
│   ├── variant_C_1080x1080.png
│   ├── variant_C_1080x1920.png
│   └── metadata.json
└── generation_summary_[timestamp].md
```

## What You'll Get

### Per Brief: 6 Images
- **3 Variations** (A, B, C) - different hooks, same visual
- **2 Formats** each - square (Feed) + vertical (Stories)
- **Total**: 6 production-ready creatives

### Metadata
- Brief details
- Variation reasoning
- Design specifications
- File references

### Summary Report
- All briefs processed
- Total images generated
- Testing and optimization recommendations

## Understanding Ad Formats

### Square (1080x1080) - For Feed
**Best for**: Facebook Feed, Instagram Feed, Carousel ads

**Layout**:
```
┌─────────────────┐
│   Visual/Photo  │ Top 50%
│                 │
├─────────────────┤
│  HEADLINE TEXT  │ Bottom 50%
│  Body copy...   │
│  [CTA Button]   │
└─────────────────┘
```

**Guidelines**:
- Visual occupies top half
- Text on solid/gradient background (bottom half)
- CTA button at bottom, high contrast
- Readable at thumbnail size

### Vertical (1080x1920) - For Stories
**Best for**: Instagram Stories, Facebook Stories, Reels

**Layout**:
```
┌─────────────┐
│ [Safe Zone] │ ← Avoid top 250px
├─────────────┤
│   Visual    │
│             │
│  HEADLINE   │
│  Body text  │
│             │
│ [CTA Button]│
├─────────────┤
│ [Safe Zone] │ ← Avoid bottom 250px
└─────────────┘
```

**Guidelines**:
- Avoid top/bottom 250px (covered by UI)
- Larger text for mobile
- CTA in lower third (above safe zone)
- Vertical orientation photo/visual

## Design Quality Standards

### Text Readability ✅
- **High contrast**: White on dark, dark on light
- **Font sizes**:
  - Square: Hook 72-96px, Body 36-48px, CTA 42-54px
  - Vertical: Hook 96-120px, Body 48-60px, CTA 42-54px
- **Background**: Solid color or blur behind text
- **Max text**: ~20% of image area (Meta guideline)

### Brand Consistency ✅
- **Colors**: From brand palette (Agent 1)
- **Typography**: Matches brief style (bold/elegant/playful)
- **Visual style**: Aligns with brand personality

### Platform Requirements ✅
- **Dimensions**: Exact (1080×1080 or 1080×1920)
- **File size**: <5MB
- **Format**: PNG or JPG
- **Resolution**: 72 DPI (web standard)

## Variation Strategy

### Variant A (Proven)
- Uses most proven hook pattern
- Baseline for comparison
- Lowest risk

**Example**: "Losing customers to delivery apps?"

### Variant B (Alternative)
- Different angle on same concept
- Tests alternative framing
- Moderate risk

**Example**: "Tired of customers who never come back?"

### Variant C (Experimental)
- Unique or underutilized angle
- Gap opportunity
- Higher risk, potential upside

**Example**: "What if every customer returned 3x more often?"

**Testing approach**:
- Run all 3 simultaneously
- Equal budget split initially
- Measure CTR, CPL, conversion
- Scale winner after 72 hours

## Common Visual Concepts

### 1. Split Screen
- Left: Problem state (frustrated, struggling)
- Right: Solution state (happy, successful)
- **Best for**: Pain-to-solution messaging

### 2. Before/After
- Top/Left: Before (problem)
- Bottom/Right: After (result)
- **Best for**: Transformation stories

### 3. Testimonial
- Customer photo (professional)
- Quote overlay
- Results/metrics callout
- **Best for**: Social proof, trust building

### 4. Stat Callout
- Large number/percentage (main focus)
- Supporting visual
- Explanatory text
- **Best for**: Data-driven claims

### 5. Product Demo
- Product screenshot/mockup
- Highlighted features
- Clear benefit statement
- **Best for**: SaaS, app marketing

## Tips for Best Results

1. **Prioritize High-Priority Briefs**:
   - Start with score 10-12 briefs
   - Higher chance of success
   - Better ROI

2. **Generate All Variations**:
   - Don't skip A/B/C testing
   - Data decides winners
   - Variant C might surprise you

3. **Use Both Formats**:
   - Square for Feed placement
   - Vertical for Stories placement
   - Maximize reach

4. **Review Before Launch**:
   - Check text readability
   - Verify brand colors
   - Test on mobile screen
   - Ensure CTA visible

5. **Iterate if Needed**:
   - First generation might need refinement
   - Adjust prompt for better results
   - Focus on text clarity

## Launch Checklist

Before uploading to Meta Ads:

```
✅ File Quality:
   - Correct dimensions (1080×1080 or 1080×1920)
   - File size <5MB
   - High resolution, no pixelation

✅ Text Requirements:
   - <20% text coverage (check with Meta's overlay tool)
   - All text readable
   - No cutoff text

✅ Brand Compliance:
   - Colors match brand guidelines
   - Typography on-brand
   - Visual style appropriate

✅ Platform Guidelines:
   - No prohibited content
   - Safe zones respected (Stories)
   - CTA clearly visible

✅ Testing Setup:
   - All variations ready
   - Campaign structure planned
   - Success metrics defined
```

## Campaign Structure Recommendation

```
Campaign: Boomerang Quiz Funnel Ads
├── Ad Set 1: Independent Restaurants (Audience)
│   ├── Ad 1A: Brief 001 - Variant A - Square
│   ├── Ad 1A-S: Brief 001 - Variant A - Vertical
│   ├── Ad 1B: Brief 001 - Variant B - Square
│   ├── Ad 1B-S: Brief 001 - Variant B - Vertical
│   ├── Ad 1C: Brief 001 - Variant C - Square
│   └── Ad 1C-S: Brief 001 - Variant C - Vertical
```

**Budget allocation**: Equal split across variants initially

## Expected Timeline

Per brief (6 images):
- **Generation time**: ~5-10 minutes
- **Review time**: ~5 minutes
- **Iteration** (if needed): ~5 minutes

For 3 briefs (18 images total):
- **Total time**: ~30-45 minutes

## Troubleshooting

### Text Not Readable
**Solution**: Increase font size in prompt, add background blur or solid color behind text

### Colors Don't Match Brand
**Solution**: Verify hex codes in prompt, be explicit about color usage

### Visual Doesn't Match Concept
**Solution**: Add more descriptive details to visual concept in prompt

### File Size Too Large
**Solution**: Save as JPG instead of PNG, or compress image

### Text Coverage >20%
**Solution**: Reduce body text length, make headline/CTA more concise

## Next Steps

After generating creatives:
1. **Review all images** for quality and brand consistency
2. **Upload to Meta Ads Manager**
3. **Set up A/B/C test campaign**
4. **Monitor performance** (CTR, CPL, conversion)
5. **Scale winners** after 72 hours
6. **Iterate losers** with learnings

## Files Reference

- **Workflow**: `.agent/workflows/agent5-designer.md`
- **System Prompt**: `agents/designer/AGENT_PROMPT.md`
- **Output Format**: `outputs/creatives/{brief_id}/`

---

## Complete System Pipeline

**Input**: Quiz funnel design (any format)

**Agent 1**: Design Analysis → Brand assets, quiz structure

**Agent 2**: Marketing Analysis (landing page) → Audiences, VPs, offers

**Agent 3**: Competitor Intel (Meta Ads) → Winning patterns, references

**Agent 4**: Creative Strategist → 3-5 briefs with A/B/C variations

**Agent 5**: Designer → 18+ production-ready creatives

**Output**: Ready to launch Meta Ads campaign! 🚀
