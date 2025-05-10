import posthog from 'posthog-js';
import { browser } from '$app/environment';

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
