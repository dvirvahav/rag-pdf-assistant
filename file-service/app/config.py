import os

# Base directory where uploaded files are stored.
# Using absolute path for Docker volume mount
STORAGE_PATH = "/app/storage/uploads"

# Ensure folder exists at startup
os.makedirs(STORAGE_PATH, exist_ok=True)
