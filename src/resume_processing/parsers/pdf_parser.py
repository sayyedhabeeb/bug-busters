import pdfplumber
from pathlib import Path
import logging
from .base import BaseParser

logger = logging.getLogger(__name__)

class PDFParser(BaseParser):
    """High-fidelity PDF text extraction using pdfplumber."""
    
    def extract_text(self, file_path: Path) -> str:
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {e}")
            return ""

    def supported_extensions(self) -> list[str]:
        return [".pdf"]
