---
description: Generate ad creative images from creative briefs
---

# Designer Agent

Workflow for generating production-ready Meta Ads creatives from strategic briefs.

## Usage

Provide creative brief(s) from Agent 4:
- Creative Briefs: `outputs/briefs/creative_briefs_[timestamp].json`
- Or individual brief: `outputs/briefs/individual/brief_001.json`

## Workflow Steps

### Step 1: Select Briefs to Generate

```
Load creative briefs file.

Prioritize by:
1. **High priority briefs first** (score 10-12)
2. **Briefs targeting largest audiences**
3. **Proven hook types** (lower risk)

For initial testing, select:
- Top 2-3 high-priority briefs
- Generate all variations (A/B/C) for each
- Both formats (square + vertical)

Output: List of brief IDs to generate
```

### Step 2: Parse Brief Details

For EACH selected brief:

```
Extract from brief JSON:

**Text Content:**
- Hook: brief.creative_direction.hook
- Body: brief.creative_direction.body
- CTA: brief.creative_direction.cta

**Visual Specifications:**
- Visual concept: brief.creative_direction.visual_concept
- Color palette: brief.creative_direction.color_scheme
- Typography style: brief.creative_direction.typography_style
- Imagery: brief.creative_direction.imagery

**Variations:**
- Variant A hook: brief.variations[0].hook_variation
- Variant B hook: brief.variations[1].hook_variation
- Variant C hook: brief.variations[2].hook_variation

**Formats:**
- Dimensions: brief.dimensions (e.g., ["1080x1080", "1080x1920"])
```

### Step 3: Create Image Generation Prompts

For EACH brief + variation + format combination:

```
Build comprehensive prompt:

Template:
"""
Create a professional Meta Ads creative image for {platform} feed.

VISUAL CONCEPT:
{visual_concept from brief}

TEXT OVERLAY (must be clearly visible and readable):
- Headline (top/center, large bold text, 96px): "{hook}"
- Body text (middle, medium text, 48px): "{body}"
- CTA Button (bottom, white text on {cta_color} button): "{cta}"

DESIGN SPECIFICATIONS:
- Dimensions: {width}x{height} pixels exactly
- Color palette: {color_scheme} - use these colors throughout
- Typography: {typography_style} style (bold, clear, readable)
- Main visual elements: {imagery list}

COMPOSITION:
{composition_instructions based on format}

STYLE:
- Modern, professional marketing ad aesthetic
- High contrast for text readability
- Clean, uncluttered layout
- Mobile-optimized (text must be readable on small screens)
- {visual_style from competitor analysis if available}

QUALITY:
- High resolution, crisp and clear
- Professional photography/illustration quality
- No pixelation, proper lighting
"""

Composition instructions by format:

For Square (1080x1080):
"Layout: Visual in top 50%, text overlay in bottom 50% on solid/gradient background. CTA button centered at bottom with padding."

For Vertical (1080x1920):
"Layout: Vertical composition. Avoid top 250px and bottom 250px (safe zones). Visual in upper portion, headline in middle, body text below, CTA button in lower third."
```

### Step 4: Generate Creative Images

**Using Google Imagen via generate_image:**

```
For each brief + variation + format:

1. Build detailed Imagen prompt:

Template:
"Professional marketing advertisement for {product}, {visual_concept}, 
text overlay with \"{hook}\" at top in bold sans-serif font {size}px white text,
\"{body}\" in middle section in medium weight font {size}px white text,
\"{cta}\" on {cta_color} button at bottom,
color scheme using {brand_colors},
{composition_description}, professional photography quality,
clean marketing layout, high contrast text for mobile readability,
photorealistic style, exact dimensions {width}x{height} pixels"

2. Call generate_image tool:

// turbo
generate_image(
  prompt: "[detailed prompt from step 1]",
  image_name: "{brief_id}_variant_{A|B|C}_{dimension}"
)

Wait for completion (5-15 seconds per image)

3. Image saved automatically to artifacts directory

4. Move/copy to outputs/creatives/{brief_id}/

Rename if needed to match convention:
{brief_id}_variant_{A|B|C}_{dimension}.png
```

**Example Imagen Prompt for Square (1080x1080)**:

