"""Deployment configuration for AgentCore Runtime"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from .agent import NegotiationAgent
import json
import os

app = BedrockAgentCoreApp()

# Initialize agent once
agent = NegotiationAgent()

@app.action(name="analyze_contract", description="Analyze contract for potential issues and unfair terms")
async def analyze_contract(payload):
    """Analyze contract clauses for issues"""
    try:
        contract_text = payload['input']['contract_text']
        session_id = payload.get('session_id', 'default')
        
        result = agent.analyze_contract(contract_text)
        
        return {
            "analysis": result['analysis'],
            "action": "analyze_contract",
            "session_id": session_id
        }
    except Exception as e:
        return {
            "error": str(e),
            "action": "analyze_contract"
        }

@app.action(name="explain_terms", description="Explain legal terms in simple language")
async def explain_terms(payload):
    """Explain contract terms in simple language"""
    try:
        terms = payload['input']['terms']
        session_id = payload.get('session_id', 'default')
        
        explanation = agent.explain_terms(terms)
        
        return {
            "explanation": explanation,
            "action": "explain_terms",
            "session_id": session_id
        }
    except Exception as e:
        return {
            "error": str(e),
            "action": "explain_terms"
        }

@app.action(name="negotiate_terms", description="Generate negotiation strategies and counterproposals")
async def negotiate_terms(payload):
    """Generate negotiation strategy"""
    try:
        current_terms = payload['input']['current_terms']
        desired_changes = payload['input']['desired_changes']
        context = payload['input'].get('context', {})
        session_id = payload.get('session_id', 'default')
        
        result = agent.negotiate_terms(current_terms, desired_changes, context)
        
        return {
            "strategy": result['strategy'],
            "action": "negotiate_terms",
            "session_id": session_id
        }
    except Exception as e:
        return {
            "error": str(e),
            "action": "negotiate_terms"
        }

@app.action(name="legal_advice", description="Provide legal guidance on contract terms")
async def legal_advice(payload):
    """Provide legal advice on contract terms"""
    try:
        contract_text = payload['input']['contract_text']
        question = payload['input']['question']
        session_id = payload.get('session_id', 'default')
        
        advice = agent.get_legal_advice(contract_text, question)
        
        return {
            "advice": advice,
            "action": "legal_advice",
            "session_id": session_id
        }
    except Exception as e:
        return {
            "error": str(e),
            "action": "legal_advice"
        }

# Main entrypoint for routing
@app.entrypoint
async def main(payload):
    """Main entrypoint that routes to appropriate action"""
    action = payload.get('action', 'negotiate_terms')
    
    if action == "analyze_contract":
        return await analyze_contract(payload)
    elif action == "explain_terms":
        return await explain_terms(payload)
    elif action == "negotiate_terms":
        return await negotiate_terms(payload)
    elif action == "legal_advice":
        return await legal_advice(payload)
    else:
        return {
            "error": f"Unknown action: {action}",
            "available_actions": ["analyze_contract", "explain_terms", "negotiate_terms", "legal_advice"]
        }

if __name__ == "__main__":
    app.run()