# Agent 4 v3: Image Generation Prompts

## 📊 Техническое Задание для Agent 5

**Версия**: v3 (Technical Specifications)  
**Источник**: Топ-10 концепций из 12 креативных брифов  
**Результат**: 20 детальных промптов (10 концепций × 2 формата)

---

## 🎯 Топ-10 Концепций (Priority Order)

1. **Brief #001**: 10K MRR Income Transformation
2. **Brief #002**: 1,800+ Partners Social Proof
3. **Brief #007**: Zero Cold Calling
4. **Brief #004**: 89% CNBC Authority Stat
5. **Brief #003**: Zero-Risk Partnership
6. **Brief #010**: 2-Day Onboarding Speed
7. **Brief #012**: Restaurant Niche Specialization
8. **Brief #005**: Recurring Revenue Machine
9. **Brief #008**: Proven Implementation System
10. **Brief #009**: Remote Work Freedom

---

## 📐 Структура Промптов

Каждая концепция имеет **2 детальных промпта**:

### Format 1: Instagram Feed (1080x1080)
- Aspect Ratio: 1:1 (Square)
- Layout specifications
- Text overlay guidelines
- Key visual elements
- Color palette
- Typography specs
- Design tone

### Format 2: Instagram Stories (1080x1920)
- Aspect Ratio: 9:16 (Vertical)
- Vertical layout breakdown (Top → Bottom)
- Section percentages (20% / 20% / 30% / 20% / 10%)
- Mobile-first optimizations
- CTA button specs

---

## 🎨 Brand System (Applied to All)

**Colors**:
- Primary: `#6460aa` (Brand Purple)
- Accent: `#0db14b` (Success Green)
- Background: `#FFFFFF` (White)
- Text: `#2a2832` (Dark Gray)

**Typography**: Aeonik-style modern sans-serif

**Tone**: Professional, data-driven, aspirational

---

## 📝 Example Prompt (Brief #001 Feed)

```
Professional Instagram feed ad (1080x1080, square format) for B2B partner program.

CONCEPT: 10K MRR Income Transformation

LAYOUT: Income transformation chart: $0 → $10,000 progression

TEXT OVERLAY:
- Main Headline (top, bold, 44-48px): "Turn 4-8 hours/week into $10,000 recurring monthly income..."
- Supporting text from brief
- CTA button at bottom

KEY VISUAL ELEMENTS:
- Income growth graph
- Time badge (4-8 hrs/week)
- 1,800+ partners badge

COLOR PALETTE:
- Primary: #6460aa (brand purple)
- Accent: #0db14b (success green)
- Background: #FFFFFF
- Text: #2a2832

TYPOGRAPHY: Aeonik-style modern sans-serif, bold headlines

TONE: Aspirational, data-driven

DESIGN STYLE: Clean, professional, mobile-optimized with clear visual hierarchy
```

---

## 📂 Output File

**Full JSON**: [`image_generation_prompts.json`](file:///Users/mikeinishev/Antigravity/Ad%20creatives%20machine=%5D/outputs/briefs/image_generation_prompts.json)

**Structure**:
```json
{
  "meta": {...},
  "brand_assets": {...},
  "image_prompts": [
    {
      "brief_id": "brief_001",
      "concept_name": "10K MRR Income Transformation",
      "target_audience": "...",
      "hook": "...",
      "formats": [
        {
          "format_name": "Instagram Feed",
          "dimensions": "1080x1080",
          "aspect_ratio": "1:1",
          "detailed_prompt": "..."
        },
        {
          "format_name": "Instagram Stories/Reels",
          "dimensions": "1080x1920",
          "aspect_ratio": "9:16",
          "detailed_prompt": "..."
        }
      ]
    },
    ...
  ]
}
```

---

## 🚀 Usage for Agent 5

### How to Use These Prompts

1. Load `image_generation_prompts.json`
2. For each concept, extract `formats[0].detailed_prompt` (Feed) and `formats[1].detailed_prompt` (Stories)
3. Pass prompts to `generate_image` tool
4. Save outputs to `outputs/creatives/brief_XXX/`

### Generation Priority

**Wave 1** (Already Done ✅):
- Brief #001, #002, #007 (6 creatives)

**Wave 2** (Next):
- Brief #004, #003, #010 (6 creatives)

**Wave 3**:
- Brief #012, #005, #008 (6 creatives)

**Wave 4**:
- Brief #009 (2 creatives)

**Total**: 20 creatives

---

## 🔗 Related Files

- **Creative Briefs v2**: [`creative_briefs.json`](file:///Users/mikeinishev/Antigravity/Ad%20creatives%20machine=%5D/outputs/briefs/creative_briefs.json)
- **Brief Summary**: [`creative_briefs_summary.md`](file:///Users/mikeinishev/Antigravity/Ad%20creatives%20machine=%5D/outputs/briefs/creative_briefs_summary.md)
- **Already Generated**: [`production_summary.md`](file:///Users/mikeinishev/Antigravity/Ad%20creatives%20machine=%5D/outputs/creatives/production_summary.md)
