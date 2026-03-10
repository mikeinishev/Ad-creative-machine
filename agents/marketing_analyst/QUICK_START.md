# Agent 2: Marketing Analyst - Quick Start

## Purpose
Extracts marketing intelligence from landing pages: value propositions, audience segments, pain points, benefits, and offers.

## How to Use

### 1. Prepare Your Input

You need:
- **Landing page URL**: The main product/service page
- **(Optional) Design Analysis**: Output from Agent 1 for context

### 2. Run the Workflow

Use the workflow: `/agent2-marketing-analyst`

Provide landing URL when prompted:
```
Landing URL: https://example.com/product
```

### 3. Review Output

Find your analysis in:
```
outputs/analysis/
├── marketing_20240209_135000.json       # Structured data
├── marketing_20240209_135000_summary.md # Human-readable summary
└── marketing_20240209_135000_metadata.json # Processing metadata
```

## What You'll Get

### Structured JSON Data
```json
{
  "landing_analysis": {...},    // Page content breakdown
  "audiences": [...],           // 2-3 customer segments
  "value_propositions": [...],  // Primary VPs
  "offers": [...]              // Lead magnets, trials, etc.
}
```

### Summary Report
- Page overview
- Audience segments with demographics/psychographics
- Value propositions with transformation stories
- Pain points and benefits
- Offers and CTAs
- Recommendations for creative angles

## Use Cases

### For Agent 3 (Competitor Intel)
The marketing analysis provides:
- Value propositions → Search queries for Meta Ads
- Pain points → Competitor angle identification
- Target segments → Filter criteria

### For Agent 4 (Creative Strategist)
The marketing analysis provides:
- Audiences → Who to target with each creative
- Value props → Core messaging for ads
- Pain points/benefits → Hook and body copy angles

### Standalone Use
- Competitive intelligence on other products
- Landing page optimization research
- Messaging audit for your own pages

## Tips for Best Results

1. **Choose the right URL**:
   - Use the main product landing page (not homepage)
   - Pages with clear offers work best
   - Long-form sales pages provide more data

2. **For B2B SaaS**:
   - Look for industry-specific pain points
   - ROI/metrics claims are key
   - Multi-segment targeting is common

3. **For B2C**:
   - Emotional triggers matter more
   - Lifestyle benefits vs. features
   - Before/after transformations

## Example Output Structure

### Audience Segment
```
Segment: Independent Restaurant Owners
Demographics: SMB, single location, full-service
Pain Points:
  - Losing customers to delivery apps
  - No customer data
  - Can't afford expensive solutions
Triggers:
  - Declining repeat rate
  - Delivery app fees
```

### Value Proposition
```
VP: Turn One-Time Diners Into Loyal Regulars
Mechanism: Mobile-first digital loyalty cards
Transformation:
  From: One-time visitors
  To: Regular customers (2-3x more visits)
Proof: 10,000+ restaurants, +25% avg increase
```

## Next Steps

After getting marketing analysis:
1. **Feed to Agent 3**: Value props become search queries for competitor research
2. **Combine with Agent 1 output**: Design + Marketing = full funnel context
3. **Feed to Agent 4**: Basis for creative brief generation

## Files Reference

- **Workflow**: `.agent/workflows/agent2-marketing-analyst.md`
- **System Prompt**: `agents/marketing_analyst/AGENT_PROMPT.md`
- **Example Output**: `agents/marketing_analyst/EXAMPLE.md`
- **Output Schema**: `shared/schemas/marketing_analysis.json`
