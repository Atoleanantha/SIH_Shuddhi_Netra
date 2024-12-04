import cloudinary.uploader

# Upload the image
def upload_to_cloudinary(file,folder):
    try:
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            file,
            folder=folder
        )
        return upload_result.get("secure_url")
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None


