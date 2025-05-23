/**
 * Lago API Service
 *
 * This service provides functions to interact with the Lago API for subscription management
 * through our backend API endpoints.
 */
import { WEBUI_API_BASE_URL } from '$lib/constants';

/**
 * Helper function for making API requests to our backend Lago endpoints
 */
async function lagoApiRequest(endpoint: string, options: RequestInit = {}) {
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json'
    },
    credentials: 'include' as RequestCredentials // Include cookies for authentication
  };

  try {
    const response = await fetch(`${WEBUI_API_BASE_URL}/lago${endpoint}`, {
      ...defaultOptions,
      ...options
    });

    if (!response.ok) {
      let errorMessage = `API error: ${response.status}`;
      try {
        const error = await response.json();
        errorMessage = error.detail || error.message || errorMessage;
      } catch (e) {
        // If the response is not JSON, use the status text
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }

    return response.json();
  } catch (error) {
    console.error('Lago API request failed:', error);
    throw error;
  }
}

/**
 * Fetch all available plans
 */
export async function fetchAllPlans() {
  return lagoApiRequest('/plans');
}

/**
 * Fetch a specific plan by code
 */
export async function fetchPlanByCode(planCode: string) {
  return lagoApiRequest(`/plans/${planCode}`);
}

/**
 * Fetch user's subscriptions
 */
export async function fetchUserSubscriptions() {
  // The backend will use the current user's ID from the session
  return lagoApiRequest('/subscriptions');
}

/**
 * Create a subscription for a user
 */
export async function createSubscription(planCode: string, options = {}) {
  const payload = {
    plan_code: planCode,
    options: options
  };

  return lagoApiRequest('/subscriptions', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

/**
 * Cancel a subscription
 */
export async function cancelSubscription(subscriptionId: string, status?: string) {
  const payload = status ? { status } : {};

  return lagoApiRequest(`/subscriptions/${subscriptionId}`, {
    method: 'DELETE',
    body: JSON.stringify(payload)
  });
}

/**
 * Fetch current usage for a subscription
 */
export async function fetchCurrentUsage(subscriptionId: string) {
  return lagoApiRequest(`/usage/${subscriptionId}`);
}

/**
 * Fetch customer invoices
 */
export async function fetchCustomerInvoices() {
  // The backend will use the current user's ID from the session
  return lagoApiRequest('/invoices');
}
