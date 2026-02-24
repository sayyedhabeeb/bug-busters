from docx import Document
from pathlib import Path
import logging
from .base import BaseParser

logger = logging.getLogger(__name__)

class DOCXParser(BaseParser):
    """Reliable .docx text extraction using python-docx."""
    
    def extract_text(self, file_path: Path) -> str:
        try:
            doc = Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return "\n".join(full_text).strip()
        except Exception as e:
            logger.error(f"Error parsing DOCX {file_path}: {e}")
            return ""

    def supported_extensions(self) -> list[str]:
        return [".docx"]
