import cloudinary.uploader

# Upload the image
def upload_to_cloudinary(image_file):
    try:
        response = cloudinary.uploader.upload(image_file)
        return response['secure_url']  # URL of the uploaded image
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None


