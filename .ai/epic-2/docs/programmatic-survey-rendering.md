# Programmatic Survey Rendering Implementation

## Overview

This document outlines the implementation of Programmatic Rendering for PostHog surveys in the GPT Portal application. We're switching from Event-Based Triggering to Programmatic Rendering because we cannot configure the survey to appear based on the `feedback_survey_trigger` event in PostHog.

## Approach Comparison

### Event-Based Triggering (Previous Approach)

In the Event-Based Triggering approach:

1. We check if the query count is a multiple of 10
2. We capture a `feedback_survey_trigger` event in PostHog
3. PostHog shows the survey based on this event

This approach relies on PostHog's survey targeting configuration, which we cannot set up correctly.

### Programmatic Rendering (New Approach)

In the Programmatic Rendering approach:

1. We still check if the query count is a multiple of 10
2. Instead of capturing an event, we directly fetch active surveys using `getActiveMatchingSurveys`
3. We render the survey in our application using `renderSurvey`

This approach gives us complete control over when and how surveys are displayed.

## Implementation Details

### 1. Survey Component

We've created a new Svelte component `FeedbackSurvey.svelte` that:

- Renders the survey in a modal/popup
- Handles survey events (shown, dismissed, completed)
- Provides styling consistent with the application

### 2. PostHog Integration

We've updated the PostHog integration to:

- Use `getActiveMatchingSurveys` to fetch surveys
- Use `renderSurvey` to display surveys
- Track survey lifecycle events properly

### 3. Application Layout

We've updated the application layout to:

- Include the survey component
- Manage survey visibility state
- Provide functions to show/hide the survey

### 4. Chat Tracking Logic

We've updated the chat tracking logic to:

- Check if it's time to show a survey
- Fetch and display the survey if conditions are met
- Handle errors gracefully

## Usage

The survey will be shown automatically when:

1. The user's query count is a multiple of 10
2. The user hasn't interacted with a survey in the last 24 hours
3. There's an active survey available for the user

## Testing

To test the survey functionality:

1. Make sure you have a survey created in PostHog
2. Submit queries until your query count is a multiple of 10
3. Verify that the survey appears
4. Test dismissing and completing the survey

## Troubleshooting

If the survey doesn't appear:

1. Check the browser console for errors
2. Verify that PostHog is initialized correctly
3. Confirm that there's an active survey in PostHog
4. Check that the user's query count is a multiple of 10
5. Verify that the user hasn't interacted with a survey in the last 24 hours
