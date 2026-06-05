import cloudinary
import cloudinary.uploader
import cloudinary.api

# Configure Cloudinary
cloudinary.config(
    cloud_name="dk2nmaizt",
    api_key="147418162226195",
    api_secret="aXgxKt7ogQbtxUeYXtbfDeKlAoc",
    secure=True
)

def upload_file(file_path_or_stream, folder="construction_ai", resource_type="auto"):
    """
    Uploads a file to Cloudinary.
    
    Args:
        file_path_or_stream: Can be a local path or a file-like object/stream.
        folder: The folder in Cloudinary to store the file.
        resource_type: "image", "raw", "video", or "auto".
    
    Returns:
        dict: The response from Cloudinary containing the secure URL, public_id, etc.
    """
    try:
        response = cloudinary.uploader.upload(
            file_path_or_stream,
            folder=folder,
            resource_type=resource_type
        )
        return response
    except Exception as e:
        print(f"Cloudinary upload error: {e}")
        raise e

def delete_file(public_id, resource_type="image"):
    """
    Deletes a file from Cloudinary given its public_id.
    """
    try:
        response = cloudinary.uploader.destroy(
            public_id,
            resource_type=resource_type
        )
        return response
    except Exception as e:
        print(f"Cloudinary delete error: {e}")
        raise e
