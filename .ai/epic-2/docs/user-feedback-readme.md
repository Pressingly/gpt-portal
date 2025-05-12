# User Feedback Collection Feature

## Overview

This feature implements user feedback collection using PostHog Surveys. It prompts users for feedback after every 10 queries, allowing them to provide free-text comments about their experience.

## Documentation

This folder contains the following documentation:

- [Technical Design Document](./user-feedback-technical-design.md): Detailed technical design for the feature
- [Task List](./user-feedback-task-list.md): Comprehensive list of tasks for implementation
- [PostHog Integration Guide](./posthog-integration-guide.md): Guide for integrating PostHog into the application
- [PostHog Survey Configuration](./posthog-survey-configuration.md): Guide for configuring the feedback survey in PostHog

## Implementation Examples

The `implementation-examples` folder contains sample implementations for the key components:

- [User Stats Model](./implementation-examples/user_stats.py): Backend model for tracking user query counts
- [User Stats Router](./implementation-examples/user_stats_router.py): API endpoints for user query counts
- [PostHog Integration](./implementation-examples/posthog.ts): Frontend PostHog integration
- [User Stats API Client](./implementation-examples/user_stats_api.ts): Frontend API client for user stats
- [Layout with PostHog](./implementation-examples/layout.svelte): Layout component with PostHog initialization
- [Chat API with Query Tracking](./implementation-examples/chat_api.ts): Chat API with query tracking integration

## Key Features

1. **Query Counting**: Tracks the number of queries a user makes
2. **Feedback Prompting**: Shows a feedback survey after every 10 queries
3. **Feedback Collection**: Collects free-text feedback via a PostHog survey
4. **Admin Dashboard**: Makes feedback visible to admins via the PostHog dashboard

## Implementation Approach

The implementation follows these key principles:

1. **Backend Tracking**: The backend tracks the number of queries a user makes
2. **Frontend Integration**: The frontend integrates with PostHog for survey display
3. **Event-Based Triggering**: Surveys are triggered based on custom events
4. **User Experience**: Surveys are designed to be non-intrusive and respectful of user time

## Getting Started

To implement this feature, follow these steps:

1. Review the [Technical Design Document](./user-feedback-technical-design.md)
2. Follow the [Task List](./user-feedback-task-list.md) for implementation
3. Use the [PostHog Integration Guide](./posthog-integration-guide.md) for PostHog setup
4. Configure the survey using the [PostHog Survey Configuration](./posthog-survey-configuration.md) guide

## Environment Variables

The following environment variables are required:

```
VITE_POSTHOG_API_KEY=your_api_key_here
VITE_POSTHOG_HOST=https://app.posthog.com
```

## Testing

To test the feature:

1. Submit queries to increment the query count
2. Verify that the survey appears after every 10 queries
3. Submit feedback through the survey
4. Verify that the feedback appears in the PostHog dashboard

## Troubleshooting

If the survey doesn't appear:

1. Check that the PostHog API key and host are correct
2. Verify that the `feedback_survey_trigger` event is being captured
3. Check the survey targeting settings in PostHog
4. Look for JavaScript errors in the browser console

If feedback isn't being recorded:

1. Verify that the survey is being completed correctly
2. Check that the PostHog events are being captured
3. Ensure the user has a stable internet connection
4. Check for any errors in the PostHog dashboard
