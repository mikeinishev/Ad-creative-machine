"""
Marketing Analyst Agent - Output Processor
Handles output generation and file management
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


def create_marketing_output_paths(base_dir: str = "outputs/analysis") -> Dict[str, str]:
    """Create timestamped output paths for marketing analysis"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    
    return {
        "json": f"{base_dir}/marketing_{timestamp}.json",
        "summary": f"{base_dir}/marketing_{timestamp}_summary.md",
        "metadata": f"{base_dir}/marketing_{timestamp}_metadata.json"
    }


def save_marketing_analysis(
    analysis: Dict[str, Any],
    url: str,
    output_paths: Dict[str, str]
):
    """Save marketing analysis results to files"""
    
    # Save JSON analysis
    with open(output_paths["json"], 'w') as f:
        json.dump(analysis, f, indent=2)
    
    # Save metadata
    metadata = {
        "source_url": url,
        "analysis_timestamp": datetime.now().isoformat(),
        "output_files": output_paths
    }
    with open(output_paths["metadata"], 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Marketing analysis saved to: {output_paths['json']}")
    print(f"📄 Summary saved to: {output_paths['summary']}")


def extract_value_props_for_search(analysis: Dict[str, Any]) -> List[str]:
    """
    Extract search-ready value propositions for Agent 3
    Returns list of search queries derived from VPs
    """
    queries = []
    
    vps = analysis.get("value_propositions", [])
    for vp in vps:
        # Use headline as base query
        headline = vp.get("headline", "")
        if headline:
            queries.append(headline)
        
        # Extract key mechanism/unique selling point
        mechanism = vp.get("unique_mechanism", "")
        if mechanism:
            queries.append(mechanism)
    
    # Also use main pain points as queries
    landing = analysis.get("landing_analysis", {})
    pain_points = landing.get("pain_points", [])[:3]  # Top 3
    queries.extend(pain_points)
    
    return queries


# Example usage
if __name__ == "__main__":
    print("""
Marketing Analyst - Output Processor

Usage in Antigravity:
1. After analyzing landing page, call save_marketing_analysis()
2. Extract value props with extract_value_props_for_search()
3. Pass queries to Agent 3 for competitor research

Example:
    paths = create_marketing_output_paths()
    save_marketing_analysis(data, url, paths)
    
    search_queries = extract_value_props_for_search(data)
    # Pass to Agent 3
""")
