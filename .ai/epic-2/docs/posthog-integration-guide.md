# PostHog Integration Guide

## Overview

This guide explains how to integrate PostHog into the GPT Portal application for analytics and user feedback collection. PostHog is an open-source product analytics platform that allows us to track user behavior, collect feedback, and analyze usage patterns.

## Prerequisites

- PostHog account with API key
- Access to the PostHog dashboard
- Development environment for GPT Portal

## Installation

### 1. Install PostHog JS Package

```bash
pnpm add posthog-js
```

### 2. Environment Configuration

Add the following environment variables to your `.env` file:

```
VITE_POSTHOG_API_KEY=your_api_key_here
VITE_POSTHOG_HOST=https://app.posthog.com
```

For Docker deployments, add these environment variables to your `docker-compose.yaml` file:

```yaml
services:
  open-webui:
    environment:
      - 'VITE_POSTHOG_API_KEY=your_api_key_here'
      - 'VITE_POSTHOG_HOST=https://app.posthog.com'
```

## Frontend Integration

### 1. Create PostHog Configuration File

Create a new file at `src/lib/posthog.ts`:

```typescript
import posthog from 'posthog-js';
import { browser } from '$app/environment';

// Initialize PostHog only in the browser
if (browser) {
  try {
    // Get the API key and host from the environment variables
    const apiKey = import.meta.env.VITE_POSTHOG_API_KEY || '';
    const apiHost = import.meta.env.VITE_POSTHOG_HOST || 'https://app.posthog.com';

    console.log('Initializing PostHog with API key:', apiKey ? 'API key found' : 'No API key');

    // Only initialize PostHog if we have an API key
    if (apiKey) {
      posthog.init(apiKey, {
        api_host: apiHost,
        capture_pageview: true,
        capture_pageleave: true,
        autocapture: true,
        persistence: 'localStorage',
        loaded: (posthog) => {
          // Identify the user if they're logged in
          try {
            const userId = localStorage.getItem('user_id');
            if (userId) {
              posthog.identify(userId);
              console.log('PostHog: Identified user', userId);
            } else {
              // If no user ID is found, generate a unique anonymous ID
              const anonymousId = 'anon_' + Math.random().toString(36).substring(2, 15);
              posthog.identify(anonymousId);
              console.log('PostHog: Using anonymous ID', anonymousId);
            }
          } catch (error) {
            console.error('Error identifying user in PostHog:', error);
          }
        }
      });
      console.log('PostHog initialized successfully');
    } else {
      console.warn('PostHog not initialized: No API key provided');
    }
  } catch (error) {
    console.error('Error initializing PostHog:', error);
  }
}

// Utility function to safely capture events
export const captureEvent = (eventName: string, properties?: Record<string, any>) => {
  if (browser) {
    try {
      // Check if PostHog is initialized before capturing events
      if ((posthog as any).__loaded) {
        posthog.capture(eventName, properties);
      } else {
        console.warn(`PostHog event not captured (not initialized): ${eventName}`);
      }
    } catch (error) {
      console.error('Error capturing PostHog event:', error);
    }
  }
};

// Function to check and trigger feedback survey
export const checkAndTriggerFeedbackSurvey = (queryCount: number) => {
  if (!browser) return;

  try {
    // Check if PostHog is initialized
    if (!(posthog as any).__loaded) {
      console.warn('Cannot trigger feedback survey: PostHog not initialized');
      return;
    }

    // Check if it's time to show the survey (every 10 queries)
    if (queryCount % 10 === 0 && queryCount > 0) {
      // Check if the user has recently interacted with a survey
      const lastInteraction = localStorage.getItem('last_survey_interaction');
      const now = Date.now();

      // Only show if it's been at least 24 hours since last interaction
      if (!lastInteraction || (now - parseInt(lastInteraction)) > 24 * 60 * 60 * 1000) {
        // Capture an event that will trigger the survey
        posthog.capture('feedback_survey_trigger', {
          query_count: queryCount,
          timestamp: new Date().toISOString()
        });

        console.log('Triggering feedback survey for query count:', queryCount);

        // Store the time of the survey trigger
        localStorage.setItem('last_survey_trigger', now.toString());
      } else {
        console.log('Skipping survey trigger: too soon since last interaction');
      }
    }
  } catch (error) {
    console.error('Error triggering feedback survey:', error);
  }
};

// Function to handle survey completion
export const setupSurveyCompletionHandler = () => {
  if (!browser) return;

  try {
    // Check if PostHog is initialized
    if (!(posthog as any).__loaded) {
      console.warn('Cannot set up survey completion handler: PostHog not initialized');
      return;
    }

    // Store that the user has interacted with the survey
    const markSurveyInteraction = () => {
      localStorage.setItem('last_survey_interaction', Date.now().toString());
    };

    // Listen for custom events that might be dispatched when a survey is completed
    window.addEventListener('posthog_survey_completed', () => {
      console.log('Survey completed via custom event');
      markSurveyInteraction();

      // Additional custom tracking if needed
      posthog.capture('custom_survey_completed', {
        timestamp: new Date().toISOString()
      });
    });

    // Try to set up PostHog survey handlers using a more dynamic approach
    try {
      // Use a dynamic approach to access potentially undefined methods
      const ph = posthog as any;

      if (typeof ph.onSurveyShown === 'function') {
        ph.onSurveyShown((survey: any) => {
          console.log('Survey shown:', survey.id);
        });
      }

      if (typeof ph.onSurveyCompleted === 'function') {
        ph.onSurveyCompleted((survey: any) => {
          console.log('Survey completed:', survey.id);
          markSurveyInteraction();

          posthog.capture('custom_survey_completed', {
            survey_id: survey.id,
            timestamp: new Date().toISOString()
          });
        });
      }
    } catch (innerError) {
      console.warn('Could not set up PostHog survey handlers:', innerError);
    }

    console.log('Survey completion handler set up');
  } catch (error) {
    console.error('Error setting up survey completion handler:', error);
  }
};

export default posthog;
```

