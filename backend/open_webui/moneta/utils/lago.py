import os
import requests
import logging

LAGO_API_URL = os.environ.get("LAGO_API_URL")
LAGO_API_KEY = os.environ.get("LAGO_API_KEY")

logger = logging.getLogger(__name__)

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
        return response.json().get("customer")

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
    
# example return [{'lago_id': '1384b28e-aabf-465c-bfc7-b4b3e6435193', 'external_id': 'f708a03c-dbb8-4c12-a65f-d154994d6a7b', 'lago_customer_id': 'cd80cb16-d2be-4f26-80fc-66cfd5eaf324', 'external_customer_id': '3f708f4a-5cd3-4e79-ab84-e50f0bd4186e', 'name': '', 'plan_code': 'micro_1205', 'status': 'active', 'billing_time': 'calendar', 'subscription_at': '2025-05-12T00:00:00Z', 'started_at': '2025-05-12T00:00:00Z', 'trial_ended_at': None, 'ending_at': None, 'terminated_at': None, 'pending_terminated_at': None, 'canceled_at': None, 'created_at': '2025-05-12T11:49:41Z', 'previous_plan_code': None, 'next_plan_code': None, 'downgrade_plan_date': None, 'dynamic_properties': {}, 'latest_aggregation_data': [{'event_id': 'b068ac55-5bf5-4979-b008-eefef30d16b2', 'charge_id': '377bc82a-69bc-4a97-b941-bd5e740aead3', 'charge_model': 'package', 'total_usage_units': 0.74031, 'billable_metric_id': 'ed4058bb-f102-4a0f-8c2a-5741025428ce', 'billable_metric_code': 'credit_cents', 'remaining_usage_units': 0.25969, 'total_deposited_units': 1}], 'latest_aggregation_data_updated_at': '2025-05-14T08:49:25Z', 'subscription_date': '2025-05-12'}, {'lago_id': 'f5913e23-6091-4354-89b4-b2453478bae1', 'external_id': 'sub-2be474c1-4e88-4fa9-bdb6-903980d4aad1', 'lago_customer_id': 'cd80cb16-d2be-4f26-80fc-66cfd5eaf324', 'external_customer_id': '3f708f4a-5cd3-4e79-ab84-e50f0bd4186e', 'name': '', 'plan_code': 'pro', 'status': 'active', 'billing_time': 'anniversary', 'subscription_at': '2025-05-12T15:10:55Z', 'started_at': '2025-05-12T15:10:55Z', 'trial_ended_at': None, 'ending_at': None, 'terminated_at': None, 'pending_terminated_at': None, 'canceled_at': None, 'created_at': '2025-05-12T15:10:55Z', 'previous_plan_code': None, 'next_plan_code': None, 'downgrade_plan_date': None, 'dynamic_properties': {'location': {'city': 'Ho Chi Minh City', 'region': 'SG', 'country': 'VN', 'timezone': 'Asia/Ho_Chi_Minh'}, 'device_data': {'os': {'os_name': 'macOS', 'version': '10.15'}, 'browser': {'version': '605.1', 'browser_name': 'Safari'}, 'device_type': 'desktop', 'device_model': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15'}, 'amount_cents': 0, 'amount_currency': 'USD'}, 'latest_aggregation_data': [], 'latest_aggregation_data_updated_at': None, 'subscription_date': '2025-05-12'}]
def get_user_subscriptions(user_external_id, status=None):
    """
    Get all subscriptions for a user from Lago.
    
    Args:
        user_external_id (str): The external ID of the user
        status (str, optional): Filter subscriptions by status. 
            Valid values: 'pending', 'active', 'terminated', 'canceled'
    
    Returns:
        list: List of subscription objects from Lago
        
    Raises:
        ValueError: If Lago API key is not configured
        Exception: If API call fails
    """
    
    # Ref: https://getlago.com/docs/api-reference/subscriptions/get-all
    
    if not LAGO_API_KEY:
        logger.error("LAGO_API_KEY environment variable not set.")
        raise ValueError("Lago API key is not configured.")

    api_endpoint = f"{LAGO_API_URL}/subscriptions"
    headers = {
        "Authorization": f"Bearer {LAGO_API_KEY}",
        "Content-Type": "application/json",
    }
    
    # Build query parameters
    params = {
        "external_customer_id": str(user_external_id),
        "page": 1,
        "per_page": 100  # Adjust if needed
    }
    
    if status:
        params["status"] = status

    try:
        response = requests.get(
            api_endpoint, 
            headers=headers, 
            params=params,
            timeout=10
        )
        response.raise_for_status()

        logger.info(f"Successfully retrieved subscriptions for customer {user_external_id}")
        return response.json().get("subscriptions", [])

    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Lago API to get subscriptions for customer {user_external_id}: {e}")
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
        logger.error(f"An unexpected error occurred getting Lago subscriptions for {user_external_id}: {e}")
        raise e