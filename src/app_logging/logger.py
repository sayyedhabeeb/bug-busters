import json
import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the LogRecord.
    """
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "path": record.pathname
        }
        
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)


class LoggerSetup:
    """Compatibility logging bootstrap used by main entrypoint."""

    @staticmethod
    def setup(log_dir: Path = Path("logs"), level: int = logging.INFO, json_format: bool = False) -> None:
        """Configure root logging once with console and rotating file handlers."""
        root_logger = logging.getLogger()
        if getattr(root_logger, "_project_logging_configured", False):
            return

        root_logger.setLevel(level)
        log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
        )
        file_handler.setFormatter(
            JsonFormatter()
            if json_format
            else logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        root_logger._project_logging_configured = True


def get_logger(name: str) -> logging.Logger:
    """Compatibility helper to fetch a named logger."""
    return logging.getLogger(name)

def setup_logger(name: str, log_dir: Path = Path("logs"), level: int = logging.INFO) -> logging.Logger:
    """
    Setup a logger with console and file handlers.
    
    Args:
        name: Logger name
        log_dir: Directory to store logs
        level: Logging level
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
        
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # JSON Formatter for Files
    json_formatter = JsonFormatter()
    
    # Standard Formatter for Console
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File Handler (Rotating)
    file_handler = RotatingFileHandler(
        log_dir / "app.log", 
        maxBytes=10*1024*1024, # 10MB
        backupCount=5
    )
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

# Create specific loggers
pred_logger = setup_logger("prediction_logger", Path("logs/predictions"))
perf_logger = setup_logger("performance_logger", Path("logs/performance"))
sec_logger = setup_logger("security_logger", Path("logs/security"))
