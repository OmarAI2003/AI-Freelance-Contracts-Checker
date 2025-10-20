"""
AWS Lambda Orchestrator Function
Handles intent classification, agent routing, and A2A communication
Optimized for AWS Bedrock AgentCore Runtime
"""

import json
import boto3
import os
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import requests

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS Clients
s3_client = boto3.client('s3', region_name='us-east-1')

# Environment variables
S3_UPLOADS_BUCKET = os.environ.get('S3_UPLOADS_BUCKET', 'freelancer-uploads-897722703585')

# Agent ARNs - Update as teammates deploy their agents
AGENT_ARNS = {
    'action': os.environ.get('ACTION_AGENT_ARN', 
        'arn:aws:bedrock-agentcore:us-east-1:897722703585:runtime/freelancer_action_agent-Q83Rk73nkD'),
    'analysis': os.environ.get('ANALYSIS_AGENT_ARN'),  # None until deployed
    'explanation': os.environ.get('EXPLANATION_AGENT_ARN'),  # None until deployed
    'negotiation': os.environ.get('NEGOTIATION_AGENT_ARN'),  # None until deployed
}

# ============================================================================
# LAMBDA HANDLER
# ============================================================================

def lambda_handler(event, context):
    """
    Main Lambda handler for orchestrator.
    
    Handles API Gateway requests for chat, upload, and health check.
    """
    try:
        logger.info(f"🔍 DEBUG Event keys: {list(event.keys())}")
        logger.info(f"🔍 DEBUG Event: {json.dumps(event)[:500]}")
        
        # Parse request - handle both API Gateway v1 and v2 formats
        # v1: httpMethod, path
        # v2: requestContext.http.method, rawPath
        if 'requestContext' in event and 'http' in event.get('requestContext', {}):
            # API Gateway v2 (HTTP API)
            http_method = event['requestContext']['http']['method']
            path = event.get('rawPath', '/')
        else:
            # API Gateway v1 (REST API) or direct invoke
            http_method = event.get('httpMethod', 'GET')
            path = event.get('path', '/')
        
        body = json.loads(event.get('body', '{}')) if event.get('body') else {}
        
        logger.info(f"📨 Request: {http_method} {path}")
        
        # Route to appropriate handler
        if path == '/api/chat' and http_method == 'POST':
            return handle_chat(body, context)
        
        elif path == '/api/upload' and http_method == 'POST':
            return handle_upload(event, context)
        
        elif path == '/api/health' and http_method == 'GET':
            return handle_health(context)
        
        else:
            logger.warning(f"❌ No route matched for {http_method} {path}")
            return response(404, {'error': 'Not found', 'path': path, 'method': http_method})
    
    except Exception as e:
        logger.error(f"❌ Lambda error: {e}", exc_info=True)
        return response(500, {'error': 'Internal server error', 'message': str(e)})

# ============================================================================
# REQUEST HANDLERS
# ============================================================================

