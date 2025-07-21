import logging
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Module-level variables
_logger: Optional[logging.Logger] = None
_log_file: Optional[str] = None
_configured = False

def _generate_log_filename() -> str:
    """Generate a timestamped log filename with random ID."""
    now = datetime.now()
    date_str = now.strftime("%d%m%Y")
    time_str = now.strftime("%H%M")
    random_id = str(uuid.uuid4())[:8]
    
    return f"logs/log_{date_str}_{time_str}_{random_id}.log"

def setup_logging(log_file: str = None, log_level: int = logging.INFO):
    """Initialize the logging system - call once at startup."""
    global _logger, _log_file, _configured
    
    if log_file is None:
        log_file = _generate_log_filename()
    
    _log_file = log_file
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(_log_file) if os.path.dirname(_log_file) else '.', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(_log_file, mode='a', encoding='utf-8'),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    _logger = logging.getLogger('AgentLogger')
    _configured = True
    
    # Log session start
    _logger.info("=" * 60)
    _logger.info(f"NEW SIMULATION SESSION STARTED")
    _logger.info("=" * 60)

def create_new_log_file(log_file: str = None) -> str:
    """Create a new log file - closes current file and starts fresh."""
    global _logger, _log_file, _configured
    
    if log_file is None:
        log_file = _generate_log_filename()
    
    # Remove existing handlers from our logger
    if _logger:
        for handler in _logger.handlers[:]:
            _logger.removeHandler(handler)
            handler.close()
    
    # Reset configuration flag so setup_logging can work again
    _configured = False
    
    # Now setup fresh logging
    _log_file = log_file
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(_log_file) if os.path.dirname(_log_file) else '.', exist_ok=True)
    
    # Use basicConfig now that handlers are cleared
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(_log_file, mode='w', encoding='utf-8'),  # 'w' for new file
            logging.StreamHandler()  # Also log to console
        ],
        force=True
    )
    
    _logger = logging.getLogger('AgentLogger')
    _configured = True
    
    # Log session start
    _logger.info("=" * 60)
    _logger.info(f"NEW SIMULATION SESSION STARTED")
    _logger.info("=" * 60)
    
    return _log_file

def get_logger() -> logging.Logger:
    """Get the logger instance."""
    if not _configured:
        setup_logging()
    return _logger

def get_current_log_file() -> Optional[str]:
    """Get the current log file path."""
    return _log_file

def _format_details(details: Dict[str, Any]) -> str:
    """Format details dictionary into a readable string."""
    formatted_parts = []
    
    for key, value in details.items():
        if key == "interaction_duration":
            formatted_parts.append(f"Duration: {value:.2f}s")
        elif key == "recipient":
            formatted_parts.append(f"To: Agent {value:03d}")
        elif key == "sender":
            formatted_parts.append(f"From: Agent {value:03d}")
        elif key == "type":
            formatted_parts.append(f"Type: {value}")
        elif key == "details" and isinstance(value, dict):
            # Handle nested details
            nested = _format_details(value)
            if nested:
                formatted_parts.append(f"Details: ({nested})")
        else:
            formatted_parts.append(f"{key}: {value}")
    
    return " | ".join(formatted_parts)

def log_agent_action(unique_id: int, step: int, action: str, details: Dict[str, Any] = None):
    """Log an agent action with structured format."""
    if not _configured:
        setup_logging()
    
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds
    
    base_msg = f"[Step {step:03d}] Agent {unique_id} - {action.upper()}"
    
    if details:
        details_str = _format_details(details)
        full_msg = f"{base_msg} | {details_str}"
    else:
        full_msg = base_msg
        
    _logger.info(full_msg)

def log_model_event(step: int, event: str, details: Dict[str, Any] = None):
    """Log model-level events."""
    if not _configured:
        setup_logging()
    
    base_msg = f"[Step {step:03d}] MODEL - {event.upper()}"
    
    if details:
        details_str = _format_details(details)
        full_msg = f"{base_msg} | {details_str}"
    else:
        full_msg = base_msg
        
    _logger.info(full_msg)

def log_session_end():
    """Log the end of a simulation session."""
    if not _configured:
        setup_logging()
    
    _logger.info("=" * 60)
    _logger.info("SIMULATION SESSION ENDED")
    _logger.info("=" * 60)

def clear_logs():
    """Clear the current log file."""
    if _log_file:
        open(_log_file, 'w').close()
        _logger.info("Log file cleared")

def set_log_level(level: int):
    """Change the logging level."""
    if _logger:
        _logger.setLevel(level)

def enable_logging():
    """Enable logging."""
    if _logger:
        _logger.disabled = False

def disable_logging():
    """Disable logging."""
    if _logger:
        _logger.disabled = True