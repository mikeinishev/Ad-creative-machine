---
description: Analyze landing page and extract marketing intelligence
---

# Marketing Analyst Agent

Workflow for analyzing landing pages to extract value propositions, audience segments, pain points, and offers.

## Usage

Provide the landing page URL (and optionally, design analysis from Agent 1):
- Landing URL: `https://example.com/product`
- Design Analysis (optional): `outputs/analysis/design_[timestamp].json`

## Workflow Steps

### Step 1: Page Scraping

**Using Playwright MCP:**

// turbo
```
Navigate to landing page: [URL]

Instructions:
1. Go to the URL
2. Wait for full page load (wait for network idle)
3. Scroll through entire page to trigger lazy-loaded content
4. Extract all text content from:
   - Headers (h1, h2, h3, h4)
   - Paragraphs
   - Lists (ul, li)
   - Buttons and CTAs
   - Forms and input labels
   - Testimonials
   - FAQ sections

5. Take full-page screenshot for reference
6. Save extracted text to temporary file
```

### Step 2: Content Analysis

Analyze the extracted content:

```
From the page content:

1. **Identify Pain Points**:
   - Look for: "struggling with", "tired of", "frustrated by"
   - Find "before state" descriptions
   - Extract problem statements
   - List: 3-5 main pain points

2. **Identify Benefits**:
   - Look for: "achieve", "get", "unlock", "discover"
   - Find "after state" descriptions
   - Extract outcome promises
   - List: 3-5 main benefits

3. **Extract Social Proof**:
   - Customer testimonials (with names/companies)
   - Usage stats ("X users", "Y% increase")
   - Company logos (partners, clients)
   - Awards or certifications
   - Media mentions
   - List: All social proof elements

4. **Map CTA Structure**:
   - Primary CTA (main action button)
   - Secondary CTAs (alternative actions)
   - CTA placement (above fold, multiple locations)
   - CTA text patterns
```

### Step 3: Audience Segmentation

Identify distinct customer segments:

```
Analyze the page language to identify 2-3 audience segments.

For EACH segment, define:

**Segment Name**: [Descriptive name]

**Demographics**:
- Industry/Profession: [e.g., "Restaurant owners"]
- Business size: [e.g., "SMB, 1-50 employees"]
- Location: [if mentioned, e.g., "North America"]
- Experience level: [e.g., "First-time buyers"]

**Psychographics**:
- Goals: [What they want to achieve]
- Fears: [What they want to avoid]
- Values: [What matters to them]
- Motivations: [What drives their decision]

**Pain Points**: [Specific to this segment]
- [Pain 1]
- [Pain 2]
- [Pain 3]

**Triggers**: [What brings them to this page]
- [Trigger 1]
- [Trigger 2]

**Language Patterns**: [How they describe their problem]
- Example phrases from the page that resonate with this segment
```

### Step 4: Value Proposition Extraction

Extract 2-3 primary value propositions:

```
For EACH value proposition:

**VP ID**: vp_1
**Headline**: [The main promise]
**Target Audience**: [Which segment(s) this VP targets]

**Supporting Points**:
1. [Proof point or feature that supports the VP]
2. [Another proof point]
3. [Another proof point]

**Unique Mechanism**: [What makes this different from alternatives]

**Transformation**:
- From: [Current pain state]
- To: [Desired outcome state]

**Believability**: [Why should they believe this claim?]
- Proof: [Social proof, data, testimonials]
- Authority: [Expertise, credentials]
```

### Step 5: Offer Analysis

Identify and classify all offers on the page:

