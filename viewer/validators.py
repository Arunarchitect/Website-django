# viewer/validators.py

from django.core.exceptions import ValidationError
import os

def validate_360_image(image):
    """
    Validator to check if uploaded image meets size and format requirements.

    Args:
        image: Uploaded file object

    Raises:
        ValidationError: If file size or extension is invalid.
    """

    # Maximum file size in megabytes
    max_size_mb = 5

    # Check file size
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Image file size should not exceed {max_size_mb} MB.")

    # Allowed file extensions
    valid_extensions = ['.jpg', '.jpeg']

    # Extract file extension and convert to lower case
    ext = os.path.splitext(image.name)[1].lower()

    if ext not in valid_extensions:
        raise ValidationError(
            f"Unsupported file extension '{ext}'. "
            f"Allowed extensions are: {', '.join(valid_extensions)}."
        )
