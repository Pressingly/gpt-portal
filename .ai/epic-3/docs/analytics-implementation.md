# GPT Portal Analytics Implementation Guide

## Overview

This document outlines the implementation of analytics tracking in GPT Portal using PostHog. The implementation focuses on capturing detailed metrics about user queries, model usage, and costs to support the requirements specified in the Website Analytics epic.

## Implementation Components

### 1. PostHog Integration

The PostHog integration has been enhanced to support tracking detailed analytics events:

- **File**: `src/lib/posthog.ts`
- **Key Functions**:
  - `captureEvent`: Enhanced to include timestamps and session IDs
  - `trackQuerySubmission`: Tracks when a query is submitted
  - `trackQueryCompletion`: Tracks when a query is completed with usage data
  - `trackModelSelection`: Tracks when a model is selected
  - `trackMultiModelSelection`: Tracks when multiple models are selected

### 2. Cost Calculation

A utility has been implemented to calculate query costs based on token usage and model pricing:

- **File**: `src/lib/utils/cost-calculator.ts`
- **Key Functions**:
  - `calculateQueryCost`: Calculates the cost of a query based on token usage and model pricing
  - `calculateMultiModelQueryCost`: Calculates the cost for multi-LLM queries

### 3. Session Tracking

Session management functionality has been implemented to track user sessions and group queries:

- **File**: `src/lib/utils/session-manager.ts`
- **Key Functions**:
  - `generateSessionId`: Generates a new session ID
  - `trackSessionStart`: Tracks when a session starts
  - `updateSessionActivity`: Updates session activity with query costs
  - `trackSessionEnd`: Tracks when a session ends
  - `initializeSessionTracking`: Initializes session tracking

### 4. Chat Completion Tracking

The chat completion tracking has been enhanced to capture detailed metrics:

- **File**: `src/lib/apis/chat_with_tracking.ts`
- **Key Changes**:
  - Extracts token usage from API responses
  - Calculates query costs
  - Tracks query submission and completion events
  - Updates session activity

### 5. Model Selection Tracking

Model selection tracking has been added to the model selector component:

- **File**: `src/lib/components/chat/ModelSelector/Selector.svelte`
- **Key Changes**:
  - Tracks model selection events
  - Includes model provider information

## Event Structure

### Query Submitted Event

```json
{
  "user_id": "user123",
  "model_id": "gpt-4",
  "additional_models": ["gpt-3.5-turbo"],
  "is_multi_llm": true,
  "chat_id": "chat123",
  "message_id": "msg123",
  "query_type": "chat_completion",
  "session_id": "session123",
  "timestamp": "2023-06-01T12:00:00Z"
}
```

### Query Completed Event

```json
{
  "user_id": "user123",
  "model_id": "gpt-4",
  "additional_models": ["gpt-3.5-turbo"],
  "is_multi_llm": true,
  "input_tokens": 100,
  "output_tokens": 200,
  "total_tokens": 300,
  "query_cost": 0.0025,
  "completion_status": "success",
  "total_duration": 1500,
  "chat_id": "chat123",
  "message_id": "msg123",
  "session_id": "session123",
  "timestamp": "2023-06-01T12:00:05Z"
}
```

### Model Selected Event

```json
{
  "user_id": "user123",
  "model_id": "gpt-4",
  "model_provider": "openai",
  "context": "chat",
  "session_id": "session123",
  "timestamp": "2023-06-01T12:00:00Z"
}
```

### Session Started Event

```json
{
  "user_id": "user123",
  "session_id": "session123",
  "device_info": {
    "userAgent": "Mozilla/5.0...",
    "platform": "MacIntel",
    "screenSize": "1920x1080"
  },
  "browser_info": {
    "language": "en-US",
    "cookiesEnabled": true,
    "doNotTrack": null
  },
  "timestamp": "2023-06-01T12:00:00Z"
}
```

### Session Ended Event

```json
{
  "user_id": "user123",
  "session_id": "session123",
  "session_duration": 3600000,
  "query_count": 10,
  "total_cost": 0.025,
  "timestamp": "2023-06-01T13:00:00Z"
}
```

## Usage

The analytics tracking is automatically integrated into the application and requires no additional setup from users. All events are sent to PostHog where they can be viewed and analyzed.

## PostHog Dashboard Configuration

See the [PostHog Dashboard Setup Guide](posthog-dashboard-setup.md) for information on how to configure PostHog dashboards to visualize the analytics data.