```
For EACH offer found:

**Offer Type**: [Choose one]
- lead_magnet (free resource, guide, ebook)
- discount (% off, $ off)
- trial (free trial, freemium)
- webinar (live event, workshop)
- quiz (diagnostic quiz, assessment)
- demo (product demo, consultation)

**Description**: [What's being offered]

**Value Stack**: [Everything included]
- [Component 1]
- [Component 2]
- [Component 3]

**Pricing**: [If mentioned]
- Regular price: [...]
- Sale price: [...]
- Savings: [...]

**Urgency Elements**:
- Scarcity: [Limited spots, limited quantity]
- Deadline: [Offer expires on X]
- Bonus: [Limited-time bonus]

**Risk Reversal**:
- Guarantee: [Money-back, satisfaction guarantee]
- Free trial: [How long]
- No commitment: [Cancel anytime]
```

### Step 6: Output Generation

// turbo
```
Generate outputs:

1. **marketing_[timestamp].json**: Full structured data according to schema

2. **marketing_[timestamp]_summary.md**: Human-readable report with:

---
# Marketing Analysis Summary
Date: [timestamp]
URL: [landing_url]

## Page Overview
- Main headline: [...]
- Primary value prop: [...]
- Target audience: [...]
- Main offer: [...]

## Audience Segments (2-3)
### Segment 1: [Name]
[Details]

### Segment 2: [Name]
[Details]

## Value Propositions (2-3)
### VP 1: [Headline]
[Details]

## Pain Points (Top 5)
1. [Pain point]
2. [Pain point]
...

## Benefits (Top 5)
1. [Benefit]
2. [Benefit]
...

## Offers
### Primary Offer: [Type]
[Details]

## Social Proof
- [Element 1]
- [Element 2]
...

## Recommendations for Creatives
[Based on analysis, suggest what creative angles might work]
---

3. Save both files to `outputs/analysis/`
```

## Expected Output

### JSON Structure
```json
{
  "landing_analysis": {
    "url": "https://example.com/product",
    "headline": "Boost Repeat Customers with Digital Loyalty",
    "subheadline": "Join 10,000+ restaurants using Boomerang",
    "pain_points": [
      "Competing with delivery apps",
      "Customers don't return",
      "Hard to track customer loyalty"
    ],
    "benefits": [
      "25% increase in repeat visits",
      "Automated SMS campaigns",
      "Real-time customer analytics"
    ],
    "social_proof": [
      "10,000+ restaurant partners",
      "Testimonial: Joe's Pizza increased repeat customers by 40%",
      "Featured in Restaurant Business Magazine"
    ],
    "cta_structure": [
      "Start Free Trial",
      "Schedule Demo"
    ]
  },
  "audiences": [
    {
      "segment": "Independent Restaurant Owners",
      "demographics": "SMB, single location, full-service dining",
      "psychographics": "Want to build loyal customer base, compete with chains",
      "pain_points": [
        "Losing customers to delivery apps",
        "No customer data",
        "Hard to drive repeat visits"
      ],
      "triggers": [
        "Declining repeat rate",
        "Delivery app fees eating profits"
      ]
    }
  ],
  "value_propositions": [
    {
      "id": "vp_1",
      "headline": "Turn One-Time Diners into Regulars",
      "supporting_points": [
        "Automated loyalty rewards",
        "SMS marketing campaigns",
        "Customer visit tracking"
      ],
      "target_audience": "Independent Restaurant Owners",
      "unique_mechanism": "Mobile-first digital loyalty cards",
      "transformation": {
        "from": "One-time visitors, no way to bring them back",
        "to": "Regular customers who return 2-3x more often"
      }
    }
  ],
  "offers": [
    {
      "type": "trial",
      "description": "30-day free trial, no credit card required",
      "value_stack": [
        "Digital loyalty platform",
        "SMS marketing tools",
        "Analytics dashboard",
        "24/7 support"
      ],
      "pricing": "$99/month after trial",
      "urgency_elements": [
        "Limited time: First month free for new signups"
      ],
      "risk_reversal": "30-day money-back guarantee"
    }
  ]
}
```

## MCP Tools Used

- `playwright.navigate` - Load landing page
- `playwright.screenshot` - Capture page visual
- `playwright.evaluate` - Extract DOM content
- `playwright.fill` / `playwright.click` - Interact with page if needed
