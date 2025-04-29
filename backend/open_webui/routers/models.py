from typing import Optional, Dict, Any, List

from open_webui.models.models import (
    ModelForm,
    ModelModel,
    ModelResponse,
    ModelUserResponse,
    ModelMeta,
    Models,
)
from open_webui.constants import ERROR_MESSAGES
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from open_webui.utils.auth import get_admin_user, get_verified_user
from open_webui.utils.access_control import has_access, has_permission
from open_webui.utils.model_metadata import populate_model_metadata


class ModelMetaUpdateForm(BaseModel):
    """Form for updating model metadata"""
    company: Optional[str] = None
    tier: Optional[str] = None
    pricing: Optional[Dict[str, Any]] = None
    best_use_cases: Optional[str] = None
    description: Optional[str] = None
    profile_image_url: Optional[str] = None
    capabilities: Optional[Dict[str, Any]] = None


router = APIRouter()


###########################
# GetModels
###########################


@router.get("/", response_model=list[ModelUserResponse])
async def get_models(id: Optional[str] = None, user=Depends(get_verified_user)):
    if user.role == "admin":
        return Models.get_models()
    else:
        return Models.get_models_by_user_id(user.id)


###########################
# GetBaseModels
###########################


@router.get("/base", response_model=list[ModelResponse])
async def get_base_models(user=Depends(get_admin_user)):
    return Models.get_base_models()


############################
# CreateNewModel
############################


@router.post("/create", response_model=Optional[ModelModel])
async def create_new_model(
    request: Request,
    form_data: ModelForm,
    user=Depends(get_verified_user),
):
    if user.role != "admin" and not has_permission(
        user.id, "workspace.models", request.app.state.config.USER_PERMISSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )

    model = Models.get_model_by_id(form_data.id)
    if model:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.MODEL_ID_TAKEN,
        )

    else:
        model = Models.insert_new_model(form_data, user.id)
        if model:
            return model
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.DEFAULT(),
            )


###########################
# GetModelById
###########################


# Note: We're not using the typical url path param here, but instead using a query parameter to allow '/' in the id
@router.get("/model", response_model=Optional[ModelResponse])
async def get_model_by_id(id: str, user=Depends(get_verified_user)):
    model = Models.get_model_by_id(id)
    if model:
        if (
            user.role == "admin"
            or model.user_id == user.id
            or has_access(user.id, "read", model.access_control)
        ):
            return model
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# ToggelModelById
############################


@router.post("/model/toggle", response_model=Optional[ModelResponse])
async def toggle_model_by_id(id: str, user=Depends(get_verified_user)):
    model = Models.get_model_by_id(id)
    if model:
        if (
            user.role == "admin"
            or model.user_id == user.id
            or has_access(user.id, "write", model.access_control)
        ):
            model = Models.toggle_model_by_id(id)

            if model:
                return model
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ERROR_MESSAGES.DEFAULT("Error updating function"),
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.UNAUTHORIZED,
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# UpdateModelById
############################


