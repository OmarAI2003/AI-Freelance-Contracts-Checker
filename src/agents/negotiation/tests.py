"""Tests for the Negotiation Agent"""

import pytest
from .agent import NegotiationAgent

@pytest.fixture
def agent():
    return NegotiationAgent()

def test_analyze_contract(agent):
    contract_text = """Payment Terms: Net 90 days. Client reserves the right to delay payment 
    without notice. No late payment penalties apply."""
    
    result = agent.analyze_contract(contract_text)
    assert "analysis" in result
    assert len(result["analysis"]) > 0
    assert "90 days" in result["analysis"].lower()

def test_explain_terms(agent):
    terms = """Intellectual Property Rights: The Service Provider hereby assigns 
    all worldwide intellectual property rights in the Deliverables to the Client."""
    
    explanation = agent.explain_terms(terms)
    assert len(explanation) > 0
    assert "rights" in explanation.lower()
    assert "property" in explanation.lower()

def test_negotiate_terms(agent):
    current_terms = """Payment Terms: Net 90 days at $40/hour"""
    desired_changes = [
        "Reduce payment terms to Net 30",
        "Increase rate to $120/hour based on market rates",
        "Add late payment penalty of 1.5% monthly"
    ]
    context = {
        "experience": "5 years",
        "role": "Senior Software Developer",
        "location": "USA"
    }
    
    result = agent.negotiate_terms(current_terms, desired_changes, context)
    assert "strategy" in result
    assert len(result["strategy"]) > 0

def test_get_legal_advice(agent):
    contract_text = """Non-compete: Service Provider agrees not to work for any 
    competing business worldwide for 5 years after contract termination."""
    question = "Is this non-compete clause enforceable in California?"
    
    advice = agent.get_legal_advice(contract_text, question)
    assert len(advice) > 0
    assert "california" in advice.lower()
    assert "non-compete" in advice.lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

if __name__ == "__main__":
    pytest.main([__file__, "-v"])