import os
import requests
import logging
from typing import Dict, List, Optional, Any, Union

LAGO_API_URL = os.environ.get("LAGO_API_URL")
LAGO_API_KEY = os.environ.get("LAGO_API_KEY")
LAGO_TRIAL_PLAN_CODE = os.environ.get("LAGO_TRIAL_PLAN_CODE")

logger = logging.getLogger(__name__)

def _make_lago_request(endpoint: str, method: str = "GET", payload: Optional[Dict] = None, timeout: int = 10) -> Dict:
    """
    Helper function to make requests to the Lago API.

    Args:
        endpoint: The API endpoint (without the base URL)
        method: HTTP method (GET, POST, DELETE, etc.)
        payload: Request payload for POST/PUT requests
        timeout: Request timeout in seconds

    Returns:
        The JSON response from the API

    Raises:
        ValueError: If Lago API key is not configured
        Exception: If the API request fails
    """
    if not LAGO_API_KEY:
        logger.error("LAGO_API_KEY environment variable not set.")
        raise ValueError("Lago API key is not configured.")

    if not LAGO_API_URL:
        logger.error("LAGO_API_URL environment variable not set.")
        raise ValueError("Lago API URL is not configured.")

    url = f"{LAGO_API_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {LAGO_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Lago API ({method} {endpoint}): {e}")
        if e.response is not None:
            try:
                error_details = e.response.json()
                logger.error(f"Lago API Error details: {error_details}")
                raise Exception(f"Lago API error: {error_details}") from e
            except ValueError:  # If response is not JSON
                logger.error(f"Lago API Error response text: {e.response.text}")
                raise Exception(f"Lago API error: {e.response.status_code} - {e.response.text}") from e
        else:
            raise Exception(f"Lago API request failed: {e}") from e

    except Exception as e:
        logger.error(f"An unexpected error occurred during Lago API request ({method} {endpoint}): {e}")
        raise e

