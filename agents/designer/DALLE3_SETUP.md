# Gemini 2.5 Flash Image (Nano Banana) Integration for Agent 5 - Setup Guide

## Overview
Agent 5 uses **Gemini 2.5 Flash Image** ("Nano Banana") from Google for professional-quality Meta Ads creative generation.

## Prerequisites

### 1. Google AI Studio API Key

Get API key at: [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

Configure in `.env`:
```bash
GOOGLE_API_KEY=your_google_api_key_here
```

### 2. Google GenAI Python SDK

Install:
```bash
pip install google-genai
```

## Gemini 2.5 Flash Image Specifications

### Model ID
```
gemini-2.5-flash-image
```

### Supported Image Sizes
- **1:1** — Square format (perfect for Instagram/Facebook Feed)
- **9:16** — Portrait/vertical (perfect for Stories)
- Up to 10 output images per prompt

### Key Features
- High-fidelity, photorealistic image generation
- Excellent text rendering within images
- Natural language prompts
- Fast generation (10-30 seconds)
- SynthID invisible watermark on all generated images
- Up to 10 images per API call

### Pricing
- Significantly cheaper than DALL-E 3
- Pay-per-use via Google AI Studio

## Usage in Agent 5

### Python Example

```python
from google import genai
from google.genai import types
import os
import base64

client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

# Generate square creative (1:1)
response = client.models.generate_images(
    model="gemini-2.5-flash-image",
    prompt="Professional Meta Ads advertisement creative for restaurant loyalty app, split screen composition...",
    config=types.GenerateImagesConfig(
        number_of_images=1,
        aspect_ratio="1:1",  # Square for Feed
        # aspect_ratio="9:16",  # Vertical for Stories
    )
)

# Save the generated image
for i, image in enumerate(response.generated_images):
    image_bytes = base64.b64decode(image.image.image_bytes)
    with open(f"creative_{i}.png", "wb") as f:
        f.write(image_bytes)
```

### Full Workflow

1. **Build detailed prompt** (natural language)
2. **Call Gemini API** with `gemini-2.5-flash-image`
3. **Decode base64** image bytes from response
4. **Resize to Meta specs** if needed (to 1080px)
5. **Save** to `outputs/creatives/{brief_id}/`

## Prompt Engineering

### Template

```
Professional Meta Ads advertisement creative for {product/service},
{detailed visual scene description},
text overlay displaying "{headline text}" at top in bold sans-serif font,
"{body copy text}" in middle section with medium weight font,
"{CTA text}" on {color} button at bottom,
color palette featuring {hex codes},
{composition style description},
professional commercial photography aesthetic,
high contrast for mobile readability,
photorealistic style,
modern marketing design
```

### Best Practices

**Text Rendering**:
✅ Specify exact text in quotes
✅ Include text placement details
✅ Specify font characteristics
✅ Add backgrounds for readability

**Visual Quality**:
✅ Be highly descriptive (detailed scenes work best)
✅ Include lighting descriptions
✅ Define composition clearly
✅ Use natural, conversational language

**Brand Consistency**:
✅ Include exact hex color codes
✅ Describe color usage explicitly
✅ Reference photography style

## Post-Processing

Resize to Meta Ads optimal size (1080px):

```python
from PIL import Image

# Load generated image
img = Image.open('gemini_output.png')

# Resize to Meta specs
# Square: → 1080×1080
img_resized = img.resize((1080, 1080), Image.Resampling.LANCZOS)

# Vertical: → 1080×1920
img_resized = img.resize((1080, 1920), Image.Resampling.LANCZOS)

# Save with high quality
img_resized.save('final_creative.png', quality=95)
```

## Aspect Ratios

| Format | Aspect Ratio | Meta Spec |
|--------|-------------|-----------|
| Feed Square | `"1:1"` | 1080×1080 |
| Stories/Reels | `"9:16"` | 1080×1920 |

## Performance

**Generation Time**: 10-30 seconds per image
**Quality**: Excellent for Meta Ads
**Reliability**: Very high (Google infrastructure)
**Max images per call**: 10

## Agent 5 Integration

### Automated Workflow

Agent 5 automatically:
1. ✅ Loads API key from environment (`GOOGLE_API_KEY`)
2. ✅ Builds descriptive prompts from brief
3. ✅ Calls Gemini 2.5 Flash Image API with optimal parameters
4. ✅ Decodes and saves generated images
5. ✅ Resizes to Meta specifications (1080px)
6. ✅ Saves to organized folders

**No manual intervention required** - just run `/agent5-designer`!

## Troubleshooting

### "Invalid API key"
**Solution**: Verify `GOOGLE_API_KEY` in `.env` file is correct. Get key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### API rate limit errors
**Solution**:
- Wait and retry
- Upgrade Google AI Studio plan for higher limits
- Implement exponential backoff in code

### Text not rendering correctly
**Solution**:
- Put all text in explicit quotes in prompt
- Be very descriptive about placement
- Add background overlays for contrast

### Images too artistic/surreal
**Solution**:
- Include "photorealistic" in prompt
- Add "professional commercial photography"
- Be more specific about the scene

## Monitoring

### Google AI Studio Dashboard
- View usage: [aistudio.google.com](https://aistudio.google.com)
- Monitor costs
- Check rate limits

## Security

**API Key Security**:
- ⚠️ Never commit API keys to git
- ⚠️ Add to `.gitignore`: `.env`
- ✅ Use environment variables for production
- ✅ Rotate keys periodically

**.gitignore**:
```
.env
*.env
.env.*
```

## Advantages over DALL-E 3

1. **Lower cost** — Cheaper per image
2. **Multiple images per call** — Up to 10 images in one request
3. **Better aspect ratio support** — Native 1:1 and 9:16
4. **Google infrastructure** — High reliability
5. **Latest model** — Gemini 2.5 generation ("Nano Banana")

## Next Steps

1. ✅ Get `GOOGLE_API_KEY` from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. ✅ Add key to `.env` file
3. ✅ Install `google-genai`: `pip install google-genai`
4. ✅ Agent 5 updated for Gemini 2.5 Flash Image
5. ✅ Ready to generate creatives!

**Test it:**
```
/agent5-designer
```

System will generate professional Meta Ads creatives using Gemini 2.5 Flash Image (Nano Banana)! 🚀
