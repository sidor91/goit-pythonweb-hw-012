from io import BytesIO

import pytest
from fastapi import UploadFile

from src.services.file.service import UploadFileService


class DummyUploader:
    @staticmethod
    def upload(file, public_id=None, overwrite=False):
        return {"version": 123}


class DummyImage:
    def __init__(self, public_id):
        self.public_id = public_id

    def build_url(self, width=None, height=None, crop=None, version=None):
        return f"https://example.com/{self.public_id}/{version}"


@pytest.mark.asyncio
async def test_upload_file_generates_cloudinary_url(monkeypatch):
    monkeypatch.setattr("src.services.file.service.cloudinary.uploader", DummyUploader)
    monkeypatch.setattr(
        "src.services.file.service.cloudinary.CloudinaryImage", DummyImage
    )

    upload_service = UploadFileService("name", 1, "secret")
    test_file = UploadFile(filename="avatar.png", file=BytesIO(b"dummy data"))

    url = upload_service.upload_file(test_file, "testuser")
    assert url == "https://example.com/RestApp/testuser/123"