```
Professional marketing advertisement for restaurant loyalty app,
split screen composition with clear visual divide,
left side: concerned restaurant owner in business casual looking at 
tablet displaying declining revenue chart, realistic office setting,
right side: smiling customer walking into restaurant entrance holding 
smartphone showing digital loyalty card on screen,
text overlay with "Losing customers to DoorDash?" at top center in 
large bold sans-serif font white color on dark semi-transparent background,
"Turn one-time diners into loyal regulars with automated digital loyalty. 
10,000+ restaurants increased repeat visits by 25%." in middle section 
in medium sans-serif font white text,
"Start Free Trial" on vibrant green button (#28A745) at bottom center 
with white bold text,
color palette: vibrant orange #FF6B35 and navy blue #004E89 as accent colors,
centered composition with visual balance,
professional photography quality, clean marketing aesthetic,
high contrast text for mobile readability,
modern tech advertisement style,
exact dimensions 1080x1080 pixels
```

**Example Imagen Prompt for Vertical (1080x1920)**:

```
Professional marketing advertisement for restaurant loyalty app,
vertical composition optimized for mobile Instagram Stories,
full bleed background with gradient from navy blue #004E89 to lighter blue,
top third: professional portrait of frustrated restaurant owner looking 
at declining metrics on tablet, realistic lighting,
middle section centered: large text overlay "Tired of customers who never 
come back?" in bold 120px sans-serif font white color with subtle dark shadow,
sub-text below: "Turn one-time diners into loyal regulars. 10,000+ 
restaurants trust us." in 60px medium weight white font,
lower third: prominent green rectangular button (#28A745) with rounded 
corners containing "Start Free Trial" in 54px bold white text,
orange #FF6B35 accent elements for visual interest,
professional photography quality for mobile,
high contrast text readability,
modern marketing creative for Stories format,
exact dimensions 1080x1920 pixels,
keep important elements within safe zones
```

**Key Prompt Elements for Imagen**:

- **Exact dimensions**: Always specify "exact dimensions 1080x1080 pixels"
- **Text in quotes**: Put all overlay text in explicit quotes
- **Font specifications**: "bold sans-serif font", "120px", "white color"
- **Backgrounds for text**: "on dark semi-transparent background"
- **Color codes**: Include hex codes "#FF6B35", "#004E89"
- **Style keywords**: "professional photography quality", "photorealistic"
- **Composition details**: "split screen", "centered", "top third"
```

### Step 5: Generate All Variations

```
For EACH brief:
  For EACH variation (A, B, C):
    For EACH dimension (1080x1080, 1080x1920):
      
      Generate image with:
      - Same visual concept
      - Same colors
      - Same layout
      - ONLY DIFFERENT: Hook text
      
      Save as: {brief_id}_variant_{var}_{dim}.png

Expected output per brief:
- 6 total images (3 variations × 2 dimensions)
```

### Step 6: Create Metadata

For each brief folder, create metadata.json:

```
{
  "brief_id": "brief_001",
  "concept_name": "Pain Amplifier - Delivery Apps",
  "priority": "high",
  "generated_at": "2026-02-09T22:00:00Z",
  "variations": [
    {
      "variant": "A",
      "hook": "Losing customers to delivery apps?",
      "reasoning": "Direct pain point question (proven format)",
      "files": {
        "square": "brief_001_variant_A_1080x1080.png",
        "vertical": "brief_001_variant_A_1080x1920.png"
      }
    },
    {
      "variant": "B",
      "hook": "Tired of customers who never come back?",
      "reasoning": "Emotional trigger pattern",
      "files": {
        "square": "brief_001_variant_B_1080x1080.png",
        "vertical": "brief_001_variant_B_1080x1920.png"
      }
    },
    {
      "variant": "C",
      "hook": "What if every customer returned 3x more often?",
      "reasoning": "Benefit-curiosity hybrid",
      "files": {
        "square": "brief_001_variant_C_1080x1080.png",
        "vertical": "brief_001_variant_C_1080x1920.png"
      }
    }
  ],
  "design_specs": {
    "colors_used": ["#FF6B35", "#004E89", "#28A745"],
    "typography_style": "bold",
    "visual_concept": "Split screen: frustrated owner vs. returning customer"
  },
  "total_images_generated": 6
}
```

### Step 7: Generate Summary Report

Create comprehensive generation summary:

```
File: outputs/creatives/generation_summary_[timestamp].md

