# Model Information Management

This document describes the implementation of the model information management system in GPT Portal.

## Overview

The model information management system allows administrators to add, update, and manage detailed information about the LLM models available in the platform. This information includes:

- Company that created the model
- Tier classification (Value, Standard, Pro)
- Pricing information (input tokens, output tokens, request-based pricing)
- Best use cases
- Additional information

## Implementation Details

### Frontend-Only Approach

To avoid backend changes that could conflict with the upstream open-source project, we've implemented a frontend-only solution:

1. **Static Configuration with Dynamic Updates**:
   - Base model information is stored in `src/lib/config/model-info.ts`
   - Custom model information is stored in the browser's localStorage
   - The system combines static and custom information at runtime

2. **Admin Interface**:
   - A new "Model Information" tab in the Admin > Models settings
   - UI for adding/editing model information
   - Ability to reset to default information

3. **User-Facing Display**:
   - Model information is displayed in the ModelInfo component
   - Users can view pricing, capabilities, and best use cases for each model

### Key Components

1. **Model Information Configuration (`src/lib/config/model-info.ts`)**:
   - Defines default model information
   - Provides functions to get, update, and reset model information
   - Handles localStorage persistence

2. **Model Information Manager (`src/lib/components/admin/ModelInfoManager.svelte`)**:
   - Admin UI for managing model information
   - Allows selecting models from available models
   - Form for editing model details

3. **Model Information Display (`src/lib/components/chat/ModelInfo.svelte`)**:
   - User-facing component to display model information
   - Shows pricing, capabilities, and best use cases

## Usage

### For Administrators

1. Navigate to Admin > Models
2. Click on the "Model Information" tab
3. Select a model from the dropdown
4. Edit the model information
5. Click "Save Model Information"

### For Users

1. Click on the model information icon in the chat interface
2. View detailed information about the selected model

## Data Structure

Model information follows this structure:

```typescript
interface ModelInfo {
  company: string;
  tier: 'Value' | 'Standard' | 'Pro';
  modelName: string;
  pricing: {
    inputTokens: number;
    outputTokens: number;
    requestPrice?: number;
  };
  bestUseCases: string;
  additionalInfo?: string;
}
```

## Future Improvements

Potential future improvements include:

1. Server-side storage for model information (when backend changes are acceptable)
2. Bulk import/export of model information
3. More detailed pricing information (e.g., volume discounts)
4. Integration with real-time pricing APIs from model providers
