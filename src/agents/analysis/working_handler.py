"""
Handler that copies the exact working pattern from test_file_analysis.py
"""

import asyncio
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handler(event):
    """
    Handler that mimics the exact working test_file_analysis.py pattern
    """
    logger.info(f"Handler called with event: {event}")
    
    try:
        # Import exactly like the working test
        from agent import AnalysisAgent
        
        # Get contract text
        contract_text = event.get('contract_text', '')
        session_id = event.get('session_id', 'default')
        
        if not contract_text:
            return {'error': 'contract_text is required'}
        
        # Create agent exactly like the working test
        agent = AnalysisAgent()
        
        # Call the method that works - but with text instead of file
        result = asyncio.run(agent._analyze_text(contract_text, session_id))
        
        logger.info(f"Analysis completed: {result.get('risk_level')}")
        return result
        
    except Exception as e:
        logger.error(f"Handler error: {str(e)}", exc_info=True)
        return {'error': str(e)}