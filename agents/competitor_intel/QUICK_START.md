# Agent 3: Competitor Intel - Quick Start

## Purpose
Find and analyze winning competitor ad creatives from Meta Ads Library to identify proven patterns and successful messaging angles.

## How to Use

### 1. Prepare Your Input

You need value propositions from Agent 2:
- **Marketing Analysis**: `outputs/analysis/marketing_[timestamp].json`
- Or **Manual VPs**: 2-3 value proposition statements

### 2. Run the Workflow

Use the workflow: `/agent3-competitor-intel`

The agent will:
1. Generate search queries from VPs
2. Search Meta Ads Library via Apify
3. Filter for "winning" ads (>14 days active)
4. Download top 20 creatives
5. Analyze patterns
6. Generate comprehensive report

### 3. Review Output

Find your analysis in:
```
outputs/competitor_intel/
├── creatives/
│   ├── ad_123456.jpg
│   ├── ad_789012.jpg
│   └── ...
├── data_20260209_144500.json        # Structured data
├── report_20260209_144500.md        # Human-readable report
└── metadata_20260209_144500.json    # Processing metadata
```

## What You'll Get

### Structured JSON Data
```json
{
  "winning_creatives": [...],  // Top 20 ads with full analysis
  "competitors": [...],        // Pages running these ads
  "patterns": {...}            // Aggregated insights
}
```

### Intelligence Report
- Top competitors list
- Winning creatives table (ranked by days active)
- Pattern analysis:
  - Most effective hook types
  - Common visual styles
  - Format distribution
  - Offer type breakdown
- Creative examples with analysis
- Recommendations for Agent 4

## Understanding Winning Criteria

**"Winning" = Active >14 days**

Why? Long-running ads indicate:
- ✅ Positive ROI (otherwise advertiser would stop)
- ✅ Effective messaging (resonates with audience)
- ✅ Proven creative (not experimental)

**Classification:**
- **Strong Winner**: >30 days (highly proven)
- **Winner**: 14-30 days (likely profitable)
- **Testing**: 7-14 days (early stage, uncertain)
- **New**: <7 days (too early to judge)

## Pattern Analysis Examples

### Hook Type Distribution
```
Pain: 40% (8/20) ← Most common winner
Benefit: 35% (7/20)
Curiosity: 25% (5/20)
```
**Insight**: Pain-based hooks dominate winning ads

### Visual Style Trends
```
Testimonial: 50% (10/20) ← Dominant style
Bold/Colorful: 30% (6/20)
Minimalist: 20% (4/20)
```
**Insight**: Customer testimonials are highly effective

### Offer Types
```
Free trial: 45% (9/20) ← Most common
Lead magnet: 30% (6/20)
Discount: 25% (5/20)
```
**Insight**: Low-risk trial offers convert best

## Use Cases

### For Agent 4 (Creative Strategist)
The competitor intel provides:
- Winning hook types → Creative brief angles
- Visual style trends → Design direction
- Reference creatives → Inspiration library
- Proven offers → Offer strategy

### For Strategic Decisions
- Identify market gaps (underutilized hooks)
- Validate messaging approaches (what's working)
- Benchmark against competition
- Discover new creative angles

### Standalone Use
- Competitive research
- Market trend analysis
- Creative inspiration gathering

## Tips for Best Results

1. **Choose Right VPs**:
   - Use specific, benefit-focused VPs
   - Include pain point language
   - Add industry context (e.g., "restaurant")

2. **Monitor Apify Usage**:
   - Actor may fetch more than requested
   - Watch for runaway costs
   - 50 items per query is a safe default

3. **Interpret Patterns**:
   - High frequency ≠ automatically use it
   - Look for gaps (underserved angles)
   - Consider your unique positioning

4. **Download Creatives**:
   - Keep local copies for reference
   - Creatives may be removed from Ads Library
   - Use for Agent 4 inspiration

## Common Search Queries

From typical B2B SaaS VPs:

| Industry | Value Prop | Search Queries |
|----------|------------|----------------|
| Restaurant Tech | "Boost repeat customers" | "customer loyalty restaurant", "SMS marketing dining" |
| Agency SaaS | "Scale with automation" | "agency automation", "AI for agencies" |
| E-commerce | "Reduce cart abandonment" | "cart recovery", "ecommerce retention" |

## Understanding the Output

### Winning Creative Entry
```json
{
  "ad_id": "123456",
  "page_name": "CompetitorBrand",
  "days_active": 45,
  "ad_copy": "Stop losing customers to delivery apps...",
  "analysis": {
    "hook_type": "pain",
    "offer_type": "trial",
    "visual_style": "testimonial",
    "cta_type": "sign_up"
  }
}
```

### What Each Field Means:
- **days_active**: How long ad has been running (45 = strong winner)
- **hook_type**: Primary attention mechanism
- **offer_type**: What's being offered
- **visual_style**: Design approach
- **cta_type**: Action requested

## Next Steps

After getting competitor intel:
1. Review winning patterns
2. Identify 2-3 top-performing angles
3. Feed insights to Agent 4 for creative briefs
4. Use reference creatives for visual inspiration

## Files Reference

- **Workflow**: `.agent/workflows/agent3-competitor-intel.md`
- **System Prompt**: `agents/competitor_intel/AGENT_PROMPT.md`
- **Python Utils**: `agents/competitor_intel/processing_utils.py`
- **Output Schema**: `shared/schemas/competitor_intel.json`
