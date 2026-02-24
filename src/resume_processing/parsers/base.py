from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

class BaseParser(ABC):
    """Abstract base class for all file-specific parsers."""
    
    @abstractmethod
    def extract_text(self, file_path: Path) -> str:
        """Extract raw text from the given file."""
        pass

    def supports(self, file_path: Path) -> bool:
        """Check if this parser supports the given file extension."""
        return file_path.suffix.lower() in self.supported_extensions()

    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """Return a list of supported file extensions."""
        pass
