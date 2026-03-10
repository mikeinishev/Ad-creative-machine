"""
Creative Strategist Agent - Synthesis Utilities
Handles data integration, opportunity scoring, and brief generation
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple


def load_agent_outputs(
    design_path: str,
    marketing_path: str,
    competitor_path: str
) -> Tuple[Dict, Dict, Dict]:
    """
    Load outputs from Agents 1-3
    
    Returns:
        Tuple of (design_data, marketing_data, competitor_data)
    """
    with open(design_path) as f:
        design = json.load(f)
    
    with open(marketing_path) as f:
        marketing = json.load(f)
    
    with open(competitor_path) as f:
        competitor = json.load(f)
    
    return design, marketing, competitor


def score_opportunity(
    audience: Dict[str, Any],
    vp: Dict[str, Any],
    hook_type: str,
    competitor_patterns: Dict[str, Any],
    brand_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Score a creative opportunity based on multiple factors
    
    Args:
        audience: Audience segment from Agent 2
        vp: Value proposition from Agent 2
        hook_type: Hook type (pain, benefit, curiosity, etc.)
        competitor_patterns: Pattern data from Agent 3
        brand_data: Brand assets from Agent 1
        
    Returns:
        Scored opportunity dict
    """
    score = 0
    reasoning = []
    
    # 1. Audience Size Factor (estimate from demographics)
    demographics = audience.get("demographics", "").lower()
    if "large" in demographics or "smb" in demographics:
        score += 4
        reasoning.append("Large target market")
    elif "medium" in demographics or "multi" in demographics:
        score += 3
    else:
        score += 2
    
    # 2. Competitor Saturation
    hook_dist = competitor_patterns.get("hook_distribution", {})
    total_hooks = sum(hook_dist.values())
    hook_count = hook_dist.get(hook_type, 0)
    saturation = hook_count / total_hooks if total_hooks > 0 else 0
    
    if saturation < 0.2:  # Low saturation = gap
        score += 3
        reasoning.append(f"Gap opportunity ({hook_type} underutilized)")
    elif saturation < 0.4:
        score += 2
    else:
        score += 1
        reasoning.append(f"Competitive space ({hook_type} common)")
    
    # 3. Hook Effectiveness
    if saturation > 0.3:  # Proven
        score += 3
        reasoning.append(f"{hook_type} proven in competitors")
    elif saturation > 0.15:
        score += 2
    else:
        score += 1
    
    # 4. Brand Fit (simplified - check if VP mentions brand values)
    # This is a simplified version; real implementation would be more sophisticated
    score += 1  # Default moderate fit
    
    return {
        "audience": audience.get("segment", "unknown"),
        "vp": vp.get("id", "unknown"),
        "hook_type": hook_type,
        "score": score,
        "reasoning": " + ".join(reasoning)
    }