### 2. Initialize PostHog in the App Layout

Update `src/routes/+layout.svelte`:

```svelte
<script>
  import { onMount } from 'svelte';
  import posthog, { setupSurveyCompletionHandler } from '$lib/posthog';

  onMount(() => {
    // Set up PostHog survey completion handler
    // We'll wait a bit to make sure PostHog is initialized
    setTimeout(() => {
      try {
        setupSurveyCompletionHandler();
        console.log('PostHog survey completion handler set up');
      } catch (error) {
        console.error('Error setting up PostHog survey completion handler:', error);
      }
    }, 2000);

    // Later in the code, after user login:
    if (sessionUser) {
      // Identify the user in PostHog
      try {
        if (posthog && typeof posthog.identify === 'function') {
          posthog.identify(sessionUser.id);
          posthog.people.set({
            name: sessionUser.name,
            email: sessionUser.email,
            role: sessionUser.role
          });
          console.log('PostHog: User identified after login', sessionUser.id);
        }
      } catch (error) {
        console.error('Error identifying user in PostHog after login:', error);
      }
    }
  });
</script>

<slot />
```

### 3. Track Query Submissions

Create a wrapper for the chat completion API that tracks queries and triggers the feedback survey:

```typescript
// In src/lib/apis/chat_with_tracking.ts
import { chatCompletion } from '$lib/apis/openai';
import { incrementUserQueryCount } from './user_stats';
import { captureEvent, checkAndTriggerFeedbackSurvey } from '$lib/posthog';

/**
 * Wrapper for the chat completion API that also tracks queries
 * @param token The authentication token
 * @param body The chat completion request body
 * @param url The API URL
 * @returns The chat completion response
 */
export const chatCompletionWithTracking = async (
  token: string = '',
  body: object,
  url: string = `${import.meta.env.VITE_WEBUI_BASE_URL || ''}/api`
): Promise<[Response | null, AbortController]> => {
  try {
    // Call the original chat completion API
    const [response, controller] = await chatCompletion(token, body, url);

    // If the response is successful, increment the query count
    if (response && response.ok) {
      try {
        console.log('Chat completion successful, incrementing query count');

        // Increment the query count
        const userStats = await incrementUserQueryCount(token);
        console.log('User stats updated:', userStats);

        // Only track events if we have a valid query count
        if (userStats && typeof userStats.query_count === 'number') {
          // Track the query submission in PostHog
          captureEvent('query_submitted', {
            query_count: userStats.query_count
          });

          // Check if it's time to show the feedback survey
          checkAndTriggerFeedbackSurvey(userStats.query_count);
        } else {
          console.warn('Cannot track query: Invalid user stats', userStats);
        }
      } catch (error) {
        // Log the error but don't fail the request
        console.error('Error tracking query:', error);
      }
    }

    return [response, controller];
  } catch (error) {
    console.error('Error in chat completion with tracking:', error);
    throw error;
  }
};
```

