---
description: Search Meta Ads Library for competitor creatives using value propositions
---

# Competitor Intel Agent

Workflow for finding and analyzing winning competitor ad creatives in Meta Ads Library.

## Usage

Provide value propositions from Agent 2 (or manually):
- Marketing Analysis: `outputs/analysis/marketing_[timestamp].json`
- Or manual VPs: List of 2-3 value propositions

## Workflow Steps

### Step 1: Generate Search Queries

From value propositions, create search queries:

```
For EACH value proposition from Agent 2:

VP: "{headline}"

Generate 2-3 search queries:

1. **Direct keywords** (3-4 words from VP):
   Example: "digital loyalty restaurant"

2. **Pain point angle** (if VP addresses pain):
   Example: "customer retention restaurant"

3. **Unique mechanism** (if VP has unique approach):
   Example: "SMS marketing restaurant"

Rules:
- Keep queries 2-4 words
- Include industry/niche context ("restaurant", "SaaS", etc.)
- Focus on benefits/outcomes, not brand names
- Broad enough to find multiple competitors

Output: List of 4-6 total search queries
```

### Step 2: Search Meta Ads Library

**Using Apify MCP:**

For EACH search query:

```
1. Construct Meta Ads Library URL:

Base URL: https://www.facebook.com/ads/library/
Parameters:
- active_status=active
- ad_type=all
- country=US (or US,CA for multi-country)
- q={URL_ENCODED_QUERY}

Full URL example:
https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&q=digital+loyalty+restaurant

2. Run Apify actor:

Actor: curious_coder/facebook-ads-library-scraper
Input:
{
  "urls": ["<constructed_url>"],
  "maxItems": 50
}

3. Monitor execution:
- Check run status every 30 seconds
- If actor fetches >100 items, consider aborting
- Wait for completion or abort after reasonable time

4. Fetch results:
- Get dataset ID from run
- Download all items from dataset
- Save raw results for processing
```

> ⚠️ **Important**: The actor may ignore `maxItems`. Monitor the run and abort if it's fetching too many results (e.g., >150 items when you wanted 50).

### Step 3: Filter and Score Creatives

Process the raw results:

```
For EACH ad in results:

1. **Extract fields** (handle nested structure):
   - ad_id: ad_archive_id
   - page_name: snapshot.page_name or pageName
   - ad_copy: snapshot.body.text or snapshot.caption
   - headline: snapshot.title
   - start_date: start_date (Unix) or startDate (string)
   - media_url: snapshot.images[0].original_image_url or snapshot.videos[0].video_hd_url
   - ad_library_url: ad_library_url or construct from ad_id

2. **Calculate duration**:
   days_active = (current_date - start_date) / 86400
   
3. **Apply filters**:
   - Must be currently active
   - Must have readable ad copy (not null/empty)
   - Optional: Filter by niche keywords in copy

4. **Classify**:
   - days_active > 30: "Strong Winner"
   - days_active 14-30: "Winner"
   - days_active 7-14: "Testing"
   - days_active < 7: "New"

5. **Select Top 20**:
   - Sort by days_active (descending)
   - Take top 20 winners (>14 days)
   - If <20 winners, include some "Testing" ads
```

### Step 4: Download Creative Assets

For the top 20 winners:

```
For EACH winning creative:

1. Get media URL from ad data:
   - For images: snapshot.images[0].original_image_url
   - For videos: snapshot.videos[0].video_hd_url

2. Download file:
   - Determine extension (.jpg, .png, .mp4)
   - Download to: outputs/competitor_intel/creatives/ad_{ad_id}.{ext}

3. Generate thumbnail (for videos):
   - Extract first frame or use video_preview_image_url
   - Save as ad_{ad_id}_thumb.jpg

4. Handle errors gracefully:
   - If download fails, save URL only
   - Note in metadata that asset wasn't downloaded
```

### Step 5: Analyze Patterns

For each winning creative, classify:

```
Analyze ad copy and visuals to determine:

**Hook Type** (primary attention-grabber):
- pain: "Tired of X", "Struggling with Y"
- curiosity: "The secret to X", "How to Y without Z"
- benefit: "Get X in Y days", "Achieve Z"
- social_proof: "10,000+ users", "Featured in"
- urgency: "Limited time", "Only X spots left"

**Offer Type** (what's being offered):
- lead_magnet: Free guide, checklist, ebook
- discount: Percentage or dollar off
- trial: Free trial period
- webinar: Live event, workshop
- quiz: Assessment, diagnostic tool
- demo: Product demonstration

**Visual Style** (design approach):
- minimalist: Clean, simple, white space
- bold: High contrast, bright colors, large text
- testimonial: Customer photo with quote
- ugc: User-generated, casual, phone-shot
- professional: Polished, corporate look

**CTA Type** (call-to-action):
- learn_more: "Learn More", "Discover How"
- sign_up: "Sign Up", "Get Started", "Join Now"
- download: "Download Free", "Get the Guide"
- book_call: "Schedule Demo", "Book a Call"

Save analysis with each creative.
```

### Step 6: Pattern Analysis

