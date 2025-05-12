import time
import logging
from typing import Optional

from open_webui.internal.db import Base, get_db, JSONField
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, String, Integer

from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# UserStats DB Schema
####################


class UserStats(Base):
    __tablename__ = "user_stats"

    user_id = Column(String, primary_key=True)
    query_count = Column(Integer, default=0)
    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)


class UserStatsModel(BaseModel):
    user_id: str
    query_count: int
    created_at: int  # timestamp in epoch
    updated_at: int  # timestamp in epoch

    model_config = ConfigDict(from_attributes=True)


####################
# Forms
####################


class UserStatsResponse(BaseModel):
    user_id: str
    query_count: int


class UserStatsTable:
    def get_user_stats_by_user_id(self, user_id: str) -> Optional[UserStatsModel]:
        """
        Get user stats by user ID.
        """
        with get_db() as db:
            user_stats = db.query(UserStats).filter_by(user_id=user_id).first()
            if user_stats:
                return UserStatsModel.model_validate(user_stats)
            return None

    def create_user_stats(self, user_id: str) -> Optional[UserStatsModel]:
        """
        Create new user stats entry.
        """
        current_time = int(time.time())
        with get_db() as db:
            user_stats = UserStats(
                user_id=user_id,
                query_count=0,
                created_at=current_time,
                updated_at=current_time,
            )
            db.add(user_stats)
            db.commit()
            db.refresh(user_stats)
            return UserStatsModel.model_validate(user_stats)

    def increment_query_count(self, user_id: str) -> Optional[UserStatsModel]:
        """
        Increment the query count for a user.
        If the user stats don't exist, create a new entry.
        """
        current_time = int(time.time())
        with get_db() as db:
            user_stats = db.query(UserStats).filter_by(user_id=user_id).first()
            if not user_stats:
                # Create new user stats if they don't exist
                user_stats = UserStats(
                    user_id=user_id,
                    query_count=1,
                    created_at=current_time,
                    updated_at=current_time,
                )
                db.add(user_stats)
            else:
                # Increment the query count
                user_stats.query_count += 1
                user_stats.updated_at = current_time
            
            db.commit()
            db.refresh(user_stats)
            return UserStatsModel.model_validate(user_stats)


# Create a singleton instance
UserStatsDB = UserStatsTable()
