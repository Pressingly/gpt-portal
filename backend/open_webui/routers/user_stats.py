import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from open_webui.models.user_stats import UserStatsDB, UserStatsResponse
from open_webui.utils.auth import get_verified_user
from open_webui.constants import ERROR_MESSAGES
from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

router = APIRouter()


############################
# GetUserStats
############################


@router.get("/", response_model=UserStatsResponse)
async def get_user_stats(user=Depends(get_verified_user)):
    """
    Get the query count for the current user.
    If the user stats don't exist, create a new entry.
    """
    user_stats = UserStatsDB.get_user_stats_by_user_id(user.id)
    if not user_stats:
        user_stats = UserStatsDB.create_user_stats(user.id)
    
    return UserStatsResponse(
        user_id=user_stats.user_id,
        query_count=user_stats.query_count
    )


############################
# IncrementQueryCount
############################


class IncrementResponse(BaseModel):
    user_id: str
    query_count: int
    success: bool


@router.post("/increment", response_model=IncrementResponse)
async def increment_query_count(user=Depends(get_verified_user)):
    """
    Increment the query count for the current user.
    If the user stats don't exist, create a new entry.
    """
    try:
        user_stats = UserStatsDB.increment_query_count(user.id)
        return IncrementResponse(
            user_id=user_stats.user_id,
            query_count=user_stats.query_count,
            success=True
        )
    except Exception as e:
        log.error(f"Error incrementing query count: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT("Error incrementing query count")
        )