Aggregate data across all winners:

```
Calculate pattern frequencies:

1. **Hook Distribution**:
   Count each hook type
   Example: {"pain": 8, "benefit": 7, "curiosity": 5}

2. **Visual Style Trends**:
   Count each style
   Example: {"testimonial": 10, "bold": 6, "minimalist": 4}

3. **Format Distribution**:
   Count image vs video
   Example: {"image": 14, "video": 6}

4. **Offer Type Distribution**:
   Count each offer type
   Example: {"trial": 9, "lead_magnet": 6, "discount": 5}

5. **Common Elements**:
   - Most frequent words in winning ad copy
   - Common color palettes (if analyzable)
   - Average ad copy length
```

### Step 7: Generate Outputs

Create comprehensive report:

```
1. **Data JSON** (outputs/competitor_intel/data_[timestamp].json):

Full structured data with:
- search_queries used
- total_ads_found
- winning_creatives (top 20 with full details)
- competitors (page names with ad counts)
- patterns (aggregated analysis)

2. **Summary Markdown** (outputs/competitor_intel/report_[timestamp].md):

Human-readable report with:

---
# Competitor Intelligence Report
Date: Feb 9, 2026
Market: North America (US, CA)
Queries: [list]

## Executive Summary
- Total ads found: 150
- Winning ads (>14 days): 23
- Competitors analyzed: 12
- Top 20 winners selected for analysis

## Top Competitors
| Page | Active Ads | Days Running | Top Performer |
...

## Winning Creatives (Top 20)
| Rank | Page | Days | Hook | Offer | Format |
...

## Pattern Analysis

### Hook Types (What Works)
- Pain-based: 40% (8/20) - Most common
- Benefit-based: 35% (7/20)
- Curiosity: 25% (5/20)

### Visual Styles
- Testimonial: 50% (10/20) - Dominant
- Bold/Colorful: 30% (6/20)
- Minimalist: 20% (4/20)

### Offer Types
- Free trial: 45% (9/20)
- Lead magnet: 30% (6/20)
- Discount: 25% (5/20)

### Format
- Static images: 70% (14/20)
- Video: 30% (6/20)

## Creative Examples

### Example 1: Top Performer (45 days active)
**Page**: Brand X
**Hook Type**: Pain
**Ad Copy**: "Tired of losing customers to delivery apps? Our loyalty system brings them back 3x more often."
**Offer**: Free 30-day trial
**Visual**: Testimonial with owner photo
**CTA**: "Start Free Trial"

[Include 3-5 examples total]

## Recommendations for Creative Strategy

Based on winning patterns:
1. Test pain-based hooks first (proven winner)
2. Use testimonial-style visuals (50% of winners)
3. Offer free trial (highest conversion signal)
4. Keep format as static images initially (easier to test)

## Search Query Performance
| Query | Ads Found | Winners | Best Performer |
...
---

3. Save metadata file with processing details
```

## Expected Output

### Directory Structure
```
outputs/competitor_intel/
├── creatives/
│   ├── ad_123456.jpg
│   ├── ad_789012.jpg
│   ├── ad_345678_video.mp4
│   └── ad_345678_thumb.jpg
├── data_20260209_144500.json
├── report_20260209_144500.md
└── metadata_20260209_144500.json
```

### JSON Output Sample
```json
{
  "analysis_metadata": {
    "timestamp": "2026-02-09T14:45:00Z",
    "queries": ["digital loyalty restaurant", "SMS marketing restaurant"],
    "country": "US",
    "max_items_per_query": 50
  },
  "search_queries": [
    {
      "query": "digital loyalty restaurant",
      "ads_found": 75,
      "winners_found": 12
    }
  ],
  "competitors": [
    {
      "page_name": "LoyaltyBrand",
      "page_id": "123456",
      "ad_count": 5,
      "active_since": "2024-01-10"
    }
  ],
  "winning_creatives": [
    {
      "ad_id": "987654321",
      "rank": 1,
      "page_name": "LoyaltyBrand",
      "days_active": 45,
      "ad_copy": "Stop losing customers to delivery apps...",
      "headline": "Get Them Back 3x More Often",
      "media_type": "image",
      "media_url": "https://...",
      "local_path": "outputs/competitor_intel/creatives/ad_987654321.jpg",
      "ad_library_url": "https://www.facebook.com/ads/library/?id=987654321",
      "analysis": {
        "hook_type": "pain",
        "offer_type": "trial",
        "visual_style": "testimonial",
        "cta_type": "sign_up"
      }
    }
  ],
  "patterns": {
    "hook_distribution": {"pain": 8, "benefit": 7, "curiosity": 5},
    "visual_styles": {"testimonial": 10, "bold": 6, "minimalist": 4},
    "format_distribution": {"image": 14, "video": 6},
    "offer_types": {"trial": 9, "lead_magnet": 6, "discount": 5}
  }
}
```

## MCP Tools Used

- `apify.run_actor` - Execute Meta Ads Library scraper
- `apify.get_run` - Check run status
- `apify.abort_run` - Stop runaway scraper
- `apify.get_dataset` - Retrieve results
