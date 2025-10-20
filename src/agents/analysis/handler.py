"""
AgentCore Runtime Handler for Analysis Agent
"""

import json
import logging
from agent import AnalysisAgent

# Suppress guardrail import errors for AgentCore
try:
    import sys
    sys.path.append('/app')
except:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize agent
analysis_agent = AnalysisAgent()

def lambda_handler(event, context):
    """
    AWS Lambda handler for AgentCore Runtime
    """
    try:
        # Extract contract text from event
        body = json.loads(event.get('body', '{}'))
        contract_text = body.get('contract_text', '')
        session_id = body.get('session_id', 'default')
        
        if not contract_text:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'contract_text is required'})
            }
        
        # Analyze contract
        result = analysis_agent.analyze(contract_text, session_id)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
        
    except Exception as e:
        logger.error(f"Handler error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def agentcore_handler(event, context=None):
    """
    AgentCore Runtime handler with full capabilities
    """
    try:
        # Handle direct input
        if isinstance(event, dict):
            contract_text = event.get('contract_text', '')
            session_id = event.get('session_id', 'default')
        else:
            return {'error': 'Invalid input format'}
        
        if not contract_text:
            return {'error': 'contract_text is required'}
        
        # Use full analysis agent with KB integration
        result = analysis_agent.analyze(contract_text, session_id)
        return result
        
    except Exception as e:
        logger.error(f"AgentCore handler error: {str(e)}", exc_info=True)
        return {'error': str(e)}