
from core.cloudinary_config import cloudinary
import cloudinary.uploader

def upload_profile_picture(file):
    """
    Upload a profile picture to Cloudinary.
    """

    result = cloudinary.uploader.upload(
        file.file,
        folder="stylemind/profiles",
        resource_type="image"
    )

    return {
        "image_url": result.get("secure_url"),
        "public_id": result.get("public_id")
    }
