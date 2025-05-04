#!/usr/bin/env python3
"""
Script to migrate model information from static config to database.
This script reads the model information from the TypeScript config file
and updates the corresponding models in the database.
"""

import os
import sys
import json
import re
import time
from typing import Dict, Any, List

# Add the backend directory to the path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from open_webui.internal.db import get_db
    from open_webui.models.models import Model, Models
except ImportError:
    print("Error: Could not import required modules from backend.")
    print("Make sure you're running this script from the project root.")
    sys.exit(1)

# Path to the model-info.ts file
MODEL_INFO_PATH = 'src/lib/config/model-info.ts'

def extract_model_info() -> Dict[str, Dict[str, Any]]:
    """Extract model information from the TypeScript config file."""
    try:
        with open(MODEL_INFO_PATH, 'r') as f:
            content = f.read()
        
        # Extract the modelInfo object using regex
        match = re.search(r'export const modelInfo: ModelInfoMap = ({[\s\S]*?});', content)
        if not match:
            print("Error: Could not find modelInfo object in the file.")
            return {}
        
        # Get the object content
        model_info_str = match.group(1)
        
        # Convert TypeScript to valid JSON
        # Replace single quotes with double quotes
        model_info_str = model_info_str.replace("'", '"')
        # Remove trailing commas
        model_info_str = re.sub(r',(\s*[}\]])', r'\1', model_info_str)
        
        # Parse the JSON
        model_info = json.loads(model_info_str)
        return model_info
    
    except Exception as e:
        print(f"Error extracting model info: {e}")
        return {}

def update_models_in_db(model_info: Dict[str, Dict[str, Any]]) -> None:
    """Update models in the database with the extracted information."""
    for model_id, info in model_info.items():
        print(f"Updating model: {model_id}")
        
        # Get the model from the database
        model = Models.get_model_by_id(model_id)
        
        if model:
            # Update the model metadata
            metadata = {
                "company": info.get("company"),
                "tier": info.get("tier"),
                "pricing": info.get("pricing"),
                "best_use_cases": info.get("bestUseCases"),
                "additionalInfo": info.get("additionalInfo", None)
            }
            
            # Update the model
            result = Models.update_model_metadata(model_id, metadata)
            
            if result:
                print(f"  ✓ Successfully updated model: {model_id}")
            else:
                print(f"  ✗ Failed to update model: {model_id}")
        else:
            print(f"  ✗ Model not found in database: {model_id}")

def main():
    """Main function to run the migration."""
    print("Starting model information migration...")
    
    # Extract model information from the TypeScript file
    model_info = extract_model_info()
    
    if not model_info:
        print("No model information found. Exiting.")
        return
    
    print(f"Found {len(model_info)} models in the config file.")
    
    # Update models in the database
    update_models_in_db(model_info)
    
    print("Migration completed.")

if __name__ == "__main__":
    main()
