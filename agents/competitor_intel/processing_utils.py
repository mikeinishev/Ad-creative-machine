"""
Competitor Intel Agent - Processing Utilities
Handles Apify data processing, creative analysis, and report generation
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from urllib.parse import quote_plus, urlencode


def generate_search_queries(value_propositions: List[Dict[str, Any]]) -> List[str]:
    """
    Generate Meta Ads search queries from value propositions
    
    Args:
        value_propositions: List of VP dicts from Agent 2
        
    Returns:
        List of search query strings
    """
    queries = []
    
    for vp in value_propositions:
        # Use VP headline as base
        headline = vp.get("headline", "")
        if headline:
            # Extract 3-4 key words
            words = headline.split()[:4]
            query = " ".join(words)
            queries.append(query)
        
        # Use unique mechanism if available
        mechanism = vp.get("unique_mechanism", "")
        if mechanism:
            queries.append(mechanism)
    
    # Deduplicate
    return list(set(queries))


def construct_meta_ads_url(query: str, country: str = "US") -> str:
    """
    Construct Meta Ads Library search URL
    
    Args:
        query: Search term
        country: Country code (US, CA, etc.)
        
    Returns:
        Full URL for Meta Ads Library
    """
    base_url = "https://www.facebook.com/ads/library/"
    params = {
        "active_status": "active",
        "ad_type": "all",
        "country": country,
        "q": query
    }
    
    return f"{base_url}?{urlencode(params)}"


def calculate_days_active(start_date_unix: int) -> int:
    """
    Calculate days an ad has been active
    
    Args:
        start_date_unix: Unix timestamp of ad start
        
    Returns:
        Number of days active
    """
    current_timestamp = int(datetime.now().timestamp())
    seconds_active = current_timestamp - start_date_unix
    days_active = seconds_active // 86400  # Seconds in a day
    
    return int(days_active)


def classify_creative(ad_copy: str, visual_data: Dict = None) -> Dict[str, str]:
    """
    Classify creative by hook type, offer type, visual style
    
    Args:
        ad_copy: Ad text content
        visual_data: Optional visual analysis data
        
    Returns:
        Classification dict with hook_type, offer_type, visual_style, cta_type
    """
    ad_copy_lower = ad_copy.lower()
    
    # Hook type classification
    hook_type = "benefit"  # default
    if any(word in ad_copy_lower for word in ["tired of", "struggling", "frustrated", "problem"]):
        hook_type = "pain"
    elif any(word in ad_copy_lower for word in ["secret", "how to", "discover", "learn"]):
        hook_type = "curiosity"
    elif any(word in ad_copy_lower for word in ["users", "customers", "featured", "trusted"]):
        hook_type = "social_proof"
    elif any(word in ad_copy_lower for word in ["limited", "only", "hurry", "today only"]):
        hook_type = "urgency"
    
    # Offer type classification
    offer_type = "trial"  # default
    if any(word in ad_copy_lower for word in ["free guide", "ebook", "checklist", "download"]):
        offer_type = "lead_magnet"
    elif any(word in ad_copy_lower for word in ["% off", "discount", "save"]):
        offer_type = "discount"
    elif any(word in ad_copy_lower for word in ["webinar", "workshop", "event"]):
        offer_type = "webinar"
    elif any(word in ad_copy_lower for word in ["quiz", "assessment", "test"]):
        offer_type = "quiz"
    elif any(word in ad_copy_lower for word in ["demo", "call", "consultation"]):
        offer_type = "demo"
    
    # CTA type classification
    cta_type = "learn_more"  # default
    if any(word in ad_copy_lower for word in ["sign up", "get started", "join"]):
        cta_type = "sign_up"
    elif any(word in ad_copy_lower for word in ["download", "get free"]):
        cta_type = "download"
    elif any(word in ad_copy_lower for word in ["book", "schedule", "call"]):
        cta_type = "book_call"
    
    # Visual style (simplified without actual image analysis)
    visual_style = "professional"  # default without image analysis
    
    return {
        "hook_type": hook_type,
        "offer_type": offer_type,
        "visual_style": visual_style,
        "cta_type": cta_type
    }


def create_competitor_output_paths(base_dir: str = "outputs/competitor_intel") -> Dict[str, str]:
    """Create timestamped output paths for competitor intel"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    Path(f"{base_dir}/creatives").mkdir(parents=True, exist_ok=True)
    
    return {
        "json": f"{base_dir}/data_{timestamp}.json",
        "summary": f"{base_dir}/report_{timestamp}.md",
        "metadata": f"{base_dir}/metadata_{timestamp}.json",
        "creatives_dir": f"{base_dir}/creatives"
    }


def analyze_patterns(winning_creatives: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate pattern analysis across winning creatives
    
    Args:
        winning_creatives: List of creative dicts with analysis
        
    Returns:
        Pattern analysis dict
    """
    hook_dist = {}
    visual_dist = {}
    format_dist = {}
    offer_dist = {}
    
    for creative in winning_creatives:
        analysis = creative.get("analysis", {})
        
        # Count hook types
        hook = analysis.get("hook_type")
        hook_dist[hook] = hook_dist.get(hook, 0) + 1
        
        # Count visual styles
        visual = analysis.get("visual_style")
        visual_dist[visual] = visual_dist.get(visual, 0) + 1
        
        # Count formats
        fmt = creative.get("media_type")
        format_dist[fmt] = format_dist.get(fmt, 0) + 1
        
        # Count offer types
        offer = analysis.get("offer_type")
        offer_dist[offer] = offer_dist.get(offer, 0) + 1
    
    return {
        "hook_distribution": hook_dist,
        "visual_styles": visual_dist,
        "format_distribution": format_dist,
        "offer_types": offer_dist,
        "total_analyzed": len(winning_creatives)
    }


# Example usage
if __name__ == "__main__":
    print("""
Competitor Intel - Processing Utilities

Usage:
1. Generate search queries from VPs
2. Construct Meta Ads Library URLs
3. Process Apify results
4. Classify creatives
5. Analyze patterns
6. Generate reports

Example:
    vps = [{"headline": "Digital Loyalty for Restaurants", "unique_mechanism": "SMS-based"}]
    queries = generate_search_queries(vps)
    # ["Digital Loyalty for Restaurants", "SMS-based"]
    
    url = construct_meta_ads_url(queries[0], "US")
    # https://www.facebook.com/ads/library/?active_status=active&...
    
    days = calculate_days_active(1704067200)  # Jan 1, 2024
    # Returns days since then
""")
