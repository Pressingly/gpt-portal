"""Populate model metadata from master data

Revision ID: a8f5b2c7d9e0
Revises: 7826ab40b532
Create Date: 2024-12-24 00:00:00.000000

"""
from typing import Sequence, Union
import logging
import time
import sys

from alembic import op
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import Column, Text, JSON, BigInteger, Boolean

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("model_info_migration")

# revision identifiers, used by Alembic.
revision = "a8f5b2c7d9e0"
down_revision = "3781e22d8b01"  # Update this to the latest migration in your system
branch_labels = None
depends_on = None

# Import model info master data
from open_webui.moneta.migrations.model_info_master import get_model_info

# Define model class for SQLAlchemy
Base = declarative_base()

class Model(Base):
    __tablename__ = "model"

    id = Column(Text, primary_key=True)
    user_id = Column(Text)
    base_model_id = Column(Text, nullable=True)
    name = Column(Text)
    params = Column(JSON)
    meta = Column(JSON)
    access_control = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    updated_at = Column(BigInteger)
    created_at = Column(BigInteger)


def upgrade() -> None:
    """Update model metadata from master data."""
    print("Starting model metadata migration...")

    # Create a SQLAlchemy session
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        # Get all base models (where base_model_id is null)
        base_models = session.query(Model).filter(Model.base_model_id.is_(None)).all()
        print(f"Found {len(base_models)} base models")

        # Update each base model
        updated_count = 0
        for model in base_models:
            print(f"Processing model {model.id}")

            # Get model info from master data
            model_info = get_model_info(model.id)
            if not model_info:
                print(f"No master data found for model {model.id}")
                continue

            # Get current metadata
            current_meta = model.meta or {}

            # Create new metadata by merging master data with existing metadata
            new_meta = current_meta.copy()

            # Fields to update from master data
            fields_to_update = {
                'company': model_info.get('company'),
                'tier': model_info.get('tier'),
                'name': model_info.get('name'),
                'pricing': model_info.get('pricing'),
                'best_use_cases': model_info.get('best_use_cases')
            }

            # Add additional info if present
            if 'additionalInfo' in model_info:
                fields_to_update['additionalInfo'] = model_info.get('additionalInfo')

            # Update metadata fields (only if not already set)
            changes_made = False
            for field, value in fields_to_update.items():
                if value is not None and (field not in current_meta or current_meta[field] is None):
                    new_meta[field] = value
                    changes_made = True
                    print(f"  - Updating {field} for model {model.id}")

            if not changes_made:
                print(f"No changes needed for model {model.id}")
                continue

            # Update the model in the database
            model.meta = new_meta
            model.updated_at = int(time.time())
            updated_count += 1

        # Commit the changes
        session.commit()
        print(f"Migration complete. Updated {updated_count} out of {len(base_models)} base models.")

    except Exception as e:
        print(f"Error during migration: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def downgrade() -> None:
    """No downgrade path for data migration."""
    pass