def upsert_customer(user_external_id, user_data):
    """
    Upserts a customer in Lago.
    # https://getlago.com/docs/api-reference/customers/create
    """
    if not LAGO_API_KEY:
        logger.error("LAGO_API_KEY environment variable not set.")
        raise ValueError("Lago API key is not configured.")

    api_endpoint = f"{LAGO_API_URL}/customers"
    headers = {
        "Authorization": f"Bearer {LAGO_API_KEY}",
        "Content-Type": "application/json",
    }

    # Construct the payload, mapping user_data to Lago's expected fields.
    # Ensure required fields like email, name, currency are present in user_data
    # Adjust the mapping based on the actual structure of your user_data
    payload = {
        "customer": {
            "external_id": str(user_external_id),
            "name": user_data.get("name", str(user_external_id)),
            "email": user_data.get("email"),
            "pinet_id_token": user_data.get("pinet_id_token_normal"),
            "moneta_id_token": user_data.get("moneta_id_token_normal"),
            "currency": user_data.get("currency", "USD"),  # Default currency if not provided
            "timezone": user_data.get("timezone", None),
            "region": user_data.get("region", "US"),
        }
    }

    # Remove keys with None values as Lago might not accept them
    # payload["customer"] = {k: v for k, v in payload["customer"].items() if v is not None}

    try:
        response = requests.post(api_endpoint, headers=headers, json=payload, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        logger.info(f"Successfully upserted customer {user_external_id} to Lago.")
        customer = response.json().get("customer")

        # Auto-subscribe the user to the trial plan
        try:
            subscription = create_subscription(user_external_id)
            if subscription:
                logger.info(f"User {user_external_id} auto-subscribed to plan {LAGO_TRIAL_PLAN_CODE}.")
            else:
                logger.warning(f"Failed to auto-subscribe user {user_external_id} to plan.")
        except Exception as e:
            # Log the error but don't prevent the user from being created
            logger.error(f"Error auto-subscribing user {user_external_id} to plan: {e}")

        return customer

    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Lago API to upsert customer {user_external_id}: {e}")
        if e.response is not None:
            try:
                error_details = e.response.json()
                logger.error(f"Lago API Error details: {error_details}")
                raise Exception(f"Lago API error: {error_details}") from e
            except ValueError: # If response is not JSON
                logger.error(f"Lago API Error response text: {e.response.text}")
                raise Exception(f"Lago API error: {e.response.status_code} - {e.response.text}") from e
        else:
             raise Exception(f"Lago API request failed: {e}") from e

    except Exception as e:
        logger.error(f"An unexpected error occurred during Lago customer upsert for {user_external_id}: {e}")
        raise e


def create_subscription(user_external_id):
    """
    Creates a subscription in Lago for the specified user.
    Uses the plan code defined in the LAGO_TRIAL_PLAN_CODE environment variable.
    # https://getlago.com/docs/api-reference/subscriptions/create
    """
    if not LAGO_API_KEY:
        logger.error("LAGO_API_KEY environment variable not set.")
        raise ValueError("Lago API key is not configured.")

    if not LAGO_TRIAL_PLAN_CODE:
        logger.warning(f"LAGO_TRIAL_PLAN_CODE environment variable not set. Skipping subscription creation for user {user_external_id}.")
        return None

    api_endpoint = f"{LAGO_API_URL}/subscriptions"
    headers = {
        "Authorization": f"Bearer {LAGO_API_KEY}",
        "Content-Type": "application/json",
    }

    # Construct the payload for creating a subscription
    payload = {
        "subscription": {
            "external_customer_id": str(user_external_id),
            "plan_code": LAGO_TRIAL_PLAN_CODE,
            "billing_time": "anniversary"  # Use anniversary billing to start from signup date
        }
    }

    try:
        response = requests.post(api_endpoint, headers=headers, json=payload, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        logger.info(f"Successfully created subscription for user {user_external_id} with plan {LAGO_TRIAL_PLAN_CODE}.")
        return response.json().get("subscription")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Lago API to create subscription for user {user_external_id}: {e}")
        if e.response is not None:
            try:
                error_details = e.response.json()
                logger.error(f"Lago API Error details: {error_details}")
                # Don't raise exception here to prevent blocking user signup if subscription creation fails
                return None
            except ValueError:  # If response is not JSON
                logger.error(f"Lago API Error response text: {e.response.text}")
                return None
        else:
            logger.error(f"Lago API request failed: {e}")
            return None

    except Exception as e:
        logger.error(f"An unexpected error occurred during Lago subscription creation for {user_external_id}: {e}")
        return None


def fetch_all_plans() -> Dict:
    """
    Fetches all available plans from Lago.

    Returns:
        Dictionary containing the list of plans
    """
    logger.info("Fetching all plans from Lago")
    return _make_lago_request("/plans")


def fetch_plan_by_code(plan_code: str) -> Dict:
    """
    Fetches a specific plan by its code.

    Args:
        plan_code: The code of the plan to fetch

    Returns:
        Dictionary containing the plan details
    """
    logger.info(f"Fetching plan with code {plan_code} from Lago")
    return _make_lago_request(f"/plans/{plan_code}")


def fetch_user_subscriptions(user_external_id: str) -> Dict:
    """
    Fetches all subscriptions for a specific user.

    Args:
        user_external_id: The external ID of the user

    Returns:
        Dictionary containing the list of subscriptions
    """
    logger.info(f"Fetching subscriptions for user {user_external_id} from Lago")
    return _make_lago_request(f"/subscriptions?external_customer_id={user_external_id}")


def cancel_subscription(subscription_id: str, status: Optional[str] = None) -> Dict:
    """
    Cancels a subscription.

    Args:
        subscription_id: The ID of the subscription to cancel
        status: Optional status parameter

    Returns:
        Dictionary containing the result of the operation
    """
    logger.info(f"Canceling subscription {subscription_id} in Lago")
    endpoint = f"/subscriptions/{subscription_id}"
    if status:
        endpoint += f"?status={status}"
    return _make_lago_request(endpoint, method="DELETE")


def fetch_current_usage(user_external_id: str, subscription_id: str) -> Dict:
    """
    Fetches the current usage for a specific subscription.

    Args:
        user_external_id: The external ID of the user
        subscription_id: The ID of the subscription

    Returns:
        Dictionary containing the usage details
    """
    logger.info(f"Fetching current usage for subscription {subscription_id} (user {user_external_id}) from Lago")
    return _make_lago_request(
        f"/customers/{user_external_id}/current_usage?external_subscription_id={subscription_id}"
    )


def fetch_customer_invoices(user_external_id: str) -> Dict:
    """
    Fetches all invoices for a specific customer.

    Args:
        user_external_id: The external ID of the user

    Returns:
        Dictionary containing the list of invoices
    """
    logger.info(f"Fetching invoices for user {user_external_id} from Lago")
    return _make_lago_request(f"/customers/{user_external_id}/invoices")