---
# Creative Generation Summary
Date: [timestamp]
Total Briefs Processed: 3
Total Images Generated: 18 (3 briefs × 6 images each)

## Briefs Generated

### Brief 001: Pain Amplifier - Delivery Apps (Priority: High)
**Variations**: A, B, C
**Formats**: Square (1080x1080), Vertical (1080x1920)
**Visual Concept**: Split screen - frustrated owner vs. returning customer
**Colors**: #FF6B35, #004E89, #28A745

**Generated Files**:
- ✅ variant_A_1080x1080.png
- ✅ variant_A_1080x1920.png
- ✅ variant_B_1080x1080.png
- ✅ variant_B_1080x1920.png
- ✅ variant_C_1080x1080.png
- ✅ variant_C_1080x1920.png

**Hook Variations**:
- A: "Losing customers to delivery apps?" (Proven)
- B: "Tired of customers who never come back?" (Emotional)
- C: "What if every customer returned 3x more often?" (Benefit)

---

[Repeat for each brief]

## Next Steps - Campaign Launch

### Testing Strategy
1. **Launch Brief 001 & 002** (High priority)
2. **Run all variations simultaneously** (A/B/C test)
3. **Test both formats** (Feed + Stories)
4. **Budget allocation**: Equal split initially

### Success Metrics
- CTR (Click-Through Rate): Target >1.5%
- CPL (Cost Per Lead): Target <$X
- Conversion Rate: Target >Y%

### Optimization Plan
- After 72 hours: Identify winning variation
- Scale winner, pause losers
- Iterate on creative with learnings
---
```

## Expected Output Structure

```
outputs/creatives/
├── brief_001/
│   ├── variant_A_1080x1080.png
│   ├── variant_A_1080x1920.png
│   ├── variant_B_1080x1080.png
│   ├── variant_B_1080x1920.png
│   ├── variant_C_1080x1080.png
│   ├── variant_C_1080x1920.png
│   └── metadata.json
├── brief_002/
│   ├── [6 images + metadata]
│   └── ...
├── brief_003/
│   └── [6 images + metadata]
└── generation_summary_[timestamp].md
```

## Design Quality Checklist

After generation, verify each creative:

```
For EACH generated image:

✅ Correct Dimensions:
   - Square: Exactly 1080×1080px
   - Vertical: Exactly 1080×1920px

✅ Text Readability:
   - All text clearly visible
   - High contrast (text vs background)
   - No text cutoff or obscured
   - Font sizes appropriate

✅ Brand Consistency:
   - Brand colors used correctly
   - Typography matches brief
   - Visual style aligns with brand

✅ Platform Requirements:
   - Text <20% of image (Meta guideline)
   - Safe zones respected (Stories)
   - File size <5MB
   - No prohibited content

✅ Variation Integrity:
   - Only hook changes between A/B/C
   - Visual identical across variations
   - Layout consistent

If any check fails, regenerate that specific creative.
```

## Prompt Engineering Tips

For better results:

1. **Be Specific About Text**:
   - Include exact text placement
   - Specify font sizes
   - Mention text color and background

2. **Describe Visual Clearly**:
   - Use descriptive adjectives
   - Reference style (photographic, illustrated, flat design)
   - Mention lighting and mood

3. **Include Quality Markers**:
   - "Professional", "high-resolution", "clean"
   - "Marketing ad aesthetic"
   - "Mobile-optimized"

4. **Specify Composition**:
   - "Centered", "rule of thirds", "split screen"
   - "Upper half", "lower third"
   - "Balanced composition"

5. **Reference Colors**:
   - Use exact hex codes
   - Describe color relationships
   - Mention accent colors for CTA

## Iteration and Refinement

If initial generation needs improvement:

```
Review generated creative:
- Is hook text readable?
- Is visual concept clear?
- Do colors match brand?
- Is CTA visible?

If NO to any:
1. Adjust prompt with more specific instructions
2. Regenerate that specific variation/format
3. Compare side-by-side
4. Keep best version
```

## Output Files

All creatives saved to `outputs/creatives/` with structure:
- One folder per brief
- 6 images per brief (3 variations × 2 formats)
- metadata.json per brief
- Overall generation summary
