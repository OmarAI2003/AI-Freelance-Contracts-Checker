"""
Contract Orchestrator - Coordinates all three agents with guardrail protection
"""

import json
import logging
from typing import Dict, Any, Optional
from agents.analysis.agent import AnalysisAgent
from agents.explanation.agent import ExplanationAgent
from agents.negotiation.agent import NegotiationAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContractOrchestrator:
    """
    Orchestrates the complete contract analysis workflow
    """
    
    def __init__(self, memory_id: Optional[str] = None):
        self.memory_id = memory_id
        
        # Initialize all agents
        self.analysis_agent = AnalysisAgent(memory_id)
        self.explanation_agent = ExplanationAgent(memory_id)
        self.negotiation_agent = NegotiationAgent(memory_id)
        
        logger.info("Contract orchestrator initialized with all agents")
    
    def process_contract(self, contract_text: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete contract processing workflow
        
        Args:
            contract_text: Raw contract text
            session_id: Optional session ID
            
        Returns:
            Complete analysis with explanation and negotiation strategies
        """
        logger.info(f"Starting contract processing, session: {session_id}")
        
        try:
            # Step 1: Analysis
            logger.info("Step 1: Running contract analysis...")
            analysis_result = self.analysis_agent.analyze(contract_text, session_id)
            
            if "error" in analysis_result:
                return {
                    "status": "error",
                    "stage": "analysis",
                    "error": analysis_result["error"],
                    "analysis": analysis_result,
                    "explanation": None,
                    "negotiation": None
                }
            
            # Step 2: Explanation
            logger.info("Step 2: Generating plain English explanation...")
            explanation_result = self.explanation_agent.explain(analysis_result, session_id)
            
            # Step 3: Negotiation (only if risks found)
            negotiation_result = None
            risks = analysis_result.get('risks', [])
            if risks and len(risks) > 0:
                logger.info("Step 3: Generating negotiation strategies...")
                negotiation_result = self.negotiation_agent.negotiate(analysis_result, session_id)
            else:
                logger.info("Step 3: Skipping negotiation - no risks found")
                negotiation_result = {
                    "negotiation_strategies": "No negotiation needed - contract appears fair",
                    "approach": "none_required",
                    "risk_count": 0,
                    "status": "success"
                }
            
            # Compile final result
            final_result = {
                "status": "success",
                "session_id": session_id,
                "analysis": analysis_result,
                "explanation": explanation_result,
                "negotiation": negotiation_result,
                "summary": {
                    "risk_level": analysis_result.get('risk_level', 'UNKNOWN'),
                    "contract_type": analysis_result.get('contract_type', 'unknown'),
                    "risks_found": len(risks),
                    "needs_negotiation": len(risks) > 0
                }
            }
            
            logger.info(f"Contract processing completed successfully. Risk level: {final_result['summary']['risk_level']}")
            return final_result
            
        except Exception as e:
            logger.error(f"Contract processing failed: {e}")
            return {
                "status": "error",
                "stage": "orchestration",
                "error": str(e),
                "analysis": None,
                "explanation": None,
                "negotiation": None
            }
    
    def analyze_only(self, contract_text: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Run analysis only"""
        return self.analysis_agent.analyze(contract_text, session_id)
    
    def explain_only(self, analysis_result: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]:
        """Run explanation only"""
        return self.explanation_agent.explain(analysis_result, session_id)
    
    def negotiate_only(self, analysis_result: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]:
        """Run negotiation only"""
        return self.negotiation_agent.negotiate(analysis_result, session_id)