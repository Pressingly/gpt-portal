import { chatCompletion } from '$lib/apis/openai';
import { incrementUserQueryCount } from './user_stats';
import {
  trackQuerySubmission,
  trackQueryCompletion,
  checkAndTriggerFeedbackSurvey
} from '$lib/posthog';
import { calculateQueryCost } from '$lib/utils/cost-calculator';
import { updateSessionActivity } from '$lib/utils/session-manager';

/**
 * Wrapper for the chat completion API that also tracks queries
 * @param token The authentication token
 * @param body The chat completion request body
 * @param url The API URL
 * @returns The chat completion response
 */
export const chatCompletionWithTracking = async (
  token: string = '',
  body: any,
  url: string = `${import.meta.env.VITE_WEBUI_BASE_URL || ''}/api`
): Promise<[Response | null, AbortController]> => {
  try {
    const startTime = Date.now();
    const messageId = body.id || `msg_${Math.random().toString(36).substring(2, 15)}`;
    const chatId = body.chat_id || 'unknown';
    const modelId = body.model;

    // Get additional models if this is a multi-LLM query
    const additionalModels = body.additional_models || [];

    // Track query submission
    trackQuerySubmission(
      modelId,
      additionalModels,
      chatId,
      messageId
    );

    // Call the original chat completion API
    const [response, controller] = await chatCompletion(token, body, url);

    // If the response is successful, track completion with usage data
    if (response && response.ok) {
      try {
        console.log('Chat completion successful, tracking metrics');

        // Increment the query counter in the backend
        const userStats = await incrementUserQueryCount(token);
        console.log('User stats updated:', userStats);

        // Try to extract token usage from the response
        let inputTokens = 0;
        let outputTokens = 0;

        try {
          // Clone the response to read the body
          const responseClone = response.clone();
          const responseData = await responseClone.json();

          // Extract token usage if available
          inputTokens = responseData.usage?.prompt_tokens || 0;
          outputTokens = responseData.usage?.completion_tokens || 0;
        } catch (error) {
          console.warn('Could not extract token usage from response:', error);
        }

        // Calculate cost based on token usage and model pricing
        const queryCost = calculateQueryCost(modelId, inputTokens, outputTokens);

        // Update session activity with the query cost
        updateSessionActivity(queryCost);

        // Track query completion
        trackQueryCompletion(
          modelId,
          additionalModels,
          inputTokens,
          outputTokens,
          queryCost,
          Date.now() - startTime,
          chatId,
          messageId,
          'success'
        );

        // Only check for survey if we have a valid query count
        if (userStats && typeof userStats.query_count === 'number') {
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
        }
      } catch (error) {
        // Log the error but don't fail the request
        console.error('Error tracking query completion:', error);
      }
    } else {
      // Track failed query
      trackQueryCompletion(
        modelId,
        additionalModels,
        0,
        0,
        0,
        Date.now() - startTime,
        chatId,
        messageId,
        'failure',
        response ? `HTTP ${response.status}` : 'Network Error'
      );
    }

    return [response, controller];
  } catch (error) {
    console.error('Error in chat completion with tracking:', error);
    throw error;
  }
};
