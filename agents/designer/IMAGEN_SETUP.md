# Google Imagen Integration for Agent 5

## Overview
Agent 5 uses **Google Imagen 3** through Antigravity's native `generate_image` tool for professional-quality ad creative generation.

## Setup

### No Additional Configuration Required

Google Imagen is built into Antigravity and works out of the box:
- ✅ No API tokens needed
- ✅ No external services
- ✅ Included in Antigravity platform usage

## Model Information

**Model**: Google Imagen 3
**Provider**: Integrated via Antigravity
**Quality**: Photorealistic, high-quality outputs
**Text Rendering**: Excellent for ad text overlays

## Usage in Agent 5

### Basic Syntax

```javascript
generate_image(
  prompt: "Detailed description with text, layout, and specifications",
  image_name: "brief_001_variant_a_1080x1080"
)
```

### Prompt Structure

```
Professional marketing advertisement for {product},
{visual_concept_description},
text overlay with "{headline}" at {position} in {font_details},
"{body_text}" at {position} in {font_details},
"{cta}" on {color} button at {position},
color scheme using {hex_codes},
{composition_details},
professional photography quality,
photorealistic style,
exact dimensions {width}x{height} pixels
```

### Complete Example Prompt

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

## Best Practices

### Text Rendering

**Do**:
✅ Put exact text in quotes: "Losing customers to DoorDash?"
✅ Specify font details: "bold sans-serif font", "white color"
✅ Include sizes: "large bold" or "120px" (Imagen understands both)
✅ Add backgrounds: "on dark semi-transparent background"
✅ Specify placement: "at top center", "in middle section"

**Don't**:
❌ Expect perfect text without explicit quotes
❌ Use overly artistic descriptions
❌ Skip color specifications
❌ Forget to specify exact dimensions

### Visual Quality

**Do**:
✅ Use "photorealistic" for realistic ads
✅ Include "professional photography quality"
✅ Specify lighting: "realistic lighting", "high contrast"
✅ Detail composition: "split screen", "centered", "top third"
✅ Always include "exact dimensions X×Y pixels"

**Tips**:
- Imagen understands natural language well
- Be descriptive but concise
- Specify ALL text elements explicitly
- Include hex color codes for brand colors

### Dimensions

Always specify exact dimensions at end of prompt:
- Square: "exact dimensions 1080x1080 pixels"
- Vertical: "exact dimensions 1080x1920 pixels"

This ensures proper aspect ratio and sizing.

## Performance

**Generation Time**: 5-15 seconds per image
**Quality**: High (Imagen 3 model)
**Cost**: Included in Antigravity usage (no additional fees)

**Estimations**:
- 1 brief (6 images): ~60-90 seconds
- 3 briefs (18 images): ~3-5 minutes
- 10 briefs (60 images): ~10-15 minutes

## Advantages vs. Other Models

### vs. Midjourney
✅ **Faster**: 5-15s vs 30-90s per image
✅ **Simpler**: No actor setup, no Apify integration
✅ **Cost**: Included vs $0.02-0.04 per image
✅ **Text**: Excellent text rendering in natural language

### vs. DALL-E
✅ **Quality**: Photorealistic outputs
✅ **Text**: Better text overlay capabilities
✅ **Integration**: Native to Antigravity

## Troubleshooting

### Text not rendering correctly
- Ensure text is in explicit quotes
- Add "text overlay with" before text
- Include background for contrast
- Simplify font descriptions

### Wrong dimensions
- Always specify "exact dimensions X×Y pixels" at end
- Use exact values: 1080x1080 or 1080x1920
- Don't use ratios like "1:1" or "9:16"

### Colors don't match brand
- Include hex codes: "#FF6B35", "#004E89"
- Specify where colors are used: "as accent colors", "for button"
- Add "color palette:" or "color scheme using"

### Output too artistic
- Add "photorealistic style"
- Include "professional photography quality"
- Avoid artistic terms like "painterly", "impressionist"
- Use "realistic", "clean", "modern"

## Workflow Integration

Agent 5 automatically:
1. ✅ Builds Imagen-optimized prompts from briefs
2. ✅ Calls generate_image with detailed specifications
3. ✅ Waits for generation (5-15s each)
4. ✅ Saves images with proper naming convention
5. ✅ Organizes into brief folders

**No manual intervention required** - just run `/agent5-designer`!

## Summary

Google Imagen through Antigravity is the perfect choice for Agent 5:
- **Simple**: No setup, no tokens, no external services
- **Fast**: 5-15 seconds per image
- **Quality**: Professional-grade photorealistic outputs
- **Cost-effective**: Included in platform usage
- **Reliable**: Native integration, no API dependencies

The system is ready to generate high-quality ad creatives immediately!
