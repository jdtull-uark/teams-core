"""
Enhanced logging utilities for the framework.
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

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
    
    return f"logs/simulation_{date_str}_{time_str}_{random_id}.log"

def setup_logging(log_file: str = None, log_level: str = "INFO"):
    """Initialize the logging system."""
    global _logger, _log_file, _configured
    
    if log_file is None:
        log_file = _generate_log_filename()
    
    _log_file = log_file
    
    # Create logs directory if it doesn't exist
    Path(_log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(_log_file, mode='w', encoding='utf-8'),
            logging.StreamHandler()
        ],
        force=True
    )
    
    _logger = logging.getLogger('FrameworkLogger')
    _configured = True
    
    # Log session start
    _logger.info("=" * 60)
    _logger.info("NEW SIMULATION SESSION STARTED")
    _logger.info("=" * 60)

def get_logger() -> logging.Logger:
    """Get the logger instance."""
    if not _configured:
        setup_logging()
    return _logger

def log_agent_action(agent_id: int, step: int, action: str, details: Dict[str, Any] = None):
    """Log an agent action."""
    if not _configured:
        setup_logging()
    
    base_msg = f"[Step {step:03d}] Agent {agent_id:03d} - {action.upper()}"
    
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

def _format_details(details: Dict[str, Any]) -> str:
    """Format details dictionary into a readable string."""
    formatted_parts = []
    
    for key, value in details.items():
        if isinstance(value, float):
            formatted_parts.append(f"{key}: {value:.3f}")
        elif isinstance(value, dict):
            nested = _format_details(value)
            if nested:
                formatted_parts.append(f"{key}: ({nested})")
        elif isinstance(value, list) and len(value) <= 3:
            formatted_parts.append(f"{key}: {value}")
        elif isinstance(value, list):
            formatted_parts.append(f"{key}: [{len(value)} items]")
        else:
            formatted_parts.append(f"{key}: {value}")
    
    return " | ".join(formatted_parts)

def log_session_end():
    """Log the end of a simulation session."""
    if not _configured:
        setup_logging()
    
    _logger.info("=" * 60)
    _logger.info("SIMULATION SESSION ENDED")
    _logger.info("=" * 60)