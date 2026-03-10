# Midjourney Integration via Apify - Setup Guide

## Overview
Agent 5 uses **Midjourney v6.1** through Apify's `igolaizola/midjourney-automation` actor for professional-quality ad creative generation.

## Prerequisites

### 1. Midjourney Subscription
**Required**: Active Midjourney subscription

Plans:
- **Basic** ($10/month) - 200 images/month (FastGPU)
- **Standard** ($30/month) - Unlimited Relax + 15h Fast
- **Pro** ($60/month) - Unlimited Relax + 30h Fast + Stealth

**Recommended**: Standard plan ($30/month) for production use

Get subscription at: [midjourney.com/account](https://www.midjourney.com/account)

### 2. Apify Account
**Free tier**: $5/month credits included

Sign up at: [apify.com](https://apify.com)

### 3. Environment Variables
Already configured in `.env`:
```bash
APIFY_TOKEN=apify_api_3s7b2d3YImw5TnVfQXwIbLRyEo5jam1BEmD9
```

## Setup Steps

### Step 1: Get Midjourney Cookies

**Why needed**: The Apify actor authenticates to Midjourney using your session cookies.

**How to get cookies**:

1. **Install Cookie-Editor** browser extension:
   - Chrome: [Cookie-Editor for Chrome](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
   - Firefox: [Cookie-Editor for Firefox](https://addons.mozilla.org/firefox/addon/cookie-editor/)

2. **Login to Midjourney**:
   - Go to [www.midjourney.com](https://www.midjourney.com)
   - Sign in with your account (via Discord)
   - Verify you're fully logged in

3. **Export cookies**:
   - Click Cookie-Editor extension icon
   - Click "Export" button
   - Choose "Export as JSON"
   - Save the JSON file

4. **Use cookies in Agent 5**:
   The cookies JSON will look like:
   ```json
   [
     {
       "domain": ".midjourney.com",
       "name": "__Secure-next-auth.session-token",
       "value": "YOUR_SESSION_TOKEN_HERE",
       ...
     },
     ...
   ]
   ```

### Step 2: Configure MCP

Already done! The config is updated:
```json
{
  "apify": {
    "env": {
      "APIFY_TOKEN": "${APIFY_TOKEN}",
      "APIFY_ACTORS": "curious_coder/facebook-ads-library-scraper,igolaizola/midjourney-automation"
    }
  }
}
```

### Step 3: Store Cookies

**Option A: Environment Variable** (Recommended for single user)
```bash
# Add to .env file
MIDJOURNEY_COOKIES='[{"domain":".midjourney.com",...}]'
```

**Option B: JSON File** (Recommended for production)
```bash
# Save cookies to file
echo '[...]' > /Users/mikeinishev/Antigravity/Ad\ creatives\ machine\=\]/config/midjourney_cookies.json
```

## Usage in Agent 5

### Basic Syntax

```javascript
apify.run_actor(
  actor_id: "igolaizola/midjourney-automation",
  input: {
    "cookies": [/* your cookies JSON */],
    "prompts": ["your prompt here --ar 1:1 --v 6.1 --style raw --q 2"],
    "concurrency": 3  // process 3 images simultaneously
  }
)
```

### Full Example

```javascript
apify.run_actor(
  actor_id: "igolaizola/midjourney-automation",
  input: {
    "cookies": process.env.MIDJOURNEY_COOKIES,  // or read from file
    "prompts": [
      "Professional Meta Ads creative for restaurant loyalty app, split screen composition... --ar 1:1 --v 6.1 --style raw --q 2",
      "Professional Meta Ads creative for Instagram Stories... --ar 9:16 --v 6.1 --style raw --q 2"
    ],
    "concurrency": 3,
    "upscale": true,  // automatically upscale best results
    "save": true  // save to album.html
  }
)
```

### Agent 5 Workflow

Agent 5 automatically:
1. ✅ Loads cookies from environment/file
2. ✅ Builds Midjourney-optimized prompts
3. ✅ Calls Apify actor with prompts
4. ✅ Waits for generation (30-90s each)
5. ✅ Downloads images from result
6. ✅ Saves to `outputs/creatives/{brief_id}/`

## Midjourney Parameters

### Essential Parameters

**--ar [ratio]**: Aspect ratio
- `1:1` for Square (1080x1080) Feed ads
- `9:16` for Vertical (1080x1920) Stories ads
- `16:9` for Horizontal (landscape)

**--v 6.1**: Version
- Latest Midjourney model
- Best text rendering
- Most photorealistic

**--style raw**: Style mode
- `raw` = Less artistic, more literal (BEST for ads)
- `natural` = Photographic
- Remove for default artistic style

**--q 2**: Quality
- `1` = Standard quality (faster, testing)
- `2` = High quality (slower, production)

**--chaos [0-100]**: Variation
- `0` = Very consistent
- `0-20` = Slight variation (recommended for ads)
- `50+` = High variation (avoid for brand consistency)

### Advanced Parameters

**--no [element]**: Remove unwanted elements
```
--no watermark, text, logos
```

**--s [0-1000]**: Stylization
- `0` = Very literal
- `100` = Default
- `250+` = Very artistic (avoid for ads)

**--seed [number]**: Reproducibility
- Use same seed for consistent variations

## Prompt Engineering for Ads

### Structure

```
[Professional Meta Ads creative description],
[detailed visual scene],
text overlay: "[exact text]" at [position] in [style],
"[more text]" in [position],
"[cta]" on [color] button at [position],
color palette: [hex codes],
[composition style],
professional marketing photography,
high contrast for mobile,
--ar [ratio] --v 6.1 --style raw --q 2
```

### Best Practices

**Text Rendering**:
✅ Put all text in quotes: "Losing customers to DoorDash?"
✅ Specify exact placement: "at top center"
✅ Include font details: "bold sans-serif white text"
✅ Add backgrounds: "on dark semi-transparent background"

**Visual Quality**:
✅ Use "professional photography" not "stock photo"
✅ Specify lighting: "realistic natural lighting"
✅ Be specific: "split screen composition" not "interesting layout"
✅ Avoid artistic terms: No "surreal", "abstract", "painterly"

**Brand Consistency**:
✅ Include exact hex codes: "#FF6B35", "#004E89"
✅ Describe brand style: "modern tech aesthetic"
✅ Stay literal: Use `--style raw` always

## Cost Management

**Pricing breakdown**:
- Midjourney subscription: $10-60/month (fixed)
- Apify usage: $0.02-0.04 per image
- Per brief (6 images): ~$0.12-0.24
- For 3 briefs (18 images): ~$0.36-0.72

**Monthly estimate** (10 briefs/month):
- Midjourney Standard: $30
- Apify (60 images): ~$1.20-2.40
- **Total**: ~$31.20-32.40/month

**Optimization tips**:
- Use `--q 1` for testing iterations
- Generate final versions with `--q 2`
- Process multiple prompts in parallel (concurrency: 3)
- Monitor Apify dashboard for usage

## Troubleshooting

### "Authentication failed"
**Solution**: Cookies expired, export new cookies from midjourney.com

### "Midjourney subscription required"
**Solution**: Verify active subscription at midjourney.com/account

### Text not rendering correctly
**Solution**: 
- Put text in explicit quotes
- Add background: "on semi-transparent dark overlay"
- Simplify font: Just "bold sans-serif"

### Images too artistic
**Solution**:
- Always use `--style raw`
- Include "professional photography"
- Avoid artistic adjectives

### Slow generation
**Solution**:
- Midjourney typically 30-90s per image
- Use concurrency for parallel processing
- Check Midjourney server status

## Monitoring

### Apify Dashboard
- View runs: console.apify.com
- Monitor credits used
- Check actor logs
- Download album.html gallery

### Midjourney Account
- View generation history
- Check subscription status
- Monitor fast hours usage (Standard/Pro)

## Security

**Cookies security**:
- ⚠️ Never commit cookies to git
- ⚠️ Add to `.gitignore`: `midjourney_cookies.json`, `.env`
- ✅ Use environment variables for production
- ✅ Rotate cookies monthly

**.gitignore**:
```
.env
config/midjourney_cookies.json
*.cookies.json
```

## Workflow Integration

Agent 5 workflow automatically handles:
1. ✅ Cookie loading from environment
2. ✅ Prompt building with Midjourney syntax
3. ✅ Apify actor invocation
4. ✅ Result downloading
5. ✅ File organization

**No manual intervention required** - just run `/agent5-designer`!

## Next Steps

1. ✅ Get Midjourney subscription ($30/month recommended)
2. ✅ Export cookies from midjourney.com
3. ✅ Add cookies to .env or config file
4. ✅ Test with single prompt via Agent 5
5. ✅ Run full creative generation workflow

System is ready to generate professional Meta Ads creatives! 🚀