def handle_chat(body: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle chat messages - orchestrate agent communication.
    """
    try:
        # Extract parameters
        user_message = body.get('prompt', '')
        session_id = body.get('sessionId', str(uuid.uuid4()))
        requested_agent = body.get('agent')  # Optional
        
        if not user_message:
            return response(400, {'error': 'No message provided'})
        
        logger.info(f"💬 Chat - Session: {session_id}, Agent: {requested_agent or 'auto'}")
        logger.info(f"📝 Message: {user_message[:100]}...")
        
        # Classify intent if no specific agent requested
        if not requested_agent:
            intent = classify_intent(user_message, session_id)
            agent_type = intent['agent']
            logger.info(f"🧠 Intent classified: {agent_type} (confidence: {intent['confidence']})")
        else:
            agent_type = requested_agent
        
        # Route to appropriate agent
        # AgentCore handles session memory automatically!
        agent_response = route_to_agent(
            agent_type=agent_type,
            message=user_message,
            session_id=session_id
        )
        
        return response(200, {
            'response': agent_response,
            'agent': agent_type,
            'sessionId': session_id,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"❌ Chat error: {e}", exc_info=True)
        return response(500, {'error': str(e)})


def handle_upload(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle file uploads to S3.
    """
    try:
        # Parse multipart form data (simplified - use proper parser in production)
        # For now, return success to support the frontend
        
        logger.info("📄 File upload requested")
        
        return response(200, {
            'success': True,
            'message': 'File upload endpoint ready',
            'note': 'Full implementation with multipart parsing pending'
        })
    
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        return response(500, {'error': str(e)})


def handle_health(context: Any) -> Dict[str, Any]:
    """
    Health check endpoint.
    """
    agent_status = {
        'action': 'deployed' if AGENT_ARNS['action'] else 'pending',
        'analysis': 'deployed' if AGENT_ARNS['analysis'] else 'pending',
        'explanation': 'deployed' if AGENT_ARNS['explanation'] else 'pending',
        'negotiation': 'deployed' if AGENT_ARNS['negotiation'] else 'pending',
    }
    
    return response(200, {
        'status': 'healthy',
        'lambda': {
            'function': context.function_name,
            'version': context.function_version,
            'memory': f"{context.memory_limit_in_mb}MB",
        },
        'agents': agent_status,
        'timestamp': datetime.utcnow().isoformat()
    })

# ============================================================================
# INTENT CLASSIFICATION
# ============================================================================

def classify_intent(message: str, session_id: str) -> Dict[str, str]:
    """
    Classify user intent to determine which agent to route to.
    
    Uses keyword matching. AgentCore handles context automatically via session memory.
    """
    message_lower = message.lower()
    
    # Analysis patterns (pre-signing review)
    if any(kw in message_lower for kw in [
        'analyz', 'review', 'check', 'before sign', 'should i sign',
        'look at contract', 'examine', 'evaluate', 'assess'
    ]):
        return {'agent': 'analysis', 'confidence': 0.9}
    
    # Explanation patterns (legal terms)
    if any(kw in message_lower for kw in [
        'what does', 'explain', 'don\'t understand', 'clarify',
        'simplify', 'what is', 'define', 'meaning', 'means'
    ]):
        return {'agent': 'explanation', 'confidence': 0.9}
    
    # Negotiation patterns (contract changes)
    if any(kw in message_lower for kw in [
        'negotiat', 'counteroffer', 'change terms', 'modify',
        'disagree', 'want different', 'bargain', 'proposal', 'amend'
    ]):
        return {'agent': 'negotiation', 'confidence': 0.9}
    
    # Action patterns (post-signing disputes)
    if any(kw in message_lower for kw in [
        'won\'t pay', 'didn\'t pay', 'breach', 'violat', 'dispute',
        'legal action', 'sue', 'court', 'lawyer', 'after sign',
        'client problem', 'broken contract', 'not paying', 'overdue'
    ]):
        return {'agent': 'action', 'confidence': 0.9}
    
    # Default to orchestrator for general queries
    return {'agent': 'orchestrator', 'confidence': 0.5}

# ============================================================================
# AGENT ROUTING & A2A COMMUNICATION
# ============================================================================

def route_to_agent(
    agent_type: str,
    message: str,
    session_id: str
) -> str:
    """
    Route message to appropriate agent using A2A protocol.
    
    For deployed agents: Use Bedrock Agent Runtime API with built-in memory
    For pending agents: Return dummy response
    """
    # Check if agent is deployed
    agent_arn = AGENT_ARNS.get(agent_type)
    
    if agent_arn:
        # Call real agent using A2A with AgentCore's built-in session memory
        logger.info(f"🔄 A2A: Calling {agent_type} agent: {agent_arn}")
        return call_bedrock_agent_a2a(
            agent_arn=agent_arn,
            message=message,
            session_id=session_id
        )
    else:
        # Return dummy response
        logger.info(f"⏳ Dummy: {agent_type} agent not deployed yet")
        return get_dummy_response(agent_type, message)

# ============================================================================
# A2A COMMUNICATION WITH BEDROCK AGENTCORE
# ============================================================================

def call_bedrock_agent_a2a(
    agent_arn: str,
    message: str,
    session_id: str
) -> str:
    """
    Call Bedrock AgentCore agent using A2A protocol via HTTP.
    
    AgentCore automatically maintains session memory - no need for manual context management!
    """
    try:
        # Extract agent runtime endpoint from ARN
        # ARN format: arn:aws:bedrock-agentcore:region:account:runtime/agent-name-ID
        agent_id = agent_arn.split('/')[-1]
        region = agent_arn.split(':')[3]
        
        logger.info(f"📡 Invoking AgentCore agent: {agent_id}")
        logger.info(f"📨 Session: {session_id}")
        logger.info(f"💭 AgentCore will automatically maintain conversation memory")
        
        # Get AWS credentials for signing
        session = boto3.Session()
        credentials = session.get_credentials()
        
        # For now, use direct invocation via agentcore CLI approach
        # In production, would use proper AWS SDK when bedrock-agentcore is available in boto3
        
        # Temporary: Return acknowledgment that we tried
        logger.info(f"✅ Would invoke agent {agent_id} with message: {message[:50]}...")
        logger.info(f"📝 Using session: {session_id}")
        
        # Simulate response for now
        return f"""I understand you said: "{message}"

**Action Agent Response** (Testing Mode):

I'm the Action Agent, specialized in post-signing dispute resolution. I can help you with:

1. **Search Similar Cases** - Find how others resolved similar disputes
2. **Generate Action Plan** - Create step-by-step plan for your situation  
3. **Get Evidence Checklist** - Know what documentation you need
4. **Get Legal Resources** - Find relevant laws and regulations

Based on your message, this seems to be a **non-payment dispute**. 

To help you better, I need some information:
- **Contract type**: What kind of work agreement do you have?
- **Amount owed**: How much are they refusing to pay?
- **Timeline**: When was payment due?
- **Communication**: Have they responded to you?

*Note: The real Action Agent is deployed at ARN: {agent_arn}. Full integration with AgentCore Runtime API coming soon.*"""
        
    except Exception as e:
        logger.error(f"❌ A2A call failed: {e}", exc_info=True)
        return f"I apologize, but I encountered an error communicating with the specialist agent. Error: {str(e)}"

# ============================================================================
# DUMMY RESPONSES (For Testing - Until teammates deploy their agents)
# ============================================================================

def get_dummy_response(agent_type: str, message: str) -> str:
    """
    Generate dummy responses for agents not yet deployed.
    """
    responses = {
        'orchestrator': """👋 Hello! I'm your Orchestrator Agent, coordinating our team of specialists.

I understand you need assistance. Based on your message, I'll route you to the appropriate specialist.

Our team includes:
📊 **Analysis Agent** - Pre-signing contract review (Coming soon from Dev 1)
📖 **Explanation Agent** - Legal term simplification (Coming soon from Dev 2)
💼 **Negotiation Agent** - Contract negotiation support (Coming soon from Dev 3)
⚖️ **Action Agent** - Post-signing dispute resolution ✅ DEPLOYED

How can we help you today?""",

        'analysis': """📊 **Analysis Agent (Dummy Response - Dev 1 Deployment Pending)**

Thank you for reaching out! I specialize in reviewing contracts before you sign them.

I can help you with:
- Comprehensive risk identification
- Clause-by-clause detailed analysis
- Red flag detection and warnings
- Professional recommendations

To provide the best analysis, please:
1. Upload your contract document
2. Tell me your role (freelancer or client)
3. Share any specific concerns you have

*This is a simulated response. The real Analysis Agent is being developed by your teammate (Dev 1).*""",

        'explanation': """📖 **Explanation Agent (Dummy Response - Dev 2 Deployment Pending)**

Hi! I'm here to explain legal terms in plain, simple English.

I can help clarify:
- Complex legal jargon and terminology
- Specific contract clauses and provisions
- Your rights and obligations
- Legal concepts in simple terms

What specific term, clause, or concept would you like me to explain?

*This is a simulated response. The real Explanation Agent is being developed by your teammate (Dev 2).*""",

        'negotiation': """💼 **Negotiation Agent (Dummy Response - Dev 3 Deployment Pending)**

Hello! I specialize in helping you negotiate better contract terms.

I can assist with:
- Strategic counteroffer development
- Professional email templates
- Terms modification strategies
- Effective bargaining tactics

What terms would you like to negotiate? Share the current terms and what you'd like to change.

*This is a simulated response. The real Negotiation Agent is being developed by your teammate (Dev 3).*"""
    }
    
    return responses.get(agent_type, 
        "I'm still learning! This specialist agent is under development by your teammate.")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate API Gateway response.
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # Configure properly for production
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        },
        'body': json.dumps(body, default=str)
    }
