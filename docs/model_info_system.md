# Model Information System

This document describes the model information system in GPT Portal, which provides detailed information about LLM models including pricing, capabilities, and best use cases.

## Overview

The model information system automatically populates metadata for base models (models where `base_model_id` is null) with standardized information from a master data file. This ensures that all models have consistent and up-to-date information about their pricing, capabilities, and best use cases.

## Components

### 1. Backend Master Data

The master data for model information is stored in:
```
backend/open_webui/migrations/model_info_master.py
```

This file contains a dictionary with standardized information for all supported models, including:
- Company that created the model
- Tier classification (Value, Standard, Pro)
- Pricing information (input tokens, output tokens, request-based pricing)
- Best use cases
- Additional information

### 2. Backend Utility Functions

Utility functions for working with model metadata are in:
```
backend/open_webui/utils/model_metadata.py
```

These functions help populate model metadata from the master data.

### 3. Migration Script

A migration script is available to update existing base models with information from the master data:
```
backend/open_webui/migrations/versions/a8f5b2c7d9e0_populate_model_metadata.py
```

### 4. Automatic Population

The system automatically populates metadata for base models when:
- Creating a new model
- Updating an existing model

### 5. Admin API Endpoints

The system provides API endpoints for administrators to manage model metadata:
```
POST /api/models/model/refresh-metadata      # Refresh metadata for a specific model
POST /api/models/refresh-all-metadata        # Refresh metadata for all base models
```

### 6. Frontend Components

The frontend components for displaying and managing model information:
```
src/lib/components/chat/ModelInfo.svelte     # Displays model information to users
src/lib/components/admin/ModelInfoManager.svelte  # Admin UI for managing model information
```

## Usage

### Running the Migration Script

To update existing base models with information from the master data:

```bash
# Run the Alembic migration
alembic upgrade a8f5b2c7d9e0
```

This will automatically update all base models with information from the master data file.

Alternatively, you can run the migration as part of your regular database migrations:

```bash
# Run all pending migrations
alembic upgrade head
```

### Adding New Models

When adding new models to the system:

1. Add the model information to the master data file (`model_info_master.py`):
   ```python
   MODEL_INFO_MASTER = {
       # Existing models...
       
       'new-model-id': {
           'company': 'Company Name',
           'tier': 'Standard',  # Value, Standard, or Pro
           'name': 'Model Display Name',
           'pricing': {
               'inputTokens': 1.00,  # Cost per million input tokens
               'outputTokens': 2.00  # Cost per million output tokens
           },
           'best_use_cases': 'Description of best use cases for this model.'
       }
   }
   ```

2. The system will automatically populate metadata for new base models when they are created

### Updating Model Information

To update model information:

1. Update the master data file (`model_info_master.py`) with the new information

2. Use one of the following methods to apply the changes:

   a. **Admin UI**:
   - Navigate to the Model Information Manager in the admin interface
   - Use the "Refresh Selected Model" or "Refresh All Models" buttons
   - Check "Force update" to overwrite existing values

   b. **API Endpoint (Single Model)**:
   ```
   POST /api/models/model/refresh-metadata
   {
     "id": "model-id",
     "force": false  # Set to true to overwrite existing values
   }
   ```

   c. **API Endpoint (All Models)**:
   ```
   POST /api/models/refresh-all-metadata
   {
     "force": false  # Set to true to overwrite existing values
   }
   ```

   d. **Migration Script**:
   ```bash
   # Run the migration script
   alembic upgrade a8f5b2c7d9e0
   ```

## Data Structure

Model metadata follows this structure:

```python
{
    'company': 'OpenAI',              # Company that created the model
    'tier': 'Standard',               # Tier classification (Value, Standard, Pro)
    'name': 'GPT-4o',                 # Full model name
    'pricing': {                      # Pricing information
        'inputTokens': 2.50,          # Cost per million input tokens in USD
        'outputTokens': 10.00,        # Cost per million output tokens in USD
        'requestPrice': 5.00          # Optional price per 1,000 requests
    },
    'best_use_cases': 'General-purpose tasks requiring a balance between performance and cost...',
    'additionalInfo': 'Optional additional information about the model'
}
```

## Implementation Notes

- The system only updates metadata for base models (where `base_model_id` is null)
- Existing metadata values are preserved (not overwritten) unless forced
- The system uses fuzzy matching to find model information in the master data
- The master data file should be updated when new models are added to the system
- The migration script can be run multiple times safely (it's idempotent)
