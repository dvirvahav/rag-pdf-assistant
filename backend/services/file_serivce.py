from fastapi import UploadFile
import os

UPLOAD_FOLDER = "uploads"

def save_pdf(file: UploadFile) -> str:
    """
    Saves the uploaded PDF file into the uploads folder.
    Returns the full file path.
    """

    # Make sure uploads folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Full path of where the file will be stored
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)

    # Save file in binary mode
    with open(save_path, "wb") as f:
        f.write(file.file.read())

    return save_path
