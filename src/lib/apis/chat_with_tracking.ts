import { chatCompletion } from '$lib/apis/openai';
import { incrementUserQueryCount, getUserQueryCount } from './user_stats';
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

        // Get the query count
        const userStats = await getUserQueryCount(token);
        console.log('User stats updated:', userStats);

        // Only track events if we have a valid query count
        if (userStats && typeof userStats.query_count === 'number') {
          // Track the query submission in PostHog
          captureEvent('query_submitted', {
            query_count: userStats.query_count
          });

          // Check if it's time to show the feedback survey
          const { showSurvey: shouldShowSurvey, surveyId } = await checkAndTriggerFeedbackSurvey(userStats.query_count);

          // If we should show the survey and have a valid survey ID, show it
          if (shouldShowSurvey && surveyId) {
            // Since we can't directly import the showSurvey function from the layout,
            // we'll use a custom event to trigger the survey
            if (typeof window !== 'undefined') {
              window.dispatchEvent(new CustomEvent('show-feedback-survey', {
                detail: { surveyId }
              }));
            }
          }
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
