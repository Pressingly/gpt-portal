import posthog from 'posthog-js';
import { browser } from '$app/environment';

/**
 * PostHog integration for GPT Portal analytics
 *
 * This module provides functions for tracking events in PostHog,
 * including user queries, model usage, and session metrics.
 */

// We'll use type assertions to work around TypeScript limitations

// Initialize PostHog only in the browser
if (browser) {
  try {
    // Get the API key and host from the environment variables
    // These will be available in both development and Docker environments
    const apiKey = import.meta.env.VITE_POSTHOG_API_KEY || 'phc_NmZ475zYZkGW8hZYboYEAXzcLeF35fPnatNUThpFLVb';
    const apiHost = import.meta.env.VITE_POSTHOG_HOST || 'https://app.posthog.com';

    console.log('Initializing PostHog with API key:', apiKey ? 'API key found' : 'No API key');
    console.log('PostHog API host:', apiHost);

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
            // Try to get the user ID from localStorage
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

/**
 * Safely capture events in PostHog
 * @param eventName Name of the event to capture
 * @param properties Properties to include with the event
 */
export const captureEvent = (eventName: string, properties?: Record<string, any>) => {
  if (browser) {
    try {
      // Check if PostHog is initialized before capturing events
      if ((posthog as any).__loaded) {
        // Add timestamp if not provided
        const eventProperties: Record<string, any> = {
          ...properties,
          timestamp: properties?.timestamp || new Date().toISOString()
        };

        // Add session_id if available and not provided
        if (localStorage.getItem('session_id') && !eventProperties.session_id) {
          eventProperties.session_id = localStorage.getItem('session_id');
        }

        // Capture the event
        posthog.capture(eventName, eventProperties);
        console.log(`PostHog event captured: ${eventName}`);
      } else {
        console.warn(`PostHog event not captured (not initialized): ${eventName}`);
      }
    } catch (error) {
      console.error('Error capturing PostHog event:', error);
    }
  }
};

/**
 * Track a query submission
 * @param modelId ID of the primary model used
 * @param additionalModels Array of additional models if multi-LLM query
 * @param chatId ID of the chat
 * @param messageId ID of the message
 */
export const trackQuerySubmission = (
  modelId: string,
  additionalModels: string[] = [],
  chatId: string = 'unknown',
  messageId: string = 'unknown'
) => {
  const userId = localStorage.getItem('user_id');
  const isMultiLlm = additionalModels.length > 0;

  captureEvent('query_submitted', {
    user_id: userId,
    model_id: modelId,
    additional_models: additionalModels,
    is_multi_llm: isMultiLlm,
    chat_id: chatId,
    message_id: messageId,
    query_type: 'chat_completion'
  });
};

/**
 * Track a query completion
 * @param modelId ID of the primary model used
 * @param additionalModels Array of additional models if multi-LLM query
 * @param inputTokens Number of input tokens
 * @param outputTokens Number of output tokens
 * @param queryCost Cost of the query
 * @param totalDuration Total duration of the query in ms
 * @param chatId ID of the chat
 * @param messageId ID of the message
 * @param status Completion status ('success' or 'failure')
 * @param errorType Type of error if status is 'failure'
 */
export const trackQueryCompletion = (
  modelId: string,
  additionalModels: string[] = [],
  inputTokens: number = 0,
  outputTokens: number = 0,
  queryCost: number = 0,
  totalDuration: number = 0,
  chatId: string = 'unknown',
  messageId: string = 'unknown',
  status: 'success' | 'failure' = 'success',
  errorType: string = ''
) => {
  const userId = localStorage.getItem('user_id');
  const isMultiLlm = additionalModels.length > 0;

  captureEvent('query_completed', {
    user_id: userId,
    model_id: modelId,
    additional_models: additionalModels,
    is_multi_llm: isMultiLlm,
    input_tokens: inputTokens,
    output_tokens: outputTokens,
    total_tokens: inputTokens + outputTokens,
    query_cost: queryCost,
    completion_status: status,
    error_type: errorType,
    total_duration: totalDuration,
    chat_id: chatId,
    message_id: messageId
  });
};

/**
 * Track model selection
 * @param modelId ID of the selected model
 * @param modelProvider Provider of the model
 * @param context Context where the selection happened
 */
export const trackModelSelection = (
  modelId: string,
  modelProvider: string = 'unknown',
  context: string = 'chat'
) => {
  const userId = localStorage.getItem('user_id');

  captureEvent('model_selected', {
    user_id: userId,
    model_id: modelId,
    model_provider: modelProvider,
    context: context
  });
};

/**
 * Track multi-model selection
 * @param modelIds Array of selected model IDs
 * @param modelProviders Array of model providers
 * @param context Context where the selection happened
 */
export const trackMultiModelSelection = (
  modelIds: string[],
  modelProviders: string[] = [],
  context: string = 'chat'
) => {
  const userId = localStorage.getItem('user_id');

  captureEvent('multi_model_selected', {
    user_id: userId,
    model_ids: modelIds,
    model_providers: modelProviders.length === modelIds.length ? modelProviders : modelIds.map(() => 'unknown'),
    context: context
  });
};

// Function to check and trigger feedback survey
export const checkAndTriggerFeedbackSurvey = async (queryCount: number): Promise<{ showSurvey: boolean, surveyId: string | null }> => {
  if (!browser) return { showSurvey: false, surveyId: null };
  console.log('Survey - Checking and triggering feedback survey for query count:', queryCount);
  try {
    // Check if PostHog is initialized
    if (!(posthog as any).__loaded) {
      console.warn('Survey - Cannot trigger feedback survey: PostHog not initialized');
      return { showSurvey: false, surveyId: null };
    }

    // Check if it's time to show the survey (every 10 queries)
    if (queryCount % 10 === 0 && queryCount > 0) {
      // Check if the user has recently interacted with a survey
      const lastInteraction = localStorage.getItem('last_survey_interaction');
      const now = Date.now();

      // Only show if it's been at least 24 hours since last interaction
      if (!lastInteraction || (now - parseInt(lastInteraction)) > 24 * 60 * 60 * 1000) {
        // Get active surveys for this user
        return new Promise((resolve) => {
          posthog.getActiveMatchingSurveys((surveys) => {
            if (surveys && surveys.length > 0) {
              console.log('Survey - Found active survey:', surveys[0].id);

              // Store the time of the survey trigger
              localStorage.setItem('last_survey_trigger', now.toString());

              // Return the survey ID to be rendered
              resolve({ showSurvey: true, surveyId: surveys[0].id });
            } else {
              console.log('Survey - No active surveys found');
              resolve({ showSurvey: false, surveyId: null });
            }
          }, true); // Force reload to get the latest surveys
        });
      } else {
        console.log('Survey - Skipping survey trigger: too soon since last interaction');
        return { showSurvey: false, surveyId: null };
      }
    }
  } catch (error) {
    console.error('Survey - Error triggering feedback survey:', error);
  }

  return { showSurvey: false, surveyId: null };
};

// Function to handle survey completion
export const setupSurveyCompletionHandler = () => {
  if (!browser) return;

  try {
    // Check if PostHog is initialized
    if (!(posthog as any).__loaded) {
      console.warn('Survey - Cannot set up survey completion handler: PostHog not initialized');
      return;
    }

    console.log('Survey - Survey completion handler set up');
  } catch (error) {
    console.error('Survey - Error setting up survey completion handler:', error);
  }
};

// Function to mark survey interaction
export const markSurveyInteraction = () => {
  if (browser) {
    localStorage.setItem('last_survey_interaction', Date.now().toString());
    console.log('Survey - Survey interaction marked at:', new Date().toISOString());
  }
};

export default posthog;
