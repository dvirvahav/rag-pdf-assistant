from fastapi import UploadFile
import os
from backend.config import settings

def save_pdf(file: UploadFile) -> str:
    """
    Saves the uploaded PDF file into the uploads folder.
    Returns the full file path.
    """

    # Get upload folder from settings (absolute path)
    upload_folder = settings.UPLOAD_FOLDER

    # Make sure uploads folder exists
    os.makedirs(upload_folder, exist_ok=True)

    # Full path of where the file will be stored
    save_path = os.path.join(upload_folder, file.filename)

    # Save file in binary mode
    with open(save_path, "wb") as f:
        f.write(file.file.read())

    return save_path
