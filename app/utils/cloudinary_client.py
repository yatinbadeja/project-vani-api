from app.Config import ENV_PROJECT
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from fastapi import UploadFile


class CloudinaryClient:
    def __init__(self, cloud_name, api_key, api_secret):
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret

    def upload_file(self, file: UploadFile):
        cloudinary_config = {
            "cloud_name": self.cloud_name,
            "api_key": self.api_key,
            "api_secret": self.api_secret,
        }

        # Upload the file to Cloudinary
        upload_result = upload(file.file, **cloudinary_config)

        # Get the public URL of the uploaded image
        public_url, options = cloudinary_url(
            upload_result["public_id"], **cloudinary_config, secure=True, format="jpg"
        )

        return public_url


cloudinary_client = CloudinaryClient(
    cloud_name=ENV_PROJECT.CLOUDINARY_CLOUD_NAME,
    api_key=ENV_PROJECT.CLOUDINARY_API_KEY,
    api_secret=ENV_PROJECT.CLOUDINARY_API_SECRET,
)
