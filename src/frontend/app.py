"""
Freelancer Legal Assistant - Backend Server
Handles orchestration, A2A communication, and agent routing
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import boto3
import json
import os
import logging
from datetime import datetime
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            static_folder='static',
            template_folder='.')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app)

# AWS Configuration
AWS_REGION = 'us-east-1'
ACCOUNT_ID = '897722703585'

# Agent ARNs - Update these as teammates deploy their agents
AGENT_ARNS = {
    'action': 'arn:aws:bedrock-agentcore:us-east-1:897722703585:runtime/freelancer_action_agent-Q83Rk73nkD',
    'analysis': None,  # TODO: Update when Dev 1 deploys
    'explanation': None,  # TODO: Update when Dev 2 deploys
    'negotiation': None,  # TODO: Update when Dev 3 deploys
}

# Initialize boto3 clients
try:
    bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name=AWS_REGION)
    logger.info("✅ AWS Bedrock Agent Runtime client initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize AWS client: {e}")
    bedrock_agent_runtime = None

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve the main application page."""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'agents': {
            'action': 'deployed' if AGENT_ARNS['action'] else 'pending',
            'analysis': 'deployed' if AGENT_ARNS['analysis'] else 'pending',
            'explanation': 'deployed' if AGENT_ARNS['explanation'] else 'pending',
            'negotiation': 'deployed' if AGENT_ARNS['negotiation'] else 'pending',
        }
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint - handles orchestration and agent routing.
    
    Request body:
    {
        "prompt": "user message",
        "context": "optional context from previous messages",
        "sessionId": "session-xyz",
        "agent": "optional specific agent to call"
    }
    """
    try:
        data = request.json
        user_message = data.get('prompt', '')
        context = data.get('context', '')
        session_id = data.get('sessionId', str(uuid.uuid4()))
        requested_agent = data.get('agent')  # Optional: force specific agent
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        logger.info(f"📨 Chat request - Session: {session_id}, Agent: {requested_agent or 'auto'}")
        logger.info(f"💬 Message: {user_message[:100]}...")
        
        # Classify intent if no specific agent requested
        if not requested_agent:
            intent = classify_intent(user_message)
            agent_type = intent['agent']
        else:
            agent_type = requested_agent
        
        logger.info(f"🎯 Routing to: {agent_type}")
        
        # Route to appropriate agent
        response_text = route_to_agent(
            agent_type=agent_type,
            message=user_message,
            context=context,
            session_id=session_id
        )
        
        return jsonify({
            'response': response_text,
            'agent': agent_type,
            'sessionId': session_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error in chat endpoint: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_contract():
    """Handle contract file upload."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save file temporarily
        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = os.path.join('uploads', filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(filepath)
        
        # TODO: Extract text from file (PDF/DOCX processing)
        # For now, just return success
        
        logger.info(f"📄 File uploaded: {filename}")
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'File uploaded successfully'
        })
        
    except Exception as e:
        logger.error(f"❌ Error uploading file: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ORCHESTRATOR LOGIC
# ============================================================================

def classify_intent(message):
    """
    Classify user intent to determine which agent to route to.
    
    Returns:
        dict: {
            'agent': str,  # 'analysis', 'explanation', 'negotiation', 'action', 'orchestrator'
            'confidence': float,
            'keywords': list
        }
    """
    message_lower = message.lower()
    
    # Analysis patterns
    analysis_keywords = [
        'analyz', 'review', 'check', 'before sign', 'should i sign',
        'look at.*contract', 'examine', 'evaluate', 'assess'
    ]
    if any(keyword in message_lower for keyword in analysis_keywords):
        return {
            'agent': 'analysis',
            'confidence': 0.9,
            'keywords': analysis_keywords
        }
    
    # Explanation patterns
    explanation_keywords = [
        'what does.*mean', 'explain', "don't understand", 'clarify',
        'simplify', 'what is', 'define', 'interpretation', 'means'
    ]
    if any(keyword in message_lower for keyword in explanation_keywords):
        return {
            'agent': 'explanation',
            'confidence': 0.9,
            'keywords': explanation_keywords
        }
    
    # Negotiation patterns
    negotiation_keywords = [
        'negotiat', 'counteroffer', 'change terms', 'modify',
        'disagree', 'want different', 'bargain', 'proposal', 'amend'
    ]
    if any(keyword in message_lower for keyword in negotiation_keywords):
        return {
            'agent': 'negotiation',
            'confidence': 0.9,
            'keywords': negotiation_keywords
        }
    
    # Action patterns (disputes, post-signing issues)
    action_keywords = [
        "won't pay", "didn't pay", 'breach', 'violat', 'dispute',
        'legal action', 'sue', 'court', 'lawyer', 'after sign',
        'client problem', 'broken contract', 'not paying'
    ]
    if any(keyword in message_lower for keyword in action_keywords):
        return {
            'agent': 'action',
            'confidence': 0.9,
            'keywords': action_keywords
        }
    
    # Default to orchestrator for general queries
    return {
        'agent': 'orchestrator',
        'confidence': 0.5,
        'keywords': []
    }

def route_to_agent(agent_type, message, context, session_id):
    """
    Route message to appropriate agent (real or dummy).
    
    Args:
        agent_type: 'analysis', 'explanation', 'negotiation', 'action', 'orchestrator'
        message: User's message
        context: Conversation context
        session_id: Session ID for memory
    
    Returns:
        str: Agent's response
    """
    # Check if agent is deployed
    if agent_type == 'action' and AGENT_ARNS['action']:
        # Call real Action Agent
        return call_bedrock_agent(
            agent_arn=AGENT_ARNS['action'],
            message=message,
            session_id=session_id
        )
    
    elif agent_type in ['analysis', 'explanation', 'negotiation'] and AGENT_ARNS.get(agent_type):
        # Call real specialist agent when available
        return call_bedrock_agent(
            agent_arn=AGENT_ARNS[agent_type],
            message=message,
            session_id=session_id
        )
    
    else:
        # Return dummy response for agents not yet deployed
        return get_dummy_response(agent_type, message)

# ============================================================================
# BEDROCK AGENT CALLS (A2A Communication)
# ============================================================================

def call_bedrock_agent(agent_arn, message, session_id):
    """
    Call a Bedrock AgentCore agent using A2A communication.
    
    Args:
        agent_arn: Full ARN of the agent
        message: User message to send
        session_id: Session ID for memory continuity
    
    Returns:
        str: Agent's response
    """
    if not bedrock_agent_runtime:
        logger.error("❌ Bedrock client not initialized")
        return "Sorry, I'm having trouble connecting to the agent. Please try again later."
    
    try:
        # Extract agent ID from ARN
        # ARN format: arn:aws:bedrock-agentcore:region:account:runtime/agent-name-ID
        agent_id = agent_arn.split('/')[-1].split('-')[0]
        
        logger.info(f"🔄 Calling agent: {agent_id} with session: {session_id}")
        
        # Note: For AgentCore, we use invoke_agent with the agentcore CLI approach
        # Since we deployed with agentcore CLI, we need to use the HTTP endpoint
        # For now, using the CLI invoke approach via subprocess
        
        import subprocess
        import json
        
        # Build the payload
        payload = {
            "prompt": message,
            "sessionId": session_id
        }
        
        # For production, use boto3 invoke_agent
        # For now, simulate the call
        logger.warning("⚠️ Using simulated agent call - implement boto3 invoke_agent for production")
        
        # TODO: Implement proper boto3 call:
        # response = bedrock_agent_runtime.invoke_agent(
        #     agentId=agent_id,
        #     agentAliasId='TSTALIASID',
        #     sessionId=session_id,
        #     inputText=message
        # )
        
        # For now, return a placeholder
        return f"[Real Action Agent Response]\n\nI received your message: '{message}'\n\nI'm your Action Agent, ready to help with post-signing disputes, non-payment issues, and legal action guidance.\n\n(Note: Full integration pending - this is a test response)"
        
    except Exception as e:
        logger.error(f"❌ Error calling Bedrock agent: {e}", exc_info=True)
        return "I apologize, but I encountered an error processing your request. Please try again."

# ============================================================================
# DUMMY RESPONSES (For Testing Before Teammates Deploy)
# ============================================================================

def get_dummy_response(agent_type, message):
    """
    Generate dummy responses for agents not yet deployed.
    Used for testing orchestrator logic before teammates finish.
    """
    responses = {
        'orchestrator': """👋 Hello! I'm your Orchestrator Agent, coordinating our team of specialists.

I can see you need assistance. Let me analyze your message and route you to the best specialist.

Our team includes:
📊 **Analysis Agent** - Pre-signing contract review
📖 **Explanation Agent** - Legal term simplification  
💼 **Negotiation Agent** - Contract negotiation support
⚖️ **Action Agent** - Post-signing dispute resolution

How can we help you today?""",

        'analysis': """📊 **Analysis Agent (Dummy Response)**

Thank you for reaching out! I specialize in reviewing contracts before you sign them.

I can help you with:
- Risk identification
- Clause-by-clause analysis
- Red flag detection
- Recommendation generation

To provide the best analysis, please:
1. Upload your contract (or paste key sections)
2. Tell me your role (freelancer or client)
3. Share any specific concerns

*Note: This is a test response. Real Analysis Agent coming soon from Dev 1!*""",

        'explanation': """📖 **Explanation Agent (Dummy Response)**

Hi! I'm here to explain legal terms in plain English.

I can help clarify:
- Complex legal jargon
- Contract clauses
- Rights and obligations
- Legal concepts

What specific term or clause would you like me to explain?

*Note: This is a test response. Real Explanation Agent coming soon from Dev 2!*""",

        'negotiation': """💼 **Negotiation Agent (Dummy Response)**

Hello! I specialize in helping you negotiate better contract terms.

I can assist with:
- Counteroffer strategy
- Email templates
- Terms modification
- Bargaining tactics

What terms would you like to negotiate?

*Note: This is a test response. Real Negotiation Agent coming soon from Dev 3!*""",

        'action': """⚖️ **Action Agent (Dummy Response)**

I'm here to help with post-signing disputes and legal action.

I specialize in:
- Non-payment disputes
- Contract breaches
- Legal resource guidance
- Action plan generation

Tell me about your issue and I'll help you take appropriate action.

*Note: This is a test response. Real Action Agent is deployed but A2A integration pending!*"""
    }
    
    return responses.get(agent_type, "I'm still learning! This agent is under development.")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def extract_agent_id_from_arn(arn):
    """Extract agent ID from full ARN."""
    # ARN: arn:aws:bedrock-agentcore:region:account:runtime/agent-name-ID
    return arn.split('/')[-1]

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🚀 Freelancer Legal Assistant - Backend Server")
    logger.info("=" * 60)
    logger.info(f"AWS Region: {AWS_REGION}")
    logger.info(f"Account: {ACCOUNT_ID}")
    logger.info("\n📋 Agent Status:")
    for agent_name, arn in AGENT_ARNS.items():
        status = "✅ DEPLOYED" if arn else "⏳ PENDING"
        logger.info(f"  {agent_name.upper()}: {status}")
    logger.info("=" * 60)
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
