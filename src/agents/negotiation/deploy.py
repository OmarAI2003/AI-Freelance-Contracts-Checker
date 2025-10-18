"""Deployment configuration for AgentCore Runtime"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from .agent import NegotiationAgent
import json

app = BedrockAgentCoreApp()

# Load configuration
with open('src/infrastructure/config.json') as f:
    config = json.load(f)
    MEMORY_ID = config['memory_id']

@app.entrypoint
async def negotiate_terms(payload):
    """AgentCore Runtime entrypoint for Negotiation Agent"""
    
    # Extract inputs
    unfair_clause = payload['input']['unfair_clause']
    clause_type = payload['input']['clause_type']
    freelancer_info = payload['input']['freelancer_info']
    session_id = payload.get('session_id', 'default')
    
    # Initialize agent
    agent = NegotiationAgent(memory_id=MEMORY_ID)
    
    # Generate negotiation response
    result = agent.negotiate(
        unfair_clause,
        clause_type,
        freelancer_info,
        session_id
    )
    
    return {
        "negotiation": result,
        "agent": "negotiation",
        "session_id": session_id
    }

if __name__ == "__main__":
    app.run()