"""
Design Analyzer Agent - Input Processor
Handles multi-format input detection and routing
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Literal
from urllib.parse import urlparse

# Input format types
InputFormat = Literal["figma", "pdf", "url", "image"]


class DesignAnalyzerInput:
    """Detects and validates input format for design analysis"""
    
    def __init__(self, input_path: str):
        self.input_path = input_path
        self.format = self._detect_format()
        
    def _detect_format(self) -> InputFormat:
        """Detect input format based on path/URL"""
        # Check if URL
        if self.input_path.startswith(('http://', 'https://')):
            parsed = urlparse(self.input_path)
            if 'figma.com' in parsed.netloc:
                return "figma"
            return "url"
        
        # Check file extension
        path = Path(self.input_path)
        ext = path.suffix.lower()
        
        if ext == '.pdf':
            return "pdf"
        elif ext in ['.png', '.jpg', '.jpeg', '.webp']:
            return "image"
        
        raise ValueError(f"Unsupported input format: {self.input_path}")
    
    def validate(self) -> bool:
        """Validate that input exists/is accessible"""
        if self.format in ["figma", "url"]:
            # URL inputs - assume valid if format detected
            return True
        else:
            # File inputs - check existence
            return Path(self.input_path).exists()
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the input"""
        return {
            "input_path": self.input_path,
            "format": self.format,
            "timestamp": datetime.now().isoformat(),
        }


def create_output_paths(base_dir: str = "outputs/analysis") -> Dict[str, str]:
    """Create timestamped output paths"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    
    return {
        "json": f"{base_dir}/design_{timestamp}.json",
        "summary": f"{base_dir}/design_{timestamp}_summary.md",
        "metadata": f"{base_dir}/design_{timestamp}_metadata.json"
    }


def save_analysis_output(
    analysis: Dict[str, Any],
    input_info: Dict[str, Any],
    output_paths: Dict[str, str]
):
    """Save analysis results to files"""
    
    # Save JSON analysis
    with open(output_paths["json"], 'w') as f:
        json.dump(analysis, f, indent=2)
    
    # Save metadata
    metadata = {
        "input": input_info,
        "output_files": output_paths,
        "generated_at": datetime.now().isoformat()
    }
    with open(output_paths["metadata"], 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Analysis saved to: {output_paths['json']}")
    print(f"📄 Summary saved to: {output_paths['summary']}")


# Example usage instructions
if __name__ == "__main__":
    print("""
Design Analyzer - Input Processor

Usage in Antigravity:
1. Provide input path/URL
2. Agent detects format automatically
3. Routes to appropriate processing method
4. Outputs structured JSON

Example:
    input = DesignAnalyzerInput("https://figma.com/file/ABC123")
    print(f"Format: {input.format}")  # "figma"
    
    paths = create_output_paths()
    print(f"Output will be saved to: {paths['json']}")
""")
