---
description: Analyze quiz funnel design from any format (Figma, PDF, URL, images)
---

# Design Analyzer Agent

Workflow for analyzing quiz funnel designs and extracting structured information.

## Usage

Provide the design in any supported format:
- Figma URL: `https://figma.com/file/ABC123/Quiz-Design`
- PDF file: `./inputs/quiz-design.pdf`
- Landing URL: `https://example.com/quiz`
- Image files: `./inputs/screen1.png`, `./inputs/screen2.png`

## Workflow Steps

### Step 1: Input Detection
Automatically detect the input format:

```
Given input: [INPUT_PATH_OR_URL]

Detect format:
- Contains "figma.com" → Figma
- Ends with ".pdf" → PDF
- Starts with "http" → Web URL
- Ends with ".png/.jpg" → Image

Format detected: [FORMAT]
```

### Step 2: Content Extraction

**For Figma:**
// turbo
```
Using Figma MCP tools:
1. Access file at [FIGMA_URL]
2. List all frames/pages
3. For each frame, extract:
   - All text layers (note font, size, color)
   - Color fills and strokes
   - Image references
4. Export frame thumbnails if needed
```

**For PDF:**
```
1. Parse PDF pages
2. For each page, analyze with vision:
   - What type of screen is this? (welcome/question/result/offer)
   - What is the main headline?
   - What is the CTA text?
   - What colors are prominent?
   - What visual elements are present?
```

**For URL:**
// turbo
```
Using Playwright:
1. Navigate to [URL]
2. Wait for page load
3. Take full-page screenshot
4. If interactive quiz, try to capture different states:
   - Initial screen
   - Question screens (click through if possible)
   - Result screen
5. Analyze screenshots with vision
```

**For Images:**
```
For each image file:
1. Analyze with vision
2. Identify screen type
3. Extract text content
4. Note visual style
5. Order images logically
```

### Step 3: Structure Analysis

Organize extracted data into quiz funnel structure:

```
Analyze all extracted screens:

1. Classify each screen:
   - Welcome: "Start Quiz", "Take Quiz", introductory language
   - Question: Has question prompt + answer options
   - Result: Shows outcome/recommendation
   - Offer: Has pricing, product info, "Buy Now" CTA

2. Map flow:
   - Determine screen sequence
   - Note any branching logic
   - Identify question progression

3. Extract brand identity:
   - Primary colors (hex codes)
   - Typography (font families)
   - Logo/brand marks
   - Visual style (minimalist/bold/playful)

4. Build JSON output according to schema
```

### Step 4: Output Generation

// turbo
```
Generate outputs:

1. Create design_[timestamp].json with full structured data
2. Create design_[timestamp]_summary.md with human-readable summary:

---
# Design Analysis Summary
Date: [timestamp]
Input: [input_path]
Format: [format]

## Funnel Structure
- Total screens: X
- Flow: Welcome → Y questions → Result → Offer

## Key Elements
- Headline style: [description]
- Primary CTA: "[text]"
- Color scheme: [colors]
- Visual style: [description]

## Screens
### Screen 1: Welcome
- Headline: "[text]"
- CTA: "[text]"
- Elements: [list]

[... for each screen ...]
---

3. Save both files to outputs/analysis/
```

## Expected Output

### JSON Structure (design_[timestamp].json)
```json
{
  "funnel_structure": {
    "screens": [
      {
        "id": "screen_1",
        "type": "welcome",
        "headline": "Discover Your Perfect Marketing Strategy",
        "subheadline": "Take our 2-minute quiz",
        "cta_text": "Start Quiz →",
        "visual_elements": ["hero_image", "logo", "trust_badges"],
        "color_scheme": ["#2C3E50", "#E74C3C", "#ECF0F1"],
        "typography": {
          "heading": "Poppins Bold 48px",
          "body": "Inter Regular 16px"
        }
      }
    ],
    "flow": ["screen_1", "screen_2", "screen_3", "screen_4", "screen_5"],
    "brand_assets": {
      "logo_url": "...",
      "color_palette": ["#2C3E50", "#E74C3C", "#ECF0F1"]
    }
  }
}
```

## MCP Tools Used

- `figma.get_file` - For Figma URLs
- `figma.get_file_nodes` - Extract specific frames
- `playwright.goto` - For web URLs
- `playwright.screenshot` - Capture pages
- Built-in vision - For image/PDF analysis
