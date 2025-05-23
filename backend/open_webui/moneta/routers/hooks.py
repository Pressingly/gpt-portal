from fastapi import APIRouter, Request, HTTPException, status, Depends, Response
from pydantic import BaseModel, Field
import logging
import aiohttp
from typing import Dict, Any, Optional

# Import Lago utilities
from open_webui.moneta.utils.lago import create_subscription
# Import Storefront utilities
from open_webui.moneta.utils.storefront import STOREFRONT_URL, save_storefront_token_to_cookies

# Configure logging
log = logging.getLogger(__name__)


# Define the structure of the user data within the webhook payload
# Based on inspection of Auths.insert_new_auth and UserModel
class WebhookUserPayload(BaseModel):
    id: str
    name: str
    email: str
    role: str
    profile_image_url: str
    last_active_at: Optional[int] = None
    updated_at: Optional[int] = None
    created_at: Optional[int] = None
    api_key: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    info: Optional[Dict[str, Any]] = None
    oauth_sub: Optional[str] = None


# Define the overall webhook payload structure
class WebhookPayload(BaseModel):
    action: str
    message: str
    user: WebhookUserPayload


# Create the FastAPI router
router = APIRouter()

# POST /moneta/webhook
@router.post("/webhook", status_code=status.HTTP_202_ACCEPTED)
async def moneta_webhook(payload: WebhookPayload, request: Request):
    """
    Receives webhook events from OpenWebUI.
    Currently processes 'signup' events for Lago integration.
    """
    log.info(f"Received webhook event. Action: {payload.action}, User Email: {payload.user.email}")

    if payload.action == "signup":
        log.info(f"Processing 'signup' event for user: {payload.user.email}")

        try:
            # Call Lago integration to create subscription for the user
            user_id = payload.user.id
            subscription = create_subscription(user_id)

            if subscription:
                log.info(f"Successfully created subscription for user {payload.user.email} (ID: {user_id})")
            else:
                log.warning(f"Failed to create subscription for user {payload.user.email} (ID: {user_id})")

            return {"status": "accepted", "action": payload.action, "user_email": payload.user.email}

        except Exception as e:
            log.error(f"Error processing signup webhook for user {payload.user.email}: {e}", exc_info=True)
            # Return an error status to the webhook sender if processing fails critically
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process signup event for Lago: {e}"
            )
    else:
        # Handle other potential future actions if needed, or just acknowledge them
        log.warning(f"Received unhandled webhook action: {payload.action}. Ignoring.")
        return {"status": "ignored", "action": payload.action}

# Example of how you might add other hook-related endpoints or utilities
# GET /moneta/webhook/status
@router.get("/webhook/status")
async def get_hooks_status():
    return {"status": "running"}
