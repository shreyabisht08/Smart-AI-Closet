
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.profile import (
    UserProfileUpdate,
    UserProfileResponse
)
from core.dependencies import get_current_user

from fastapi import UploadFile, File, HTTPException, status
from PIL import Image, UnidentifiedImageError
from io import BytesIO

from services.profile_service import upload_profile_picture
from fastapi import HTTPException, status
import cloudinary.uploader


router = APIRouter(
    prefix="/profile",
    tags=["User Profile"]
)


@router.put("/me", response_model=UserProfileResponse)
def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Get only the fields provided by the user
    update_data = profile_data.model_dump(exclude_unset=True)

    # Update user information
    for field, value in update_data.items():
        setattr(current_user, field, value)

    # Save changes in MySQL
    db.commit()
    db.refresh(current_user)

    return current_user

@router.post("/me/picture", response_model=UserProfileResponse)
def upload_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Allowed image formats
    allowed_formats = {"JPEG", "PNG", "WEBP"}
    allowed_content_types = {
        "image/jpeg",
        "image/png",
        "image/webp"
    }

    # Validate declared content type
    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG and WEBP images are allowed"
        )

    # Read at most 5 MB plus one byte
    image_data = file.file.read(5 * 1024 * 1024 + 1)

    if len(image_data) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Image size must not exceed 5 MB"
        )

    # Validate actual image content
    try:
        image = Image.open(BytesIO(image_data))

        if image.format not in allowed_formats:
            raise HTTPException(
                status_code=400,
                detail="Unsupported image format"
            )

        image.verify()

    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise HTTPException(
            status_code=400,
            detail="Invalid or corrupted image"
        )

    # Reset file pointer before uploading
    file.file.seek(0)

    # Upload to Cloudinary
    result = upload_profile_picture(file)

    old_public_id = current_user.cloudinary_public_id

    try:
        # Save image details in MySQL
        current_user.profile_picture = result["image_url"]
        current_user.cloudinary_public_id = result["public_id"]

        db.commit()
        db.refresh(current_user)

    except Exception:
        db.rollback()

        # Remove newly uploaded image if database update fails
        cloudinary.uploader.destroy(result["public_id"])
        raise

    # Delete old image only after successful database update
    if old_public_id:
        cloudinary.uploader.destroy(old_public_id)

    return current_user

@router.delete("/me/picture", response_model=UserProfileResponse)
def delete_profile_picture(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check whether the user has a profile picture
    if not current_user.cloudinary_public_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile picture found"
        )

    # Delete the image from Cloudinary
    try:
        result = cloudinary.uploader.destroy(
            current_user.cloudinary_public_id,
            resource_type="image",
            invalidate=True
        )

        if result.get("result") not in ["ok", "not found"]:
            raise HTTPException(
                status_code=502,
                detail="Could not delete image from Cloudinary"
            )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Cloudinary image deletion failed"
        )

    # Clear the image details from MySQL
    current_user.profile_picture = None
    current_user.cloudinary_public_id = None

    try:
        db.commit()
        db.refresh(current_user)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Image deleted, but profile update failed"
        )

    return current_user

@router.patch("/me/deactivate", response_model=UserProfileResponse)
def deactivate_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already deactivated"
        )

    current_user.is_active = False

    try:
        db.commit()
        db.refresh(current_user)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not deactivate account"
        )

    return current_user