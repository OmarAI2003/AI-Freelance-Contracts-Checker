"""Main Negotiation Agent implementation"""

from typing import Dict, Optional
from strands import Agent
from strands.models import BedrockModel
from bedrock_agentcore.memory import MemoryClient
from .tools import market_rate_tool, case_law_search
from .prompts import (
    NEGOTIATION_SYSTEM_PROMPT,
    CLAUSE_ANALYSIS_PROMPT,
    NEGOTIATION_TACTICS_PROMPT
)

class NegotiationAgent:
    def __init__(self, memory_id: Optional[str] = None):
        """Initialize Negotiation Agent with memory"""
        self.model = BedrockModel("us.anthropic.claude-3-7-sonnet-20250219-v1:0")
        self.memory_client = MemoryClient() if memory_id else None
        self.memory_id = memory_id
        
        # Initialize agent with tools
        self.agent = Agent(
            model=self.model,
            system_prompt=NEGOTIATION_SYSTEM_PROMPT,
            tools=[market_rate_tool, case_law_search]
        )
        
        if memory_id:
            self._setup_memory_hooks()

    def _setup_memory_hooks(self):
        """Set up memory hooks for negotiation history"""
        # TODO: Implement memory hooks for tracking negotiation history
        pass

    def analyze_clause(self, clause: str, contract_type: str) -> Dict:
        """Analyze a contract clause for potential issues"""
        analysis = self.agent.generate(
            f"{CLAUSE_ANALYSIS_PROMPT}\n\nAnalyze this clause:\n{clause}",
            max_tokens=1000
        )
        return {
            "clause": clause,
            "type": contract_type,
            "issues": analysis,
            "risk_level": self._assess_risk_level(analysis)
        }

    def _assess_risk_level(self, analysis: str) -> str:
        """Assess risk level based on clause analysis"""
        # Count serious issues
        serious_issues = sum(
            1 for issue in ["violates", "illegal", "unfair", "dangerous"]
            if issue in analysis.lower()
        )
        
        if serious_issues >= 2:
            return "high"
        elif serious_issues == 1:
            return "medium"
        return "low"

    def negotiate(
        self,
        unfair_clause: str,
        clause_type: str,
        freelancer_info: Dict,
        session_id: Optional[str] = None
    ) -> Dict:
        """Generate counter-proposal and negotiation strategy"""
        
        # Get market data
        market_data = market_rate_tool(
            role=freelancer_info["role"],
            jurisdiction=freelancer_info["location"],
            experience_years=freelancer_info.get("experience_years", 5),
            specialization=freelancer_info.get("specialization")
        )
        
        # Get relevant case law
        cases = case_law_search(
            issue_type=clause_type,
            jurisdiction=freelancer_info["location"],
            contract_type="service_agreement"
        )
        
        # Analyze the clause
        analysis = self.analyze_clause(unfair_clause, clause_type)
        
        # Generate negotiation tactics
        tactics = self.agent.generate(
            f"{NEGOTIATION_TACTICS_PROMPT}\n\nGenerate tactics for:\n"
            f"Clause: {unfair_clause}\n"
            f"Analysis: {analysis}\n"
            f"Market Data: {market_data}\n"
            f"Case Law: {cases}",
            max_tokens=1000
        )
        
        # Generate counter-proposal
        counter_proposal = self.agent.generate(
            f"Based on the analysis, market data, and case law, generate a "
            f"professional counter-proposal for:\n{unfair_clause}",
            max_tokens=1000
        )
        
        # Generate email template
        email_template = self.agent.generate(
            f"Create a professional negotiation email using the counter-proposal:\n"
            f"{counter_proposal}\n\nInclude market data and case law to support the position.",
            max_tokens=1000
        )
        
        result = {
            "original_clause": unfair_clause,
            "analysis": analysis,
            "market_data": market_data,
            "similar_cases": cases,
            "counter_proposal": counter_proposal,
            "negotiation_tactics": tactics,
            "email_template": email_template,
            "risk_level": analysis["risk_level"]
        }
        
        # Save to memory if enabled
        if self.memory_client and self.memory_id:
            self.memory_client.add_memory(
                self.memory_id,
                session_id or "default",
                result
            )
        
        return result

if __name__ == "__main__":
    # Test the agent
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
    print("Counter-proposal:", result["counter_proposal"])
    print("Risk Level:", result["risk_level"])