Then update the Chat component to use the tracking wrapper:

```typescript
// In src/lib/components/playground/Chat.svelte
import { generateOpenAIChatCompletion } from '$lib/apis/openai';
import { chatCompletionWithTracking } from '$lib/apis/chat_with_tracking';

// Replace the existing chat completion call
const chatCompletionHandler = async () => {
  // ...existing code...

  const [res, controller] = await chatCompletionWithTracking(
    localStorage.token,
    {
      model: model.id,
      stream: true,
      messages: [
        system
          ? {
              role: 'system',
              content: system
            }
          : undefined,
        ...messages
      ].filter((message) => message)
    },
    `${WEBUI_BASE_URL}/api`
  );

  // ...rest of the function...
};

## PostHog Survey Configuration

### 1. Create a Survey in PostHog

1. Log in to your PostHog dashboard
2. Navigate to "Surveys" in the left sidebar
3. Click "New survey"
4. Select "API" as the survey type
5. Configure the survey with the following settings:

### 2. Survey Settings

- **Name**: User Feedback Survey
- **Question**: How can we improve your experience?
- **Question Type**: Open text
- **Targeting**: Set to "API" survey type
- **Appearance**: Customize to match your application's design
- **Thank You Message**: Thank you for your feedback!

### 3. Survey Targeting

We're using Programmatic Rendering to display surveys, so the targeting is controlled in our code rather than in PostHog:

1. In the survey settings, go to the "Targeting" tab
2. Select "API" as the survey type
3. You don't need to set up event-based targeting, as we'll fetch and display the survey programmatically
4. Our code will handle throttling (showing the survey only every 24 hours)

## Viewing Feedback in PostHog

### 1. Access Survey Results

1. Log in to your PostHog dashboard
2. Navigate to "Surveys" in the left sidebar
3. Click on your survey name
4. View the "Results" tab to see all feedback submissions

### 2. Create a Dashboard for Feedback Analysis

1. Navigate to "Dashboards" in the left sidebar
2. Click "New dashboard"
3. Add panels for:
   - Survey response rate
   - Survey completion rate
   - Recent feedback submissions
   - Feedback trends over time

## Best Practices

1. **Respect User Privacy**: Only collect necessary information
2. **Prevent Survey Fatigue**: Don't show surveys too frequently
3. **Test Thoroughly**: Ensure the survey appears correctly and doesn't disrupt the user experience
4. **Review Feedback Regularly**: Set up a process to review and act on feedback
5. **Iterate**: Adjust the survey based on response rates and feedback quality

## Troubleshooting

### Survey Not Appearing

1. Check that the PostHog API key and host are correct
2. Verify that there are active surveys in your PostHog dashboard
3. Check that the user's query count is a multiple of 10
4. Verify that the user hasn't interacted with a survey in the last 24 hours
5. Look for JavaScript errors in the browser console
6. Check if `getActiveMatchingSurveys` is returning surveys

### Feedback Not Being Recorded

1. Verify that the survey is being completed correctly
2. Check that the PostHog events are being captured
3. Ensure the user has a stable internet connection
4. Check for any errors in the PostHog dashboard