def build_opportunity_matrix(
    audiences: List[Dict],
    vps: List[Dict],
    competitor_patterns: Dict[str, Any],
    brand_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Build and score all opportunity combinations
    
    Returns:
        List of opportunities sorted by score (descending)
    """
    opportunities = []
    
    # Get hook types from competitor data
    hook_dist = competitor_patterns.get("hook_distribution", {})
    hook_types = list(hook_dist.keys()) if hook_dist else ["pain", "benefit", "curiosity"]
    
    for audience in audiences:
        for vp in vps:
            for hook_type in hook_types:
                opp = score_opportunity(
                    audience, vp, hook_type,
                    competitor_patterns, brand_data
                )
                opportunities.append(opp)
    
    # Sort by score descending
    opportunities.sort(key=lambda x: x["score"], reverse=True)
    
    return opportunities


def generate_hook_variations(
    hook_type: str,
    pain_points: List[str],
    vp_headline: str,
    offer_type: str
) -> List[Dict[str, str]]:
    """
    Generate 3 hook variations (A/B/C) for testing
    
    Returns:
        List of 3 variation dicts
    """
    variations = []
    
    if hook_type == "pain":
        # A: Direct question
        variations.append({
            "variant": "A",
            "hook_variation": f"{pain_points[0]}?",
            "reasoning": "Direct pain point question (proven format)"
        })
        
        # B: Emotional amplification
        variations.append({
            "variant": "B",
            "hook_variation": f"Tired of {pain_points[0].lower()}?",
            "reasoning": "Emotional trigger (tired of pattern)"
        })
        
        # C: Benefit flip
        benefit = vp_headline.split()[:5]  # First 5 words
        variations.append({
            "variant": "C",
            "hook_variation": f"What if " + " ".join(benefit).lower() + "?",
            "reasoning": "Benefit-curiosity hybrid (gap test)"
        })
    
    elif hook_type == "benefit":
        # A: Direct promise
        variations.append({
            "variant": "A",
            "hook_variation": vp_headline,
            "reasoning": "Direct VP headline (proven)"
        })
        
        # B: Time-bound
        variations.append({
            "variant": "B",
            "hook_variation": f"Get {vp_headline.lower()} in 30 days",
            "reasoning": "Time-bound promise (urgency)"
        })
        
        # C: Question format
        variations.append({
            "variant": "C",
            "hook_variation": f"Ready to {vp_headline.lower()}?",
            "reasoning": "Question format benefit (softer)"
        })
    
    else:  # curiosity, social_proof, etc.
        # Generic fallback
        variations.append({
            "variant": "A",
            "hook_variation": vp_headline,
            "reasoning": "VP headline as hook"
        })
        variations.append({
            "variant": "B",
            "hook_variation": f"Discover: {vp_headline}",
            "reasoning": "Curiosity prefix"
        })
        variations.append({
            "variant": "C",
            "hook_variation": pain_points[0] if pain_points else vp_headline,
            "reasoning": "Alternative angle"
        })
    
    return variations


def create_brief_from_opportunity(
    opp: Dict[str, Any],
    audiences: List[Dict],
    vps: List[Dict],
    pain_points: List[str],
    offers: List[Dict],
    brand_colors: List[str],
    reference_ads: List[str],
    brief_id: str
) -> Dict[str, Any]:
    """
    Generate full creative brief from opportunity
    
    Returns:
        Complete brief dict
    """
    # Find full audience and VP data
    audience = next((a for a in audiences if a.get("segment") == opp["audience"]), {})
    vp = next((v for v in vps if v.get("id") == opp["vp"]), {})
    
    # Determine priority
    score = opp["score"]
    if score >= 10:
        priority = "high"
    elif score >= 7:
        priority = "medium"
    else:
        priority = "low"
    
    # Get offer for CTA
    offer = offers[0] if offers else {"type": "trial"}
    offer_type = offer.get("type", "trial")
    
    cta_map = {
        "trial": "Start Free Trial →",
        "lead_magnet": "Get Free Guide →",
        "webinar": "Save Your Spot →",
        "quiz": "Take the Quiz →",
        "demo": "Schedule Demo →",
        "discount": "Claim Offer →"
    }
    cta = cta_map.get(offer_type, "Learn More →")
    
    # Generate variations
    variations = generate_hook_variations(
        opp["hook_type"],
        pain_points,
        vp.get("headline", ""),
        offer_type
    )
    
    # Build brief
    brief = {
        "id": brief_id,
        "concept_name": f"{opp['hook_type'].title()} Hook - {audience.get('segment', 'Unknown')}",
        "target_audience": opp["audience"],
        "value_proposition": opp["vp"],
        "priority": priority,
        "format": "static",
        "dimensions": ["1080x1080", "1080x1920"],
        "creative_direction": {
            "hook": variations[0]["hook_variation"],  # Use Variant A as primary
            "body": vp.get("headline", "") + ". " + (vp.get("supporting_points", [""])[0] if vp.get("supporting_points") else ""),
            "cta": cta,
            "visual_concept": f"{opp['hook_type']}-based visual with clear {offer_type} offer",
            "color_scheme": brand_colors[:3] if brand_colors else ["#FF6B35", "#004E89", "#FFFFFF"],
            "typography_style": "bold" if opp["hook_type"] in ["pain", "urgency"] else "professional",
            "imagery": [
                f"target_audience_{audience.get('segment', 'customer')}",
                "product_benefit_visual",
                "cta_visual_cue"
            ]
        },
        "variations": variations,
        "reference_creatives": reference_ads[:2],  # Top 2 references
        "reasoning": opp["reasoning"]
    }
    
    return brief


def create_strategist_output_paths(base_dir: str = "outputs/briefs") -> Dict[str, str]:
    """Create timestamped output paths for creative briefs"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    Path(f"{base_dir}/individual").mkdir(parents=True, exist_ok=True)
    
    return {
        "master_json": f"{base_dir}/creative_briefs_{timestamp}.json",
        "summary": f"{base_dir}/creative_briefs_{timestamp}_summary.md",
        "individual_dir": f"{base_dir}/individual"
    }


# Example usage
if __name__ == "__main__":
    print("""
Creative Strategist - Synthesis Utilities

Usage:
1. Load outputs from Agents 1-3
2. Build opportunity matrix
3. Score and rank opportunities
4. Select top concepts
5. Generate creative briefs

Example:
    design, marketing, competitor = load_agent_outputs(
        "outputs/analysis/design_*.json",
        "outputs/analysis/marketing_*.json",
        "outputs/competitor_intel/data_*.json"
    )
    
    opportunities = build_opportunity_matrix(
        marketing["audiences"],
        marketing["value_propositions"],
        competitor["patterns"],
        design["funnel_structure"]["brand_assets"]
    )
    
    # Top 5 opportunities
    top_5 = opportunities[:5]
    
    # Generate briefs
    for i, opp in enumerate(top_5):
        brief = create_brief_from_opportunity(...)
""")
