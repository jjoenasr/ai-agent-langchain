from gradio.data_classes import FileData
from pydantic import BaseModel
from typing import Optional

class MultimodalMessage(BaseModel):
    text: str = ""
    files: Optional[list[FileData | str]] = []