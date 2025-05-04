"""
Utility functions for handling model metadata.
"""
import logging
from typing import Dict, Any, Optional

from open_webui.moneta.migrations.model_info_master import get_model_info

log = logging.getLogger(__name__)


def populate_model_metadata(model_id: str, existing_meta: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Populate model metadata from master data.

    Args:
        model_id: The ID of the model
        existing_meta: Existing metadata to merge with (optional)

    Returns:
        Dictionary with updated metadata
    """
    # Start with existing metadata or empty dict
    meta = existing_meta.copy() if existing_meta else {}

    # Get model info from master data
    model_info = get_model_info(model_id)
    if not model_info:
        log.info(f"No master data found for model {model_id}")
        return meta

    # Fields to update from master data (only if not already set)
    fields_to_update = {
        'company': model_info.get('company'),
        'tier': model_info.get('tier'),
        'name': model_info.get('name'),
        'pricing': model_info.get('pricing'),
        'best_use_cases': model_info.get('best_use_cases')
    }

    # Add additional info if present
    if 'additionalInfo' in model_info:
        fields_to_update['additionalInfo'] = model_info.get('additionalInfo')

    # Update metadata fields (only if not already set)
    for field, value in fields_to_update.items():
        if value is not None and (field not in meta or meta.get(field) is None):
            meta[field] = value
            log.debug(f"Added {field} to metadata for model {model_id}")

    return meta
