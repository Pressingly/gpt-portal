# User Feedback Collection - Technical Design Document

## Overview

This document outlines the technical design for implementing user feedback collection using PostHog Surveys. The feature will prompt users for feedback after every 10 queries, allowing them to provide free-text comments about their experience.

## Requirements

1. Track the number of queries a user makes
2. Prompt users for feedback after every 10 queries
3. Collect free-text feedback via a modal popup
4. Store feedback in PostHog for analysis
5. Allow users to dismiss the feedback prompt and be reminded later
6. Make feedback visible to admins via the PostHog dashboard

## Architecture

### Backend Components

#### User Query Counter

- **Model**: `UserStats` in `backend/open_webui/models/user_stats.py`
- **Table**: `user_stats` in the database
- **API**: Endpoints in `backend/open_webui/routers/user_stats.py`
- **Purpose**: Track how many queries each user has made

#### Integration Points

- Chat completion endpoint will be modified to increment the query counter
- API endpoints will be added to get and update the query count

### Frontend Components

#### PostHog Integration

- **Configuration**: PostHog initialization in `src/lib/posthog.ts`
- **Global Setup**: PostHog initialization in `src/routes/+layout.svelte`
- **Environment Variables**: PostHog API key and host in `.env`

#### Query Counter Tracking

- **API Client**: Functions in `src/lib/apis/user_stats.ts`
- **Integration**: Query counter incrementation in `src/lib/apis/index.ts`
- **Check Logic**: Function to check if it's time to show the survey

#### Survey Triggering

- **Trigger Logic**: Code to trigger the PostHog survey after every 10 queries
- **Frequency Control**: Logic to prevent showing the survey too frequently
- **Event Tracking**: Tracking for survey interactions

### PostHog Survey Configuration

- **Survey Creation**: Feedback survey in the PostHog dashboard
- **Appearance**: Customized to match the application's design
- **Question**: Free-text feedback question
- **Targeting**: Configured to show based on custom event

## Technical Approach

### Query Counting Mechanism

1. Create a `user_stats` table with `user_id` and `query_count` columns
2. Increment the counter each time a user submits a query
3. Return the updated count to the frontend

### Survey Triggering Logic

We'll use one of two approaches for triggering the survey:

#### Approach 1: Event-Based Triggering (Previous Approach)

```typescript
// When query count reaches a multiple of 10
if (queryCount % 10 === 0) {
  // Fire a custom event that will trigger the survey
  posthog.capture('feedback_survey_trigger', {
    query_count: queryCount
  });
}
```

#### Approach 2: Programmatic Rendering (Current Approach)

```typescript
// When query count reaches a multiple of 10
if (queryCount % 10 === 0) {
  // Check if the user has recently interacted with the survey
  const lastInteraction = localStorage.getItem('last_survey_interaction');
  const now = Date.now();

  // Only show if it's been at least 24 hours since last interaction
  if (!lastInteraction || (now - parseInt(lastInteraction)) > 24 * 60 * 60 * 1000) {
    // Get active surveys for this user
    posthog.getActiveMatchingSurveys((surveys) => {
      if (surveys && surveys.length > 0) {
        // Store the survey ID
        const surveyId = surveys[0].id;

        // Render the survey in a specific container
        posthog.renderSurvey(surveyId, '#survey-container');

        // Track that the survey was shown
        posthog.capture('survey shown', {
          $survey_id: surveyId
        });
      }
    });
  }
}
```

### Preventing Survey Fatigue

To prevent survey fatigue, we'll:

1. Store the timestamp of the last survey interaction in localStorage
2. Only show the survey again after a reasonable time period (e.g., 24 hours)
3. Allow users to dismiss the survey

### Event Tracking

We'll track the following events in PostHog:

1. `query_submitted`: When a user submits a query (includes query_count)
2. `survey shown`: When the survey is displayed to the user
3. `survey dismissed`: When the user dismisses the survey
4. `survey sent`: When the user submits feedback

## Data Flow

1. User submits a query
2. Backend increments the query count
3. Frontend checks if count % 10 === 0
4. If true, frontend fetches active surveys using `getActiveMatchingSurveys`
5. If a survey is available, frontend renders it using `renderSurvey`
6. User submits feedback or dismisses the survey
7. PostHog captures the feedback or dismissal event
8. Feedback is stored in PostHog for admin analysis

## Security Considerations

1. User IDs will be hashed before being sent to PostHog
2. No sensitive information will be included in survey events
3. PostHog's data retention policies will be configured appropriately

## Performance Considerations

1. Query counter updates will be asynchronous to avoid blocking the UI
2. Survey display logic will be optimized to minimize impact on performance
3. Local storage will be used to reduce unnecessary API calls

## Testing Strategy

1. Unit tests for the query counter API
2. Integration tests for the survey triggering logic
3. End-to-end tests for the complete feedback flow
4. Manual testing of the survey appearance and submission

## Rollout Plan

1. Deploy backend changes for query counting
2. Configure PostHog survey in staging environment
3. Deploy frontend changes for survey triggering
4. Test the complete flow in staging
5. Deploy to production
6. Monitor feedback collection and adjust as needed
