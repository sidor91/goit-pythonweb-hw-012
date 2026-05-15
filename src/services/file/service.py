import cloudinary  # type: ignore
import cloudinary.uploader  # type: ignore
from fastapi import UploadFile


class UploadFileService:
    """Upload file service abstraction for Cloudinary image hosting."""

    def __init__(self, cloud_name: str, api_key: int, api_secret: str):
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(  # type: ignore
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file: UploadFile, username: str) -> str:
        """Upload an avatar file to Cloudinary and return a public URL."""
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)  # type: ignore
        src_url = cloudinary.CloudinaryImage(public_id).build_url(  # type: ignore
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url  # type: ignore
