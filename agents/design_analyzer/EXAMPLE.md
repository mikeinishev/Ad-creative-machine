# Example: Quiz Funnel Design Analysis

This is a reference example showing expected input and output for Agent 1.

## Sample Input

**Format**: Figma URL (but could be PDF, URL, or images)

```
https://figma.com/file/ABC123/Quiz-Funnel-Design
```

## Analysis Process

### Screen 1: Welcome Screen
- **Type**: Welcome
- **Headline**: "What's Your Marketing Superpower?"
- **Subheadline**: "Take this 60-second quiz to discover your hidden strengths"
- **CTA**: "Start Quiz →"
- **Visual Elements**: 
  - Hero illustration (cartoon character)
  - Logo (top left)
  - Trust badges (bottom)
- **Colors**: #6366F1 (primary), #F59E0B (accent), #FFFFFF (background)
- **Typography**: Poppins Bold (headlines), Inter Regular (body)

### Screen 2-4: Question Screens
Each has:
- Question prompt
- 3-4 multiple choice options (buttons)
- Progress bar (e.g., "2 of 3")
- Same color scheme and typography

### Screen 5: Result Screen
- **Type**: Result
- **Headline**: "You're a [Result Type]!"
- **Subheadline**: "Here's what that means..."
- **Content**: Personalized description
- **CTA**: "Get Your Custom Plan →"

### Screen 6: Offer Screen
- **Type**: Offer
- **Headline**: "Ready to unlock your potential?"
- **Offer**: "Custom Marketing Strategy Session - $497 $297"
- **CTA**: "Book Your Session"
- **Trust elements**: Money-back guarantee, testimonials

## Expected JSON Output

```json
{
  "funnel_structure": {
    "screens": [
      {
        "id": "welcome",
        "type": "welcome",
        "headline": "What's Your Marketing Superpower?",
        "subheadline": "Take this 60-second quiz to discover your hidden strengths",
        "cta_text": "Start Quiz →",
        "visual_elements": ["hero_illustration", "logo", "trust_badges"],
        "color_scheme": ["#6366F1", "#F59E0B", "#FFFFFF"],
        "typography": {
          "heading": "Poppins Bold",
          "body": "Inter Regular"
        }
      },
      {
        "id": "question_1",
        "type": "question",
        "headline": "What's your biggest marketing challenge?",
        "subheadline": "",
        "cta_text": "Next →",
        "visual_elements": ["progress_bar", "icon"],
        "color_scheme": ["#6366F1", "#F59E0B", "#FFFFFF"],
        "typography": {
          "heading": "Poppins Bold",
          "body": "Inter Regular"
        }
      },
      {
        "id": "question_2",
        "type": "question",
        "headline": "How much time do you spend on marketing weekly?",
        "subheadline": "",
        "cta_text": "Next →",
        "visual_elements": ["progress_bar", "icon"],
        "color_scheme": ["#6366F1", "#F59E0B", "#FFFFFF"],
        "typography": {
          "heading": "Poppins Bold",
          "body": "Inter Regular"
        }
      },
      {
        "id": "question_3",
        "type": "question",
        "headline": "What's your primary business goal?",
        "subheadline": "",
        "cta_text": "See Results →",
        "visual_elements": ["progress_bar", "icon"],
        "color_scheme": ["#6366F1", "#F59E0B", "#FFFFFF"],
        "typography": {
          "heading": "Poppins Bold",
          "body": "Inter Regular"
        }
      },
      {
        "id": "result",
        "type": "result",
        "headline": "You're a Strategic Visionary!",
        "subheadline": "Here's what that means...",
        "cta_text": "Get Your Custom Plan →",
        "visual_elements": ["result_badge", "description_text"],
        "color_scheme": ["#6366F1", "#F59E0B", "#FFFFFF"],
        "typography": {
          "heading": "Poppins Bold",
          "body": "Inter Regular"
        }
      },
      {
        "id": "offer",
        "type": "offer",
        "headline": "Ready to unlock your potential?",
        "subheadline": "Custom Marketing Strategy Session",
        "cta_text": "Book Your Session",
        "visual_elements": ["pricing", "testimonials", "guarantee_badge"],
        "color_scheme": ["#6366F1", "#F59E0B", "#FFFFFF"],
        "typography": {
          "heading": "Poppins Bold",
          "body": "Inter Regular"
        }
      }
    ],
    "flow": ["welcome", "question_1", "question_2", "question_3", "result", "offer"],
    "brand_assets": {
      "logo_url": "https://...",
      "color_palette": ["#6366F1", "#F59E0B", "#FFFFFF", "#1F2937"]
    }
  }
}
```

## Summary Markdown

```markdown
# Design Analysis Summary
Date: 2024-01-15 10:30:00
Input: https://figma.com/file/ABC123/Quiz-Funnel-Design
Format: Figma

## Funnel Structure
- Total screens: 6
- Flow: Welcome → 3 Questions → Result → Offer

## Brand Identity
- **Primary color**: #6366F1 (Indigo)
- **Accent color**: #F59E0B (Amber)
- **Typography**: Poppins Bold (headings), Inter Regular (body)
- **Style**: Modern, friendly, professional

## Key Elements
- **Main headline**: "What's Your Marketing Superpower?"
- **Primary CTA**: "Start Quiz →"
- **Visual style**: Illustrated, colorful, engaging
- **Trust elements**: Badges, testimonials, guarantee

## Screen Breakdown

### Welcome Screen
- Sets the tone with engaging question-based headline
- Clear value prop in subheadline (60 seconds, discover strengths)
- Strong CTA with arrow suggesting forward movement

### Question Screens (3)
- Consistent layout and styling
- Progress indicator builds momentum
- Multiple choice format (3-4 options each)

### Result Screen
- Personalized outcome ("You're a Strategic Visionary!")
- Descriptive content validates the user
- Transitions to offer with "Get Your Custom Plan" CTA

### Offer Screen
- Clear pricing with discount ($497 → $297)
- Social proof via testimonials
- Risk reversal with guarantee
- Strong CTA: "Book Your Session"
```

This example demonstrates the level of detail and structure expected from Agent 1's analysis.