@router.post("/model/update", response_model=Optional[ModelModel])
async def update_model_by_id(
    id: str,
    form_data: ModelForm,
    user=Depends(get_verified_user),
):
    model = Models.get_model_by_id(id)

    if not model:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    if (
        model.user_id != user.id
        and not has_access(user.id, "write", model.access_control)
        and user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    model = Models.update_model_by_id(id, form_data)
    return model


############################
# DeleteModelById
############################


@router.delete("/model/delete", response_model=bool)
async def delete_model_by_id(id: str, user=Depends(get_verified_user)):
    model = Models.get_model_by_id(id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    if (
        user.role != "admin"
        and model.user_id != user.id
        and not has_access(user.id, "write", model.access_control)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )

    result = Models.delete_model_by_id(id)
    return result


@router.delete("/delete/all", response_model=bool)
async def delete_all_models(user=Depends(get_admin_user)):
    result = Models.delete_all_models()
    return result


############################
# UpdateModelMetadata
############################


@router.post("/model/update-metadata", response_model=Optional[ModelModel])
async def update_model_metadata(
    id: str,
    metadata: ModelMetaUpdateForm,
    user=Depends(get_verified_user),
):
    """Update only the metadata of a model"""
    model = Models.get_model_by_id(id)

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    # Check permissions
    if (
        model.user_id != user.id
        and not has_access(user.id, "write", model.access_control)
        and user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    # Update only the metadata
    updated_model = Models.update_model_metadata(id, metadata)
    if not updated_model:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT("Failed to update model metadata"),
        )

    return updated_model


############################
# Refresh Model Metadata
############################

class RefreshModelMetadataForm(BaseModel):
    """Form for refreshing model metadata from master data"""
    force: bool = Field(default=False, description="If true, overwrite existing metadata values")


@router.post("/model/refresh-metadata", response_model=Optional[ModelModel])
async def refresh_model_metadata(
    id: str,
    form_data: RefreshModelMetadataForm = RefreshModelMetadataForm(),
    user=Depends(get_admin_user),
):
    """Refresh model metadata from master data"""
    model = Models.get_model_by_id(id)

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    # Only allow refreshing metadata for base models
    if model.base_model_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only refresh metadata for base models",
        )

    # Get current metadata
    current_meta = model.meta or {}

    # Populate metadata from master data
    updated_meta = {}

    if form_data.force:
        # If force is true, start with an empty dict to overwrite all values
        updated_meta = populate_model_metadata(model.id, {})
    else:
        # Otherwise, preserve existing values
        updated_meta = populate_model_metadata(model.id, current_meta)

    # Create metadata update form
    metadata_update = ModelMetaUpdateForm(
        company=updated_meta.get("company"),
        tier=updated_meta.get("tier"),
        pricing=updated_meta.get("pricing"),
        best_use_cases=updated_meta.get("best_use_cases"),
    )

    if "additionalInfo" in updated_meta:
        # Add additionalInfo to meta directly since it's not in the form
        current_meta["additionalInfo"] = updated_meta["additionalInfo"]

    # Update the model metadata
    updated_model = Models.update_model_metadata(id, metadata_update)
    if not updated_model:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGES.DEFAULT("Failed to refresh model metadata"),
        )

    return updated_model


@router.post("/refresh-all-metadata", response_model=Dict[str, Any])
async def refresh_all_metadata(
    form_data: RefreshModelMetadataForm = RefreshModelMetadataForm(),
    user=Depends(get_admin_user),
):
    """Refresh metadata for all base models from master data"""
    # Get all base models
    base_models = Models.get_base_models()

    results = {
        "total": len(base_models),
        "updated": 0,
        "failed": 0,
        "skipped": 0,
        "details": {}
    }

    # Update each base model
    for model in base_models:
        try:
            # Get current metadata
            current_meta = model.meta or {}

            # Populate metadata from master data
            updated_meta = {}

            if form_data.force:
                # If force is true, start with an empty dict to overwrite all values
                updated_meta = populate_model_metadata(model.id, {})
            else:
                # Otherwise, preserve existing values
                updated_meta = populate_model_metadata(model.id, current_meta)

            # Check if any changes were made
            changes_made = False
            for field in ["company", "tier", "pricing", "best_use_cases"]:
                if field in updated_meta and (field not in current_meta or current_meta[field] != updated_meta[field]):
                    changes_made = True
                    break

            if "additionalInfo" in updated_meta and (
                "additionalInfo" not in current_meta or current_meta["additionalInfo"] != updated_meta["additionalInfo"]
            ):
                changes_made = True

            if not changes_made:
                results["skipped"] += 1
                results["details"][model.id] = "No changes needed"
                continue

            # Create metadata update form
            metadata_update = ModelMetaUpdateForm(
                company=updated_meta.get("company"),
                tier=updated_meta.get("tier"),
                pricing=updated_meta.get("pricing"),
                best_use_cases=updated_meta.get("best_use_cases"),
            )

            if "additionalInfo" in updated_meta:
                # Add additionalInfo to meta directly since it's not in the form
                current_meta["additionalInfo"] = updated_meta["additionalInfo"]

            # Update the model metadata
            updated_model = Models.update_model_metadata(model.id, metadata_update)
            if updated_model:
                results["updated"] += 1
                results["details"][model.id] = "Updated successfully"
            else:
                results["failed"] += 1
                results["details"][model.id] = "Failed to update"
        except Exception as e:
            results["failed"] += 1
            results["details"][model.id] = f"Error: {str(e)}"

    return results
