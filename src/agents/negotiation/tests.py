"""Tests for the Negotiation Agent"""

import pytest
from .agent import NegotiationAgent
from .tools import market_rate_tool, case_law_search

def test_market_rate_tool():
    """Test market rate tool returns valid data"""
    result = market_rate_tool(
        "Software Developer",
        "usa-california",
        experience_years=5
    )
    
    assert result['hourly_rate']['median'] > 0
    assert 'payment_terms' in result
    assert 'data_sources' in result

def test_case_law_search():
    """Test case law search returns relevant cases"""
    cases = case_law_search(
        "non_payment",
        "usa-california",
        "service_agreement"
    )
    
    assert len(cases['similar_cases']) > 0
    assert 'success_rate' in cases
    assert 'recommendation' in cases

def test_agent_initialization():
    """Test agent initializes correctly"""
    agent = NegotiationAgent()
    assert agent.model is not None
    assert agent.agent is not None

def test_clause_analysis():
    """Test contract clause analysis"""
    agent = NegotiationAgent()
    analysis = agent.analyze_clause(
        "Payment: Net 90 days at $40/hour",
        "payment_terms"
    )
    
    assert 'issues' in analysis
    assert 'risk_level' in analysis
    assert analysis['risk_level'] in ['low', 'medium', 'high']

def test_negotiation():
    """Test full negotiation workflow"""
    agent = NegotiationAgent()
    result = agent.negotiate(
        unfair_clause="Payment: Net 90 days at $40/hour",
        clause_type="payment_terms",
        freelancer_info={
            "role": "Software Developer",
            "experience_years": 5,
            "location": "usa-california"
        }
    )
    
    assert 'counter_proposal' in result
    assert 'market_data' in result
    assert 'similar_cases' in result
    assert 'negotiation_tactics' in result
    assert 'email_template' in result
    assert 'risk_level' in result

def test_memory_integration():
    """Test memory integration when enabled"""
    agent = NegotiationAgent(memory_id="test-memory")
    result = agent.negotiate(
        unfair_clause="Rate: $40/hour",
        clause_type="payment_rate",
        freelancer_info={
            "role": "Graphic Designer",
            "experience_years": 3,
            "location": "uk"
        },
        session_id="test-session"
    )
    
    assert 'counter_proposal' in result
    assert 'negotiation_tactics' in result
    # Memory validation would go here if we had access to memory client

def test_risk_assessment():
    """Test risk level assessment"""
    agent = NegotiationAgent()
    analysis = agent.analyze_clause(
        "Client owns all intellectual property rights worldwide in perpetuity",
        "ip_rights"
    )
    
    assert analysis['risk_level'] in ['low', 'medium', 'high']
    assert len(analysis['issues']) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])