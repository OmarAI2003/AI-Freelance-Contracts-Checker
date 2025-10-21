"""
Minimal test handler to isolate startup issues
"""

import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handler(event):
    """
    Minimal test handler
    """
    logger.info(f"Test handler called with event: {event}")
    
    return {
        "status": "success",
        "message": "Test handler working",
        "event_received": event
    }