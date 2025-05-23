from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Optional, Any
import logging

from open_webui.utils.auth import get_verified_user
from open_webui.models.users import UserModel
from open_webui.moneta.utils.lago import (
    fetch_all_plans,
    fetch_plan_by_code,
    fetch_user_subscriptions,
    create_subscription,
    cancel_subscription,
    fetch_current_usage,
    fetch_customer_invoices
)

# Configure logging
logger = logging.getLogger(__name__)

# Create the FastAPI router
router = APIRouter()


class SubscriptionRequest(BaseModel):
    plan_code: str
    options: Optional[Dict[str, Any]] = None


class CancelSubscriptionRequest(BaseModel):
    status: Optional[str] = None


@router.get("/plans")
async def get_plans(user: UserModel = Depends(get_verified_user)):
    """
    Get all available subscription plans.
    """
    try:
        plans = fetch_all_plans()
        print(plans)
        return plans
    except Exception as e:
        logger.error(f"Error fetching plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch plans: {str(e)}"
        )


@router.get("/plans/{plan_code}")
async def get_plan_by_code(plan_code: str, user: UserModel = Depends(get_verified_user)):
    """
    Get a specific plan by its code.
    """
    try:
        plan = fetch_plan_by_code(plan_code)
        return plan
    except Exception as e:
        logger.error(f"Error fetching plan {plan_code}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch plan: {str(e)}"
        )


@router.get("/subscriptions")
async def get_user_subscriptions(user: UserModel = Depends(get_verified_user)):
    """
    Get all subscriptions for the current user.
    """
    try:
        subscriptions = fetch_user_subscriptions(user.id)
        print(subscriptions)
        return subscriptions
    except Exception as e:
        logger.error(f"Error fetching subscriptions for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch subscriptions: {str(e)}"
        )


@router.post("/subscriptions")
async def create_user_subscription(
    request: SubscriptionRequest, 
    user: UserModel = Depends(get_verified_user)
):
    """
    Create a new subscription for the current user.
    """
    try:
        options = request.options or {}
        subscription = create_subscription(user.id, request.plan_code, options)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create subscription"
            )
        return subscription
    except Exception as e:
        logger.error(f"Error creating subscription for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )


@router.delete("/subscriptions/{subscription_id}")
async def cancel_user_subscription(
    subscription_id: str, 
    request: CancelSubscriptionRequest = None,
    user: UserModel = Depends(get_verified_user)
):
    """
    Cancel a subscription.
    """
    try:
        status_param = request.status if request else None
        result = cancel_subscription(subscription_id, status_param)
        return result
    except Exception as e:
        logger.error(f"Error canceling subscription {subscription_id} for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )


@router.get("/usage/{subscription_id}")
async def get_current_usage(
    subscription_id: str, 
    user: UserModel = Depends(get_verified_user)
):
    """
    Get current usage for a specific subscription.
    """
    try:
        usage = fetch_current_usage(user.id, subscription_id)
        return usage
    except Exception as e:
        logger.error(f"Error fetching usage for subscription {subscription_id} (user {user.id}): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch usage: {str(e)}"
        )


@router.get("/invoices")
async def get_customer_invoices(user: UserModel = Depends(get_verified_user)):
    """
    Get all invoices for the current user.
    """
    try:
        invoices = fetch_customer_invoices(user.id)
        return invoices
    except Exception as e:
        logger.error(f"Error fetching invoices for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch invoices: {str(e)}"
        )
