"""
Minimal file parser for Vercel deployment - no heavy dependencies
"""

import logging
import base64
import os

logger = logging.getLogger(__name__)

def parse_attachments(attachments, upload_dir=None):
    """
    Minimal attachment parser for Vercel deployment
    Returns empty string since we can't process files without heavy dependencies
    """
    if not attachments:
        return ""
    
    logger.info(f"Minimal parser: Skipping {len(attachments)} attachments (no processing capabilities in minimal mode)")
    
    # For minimal deployment, we can't process actual file content
    # Return a placeholder that indicates attachments were present
    attachment_names = []
    for attachment in attachments:
        if isinstance(attachment, dict):
            filename = attachment.get('filename', 'unknown')
            attachment_names.append(filename)
    
    if attachment_names:
        return f"Attachments present: {', '.join(attachment_names)} (content not processed in minimal mode)"
    
    return "Attachments present but not processed in minimal mode"