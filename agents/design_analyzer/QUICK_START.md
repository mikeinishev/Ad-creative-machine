# Agent 1: Design Analyzer - Quick Start

## Purpose
Extracts structured design information from quiz funnels in any format (Figma, PDF, URL, images).

## How to Use

### 1. Prepare Your Input

Choose one of these input formats:

- **Figma URL**: `https://figma.com/file/YOUR_FILE_ID/Quiz-Design`
- **PDF file**: Place in `inputs/` folder
- **Landing page**: Any live quiz URL
- **Screenshots**: Place images in `inputs/` folder

### 2. Run the Workflow

Use the workflow: `/agent1-design-analyzer`

Provide your input when prompted:
```
Input: https://figma.com/file/ABC123/My-Quiz-Design
```

### 3. Review Output

Find your analysis in:
```
outputs/analysis/
├── design_20240115_103000.json          # Structured data
├── design_20240115_103000_summary.md    # Human-readable summary
└── design_20240115_103000_metadata.json # Processing metadata
```

## What You'll Get

### Structured JSON Data
```json
{
  "funnel_structure": {
    "screens": [...],      // All quiz screens with details
    "flow": [...],         // Screen sequence
    "brand_assets": {...}  // Colors, logo, typography
  }
}
```

### Summary Report
- Funnel overview (# screens, flow)
- Brand identity (colors, fonts, style)
- Screen-by-screen breakdown
- Key headlines and CTAs

## Use Cases

### For Agent 2 (Marketing Analyst)
The design analysis provides:
- Visual style context for landing page analysis
- Brand assets to match creative briefs to
- Quiz structure to understand the funnel

### For Agent 4 (Creative Strategist)
The design analysis provides:
- Brand colors for creative direction
- Typography styles to maintain consistency
- Visual elements to reference in briefs

### Standalone Use
- Document existing quiz designs
- Compare multiple quiz versions
- Extract copy for other purposes

## Examples

### Example 1: Figma File
```
Input: https://figma.com/file/ABC123/SaaS-Quiz-Funnel
Output: 
- 6 screens identified (welcome, 3 questions, result, offer)
- Primary color: #4F46E5
- Typography: Inter + Poppins
```

### Example 2: Live Quiz
```
Input: https://example.com/marketing-quiz
Output:
- 5 screens captured via screenshots
- Flow: Welcome → Q1 → Q2 → Result → Offer
- CTA progression mapped
```

### Example 3: PDF Design Mockup
```
Input: ./inputs/quiz-mockup.pdf
Output:
- 8 pages analyzed
- Each screen classified by type
- Text extracted from visual designs
```

## Tips for Best Results

1. **For Figma files**: 
   - Ensure file is shared publicly or you have access
   - Organize frames in order (left to right or top to bottom)
   - Name frames clearly (e.g., "Screen 1: Welcome")

2. **For PDF files**:
   - One screen per page works best
   - Use high-resolution exports
   - Include all quiz screens in sequence

3. **For URLs**:
   - Quiz should be publicly accessible
   - Avoid login-required quizzes (unless you can provide credentials)
   - Single-page quizzes work better than multi-page

4. **For images**:
   - Name files in order (screen1.png, screen2.png)
   - Use clear, high-quality screenshots
   - Include full screen, not cropped portions

## Troubleshooting

**"Cannot access Figma file"**
- Check if file is public or shared with your Figma account
- Verify FIGMA_ACCESS_TOKEN is set correctly

**"PDF parsing failed"**
- Ensure PDF is not password-protected
- Try exporting PDF pages as images instead

**"URL not accessible"**
- Check if page requires login
- Verify URL is correct and live
- Try using screenshots instead

## Next Steps

After getting design analysis:
1. Use output JSON with Agent 2 for marketing analysis
2. Reference brand assets when generating creatives
3. Keep for documentation and version comparison

## Files Reference

- **Workflow**: `.agent/workflows/agent1-design-analyzer.md`
- **System Prompt**: `agents/design_analyzer/AGENT_PROMPT.md`
- **Example Output**: `agents/design_analyzer/EXAMPLE.md`
- **Output Schema**: `shared/schemas/design_analysis.json`
