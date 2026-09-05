import os
from imagekitio import ImageKit

# Initialize ImageKit
# Searched for Private and Public key variables in the .env file
def get_imagekit_client():
    return ImageKit()

# Video Optimization per ImageKit docs
def get_optimized_video_url(base_url:str) -> str:
    if "?" in base_url:
        return f"{base_url}&tr=q-50,f-auto"
    return f"{base_url}?tr=q-50,f-auto"

# ImageKit offers a video loading format.
# This handles loading a video based off the user's internet connection
def get_streaming_url(base_url: str) -> str:
    return f"{base_url}/ik-master.m3u8?tr=sr-240_360_480_720_1080"

# ImageKit Thumbnail loader
def get_thumbnail_url(base_url: str) -> str:
    return f"{base_url}/ik-thumbnail.jpg"

# Upload Video to ImageKit
def upload_video(file_data: bytes, file_name: str, folder: str = "videos") -> dict:
    public_key = os.environ.get("IMAGEKIT_PUBLIC_KEY")

    client = get_imagekit_client()

    response = client.files.upload(
        file=file_data,
        file_name=file_name,
        folder=folder,
        public_key=public_key
    )

    print("UPLOAD RESPONSE",response)

    return {
        "file_id": response.file_id,
        "url": response.url
    }

def upload_thumbnail(file_data: bytes, file_name: str, folder: str = "thumbnails") -> dict:
    # Possibly decode in case a base64 format
    import base64
    public_key = os.environ.get("IMAGEKIT_PUBLIC_KEY")

    if file_data.startswith("data"):
        base64_data = file_data.split(",", 1)[1]
        image_bytes = base64.b64decode(base64_data)
    else:
        image_bytes = base64.b64decode(file_data)

    # Initialize imagekit and upload
    client = get_imagekit_client()
    response = client.files.upload(
        file=image_bytes,
        file_name=file_name,
        folder=folder,
        public_key=public_key
    )

    return {
        "file_id": response.file_id,
        "url": response.url
    }