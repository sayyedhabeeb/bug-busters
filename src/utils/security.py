import re
from typing import Optional
from pathlib import Path
import logging

try:
    import magic
except ImportError:
    magic = None
    # On Windows, user might need python-magic-bin
    # simple fallback will be used

logger = logging.getLogger(__name__)

class SecurityUtils:
    """
    Security validation for user inputs and files.
    """
    
    ALLOWED_MIME_TYPES = {
        'application/pdf', 
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document', # docx
        'text/plain'
    }
    
    MAX_FILE_SIZE_MB = 5
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Remove potentially dangerous characters from text input.
        Prevent XSS or basic injection attempts.
        """
        if not text:
            return ""
        # Remove HTML tags
        text = re.sub(r'<[^>]*>', '', text)
        # Remove null bytes
        text = text.replace('\0', '')
        # Allow only safe chars (alphanumeric, punctuation, whitespace)
        # This is restrictive; adjust based on need
        # text = re.sub(r'[^\w\s.,!?-@]', '', text) 
        return text.strip()
    
    @staticmethod
    def validate_file(file_content: bytes, filename: str) -> bool:
        """
        Validate file type and size.
        """
        # 1. Check Size
        if len(file_content) > SecurityUtils.MAX_FILE_SIZE_MB * 1024 * 1024:
            logger.warning(f"File {filename} too large.")
            return False
            
        # 2. Check Magic Number (MIME type)
        try:
            if magic:
                mime_type = magic.from_buffer(file_content, mime=True)
                if mime_type not in SecurityUtils.ALLOWED_MIME_TYPES:
                    logger.warning(f"File {filename} has invalid mime type: {mime_type}")
                    return False
            else:
                 logger.warning("python-magic not installed, skipping strict MIME check.")
        except Exception as e:
            logger.error(f"Error checking mime type: {e}")
            # Fallback to extension check if magic fails (less secure)
            ext = Path(filename).suffix.lower()
            if ext not in ['.pdf', '.docx', '.txt']:
                return False
                
        return True

    @staticmethod
    def is_safe_path(path: str) -> bool:
        """Prevent directory traversal."""
        return ".." not in path and not path.startswith("/") and not path.startswith("\\")
