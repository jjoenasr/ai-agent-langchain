from app.gradio.schemas import FileData
from pathlib import Path
from app.core.logger_config import logger
import shutil
import os

def download_file(uploaded_file: FileData | str) -> str:
    """Process uploaded file from Gradio interface and save it locally"""
    try:
        os.makedirs("temp", exist_ok=True)
        if isinstance(uploaded_file, str):
            file_path= f"temp/{Path(uploaded_file).name}"
            if os.path.exists(file_path):
                return file_path
            shutil.copy(uploaded_file, file_path)
        else:
            file_path = f"temp/{uploaded_file.orig_name}"
            if os.path.exists(file_path):
                return file_path
            # Save the uploaded file locally
            shutil.copy(uploaded_file.path, file_path)
        logger.info(f"File uploaded and saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving uploaded file: {e}")
        
    return file_path