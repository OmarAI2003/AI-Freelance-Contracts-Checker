"""
Guardrail Integration Module for AI-Freelance-Contracts-Checker

This module provides guardrail integration for all three agents with
runtime validation and monitoring capabilities.
"""

import boto3
import json
import logging
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class GuardrailAction(Enum):
    BLOCK = "BLOCK"
    ANONYMIZE = "ANONYMIZE" 
    FLAG = "FLAG"
    ALLOW = "ALLOW"

@dataclass
class GuardrailResult:
    action: GuardrailAction
    message: str
    filtered_content: Optional[str] = None
    violations: List[Dict[str, Any]] = None
    confidence: float = 1.0

class ContractGuardGuardrail:
    """
    Comprehensive guardrail integration for contract analysis agents
    """
    
    def __init__(self, guardrail_id: str, version: str, region: str = 'us-east-1'):
        self.guardrail_id = guardrail_id
        self.version = version
        self.region = region
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)
        
        # Load agent-specific rules
        self.agent_rules = self._load_agent_rules()
        
    def _load_agent_rules(self) -> Dict[str, Any]:
        """Load agent-specific guardrail rules"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'guardrail_config.json')
            with open(config_path) as f:
                config = json.load(f)
            return config['guardrail']['agent_specific_rules']
        except Exception as e:
            logger.warning(f"Could not load agent rules: {e}")
            return {}
    
    def validate_input(self, content: str, agent_type: str) -> GuardrailResult:
        """
        Validate input content against guardrails
        
        Args:
            content: Input text to validate
            agent_type: Type of agent (analysis, explanation, negotiation)
            
        Returns:
            GuardrailResult with validation outcome
        """
        try:
            # Apply Bedrock guardrail
            response = self.bedrock_runtime.apply_guardrail(
                guardrailIdentifier=self.guardrail_id,
                guardrailVersion=self.version,
                source='INPUT',
                content=[{
                    'text': {
                        'text': content
                    }
                }]
            )
            
            # Check for violations
            if response['action'] == 'GUARDRAIL_INTERVENED':
                violations = []
                
                # Extract violation details
                for output in response.get('outputs', []):
                    if 'text' in output:
                        violations.append({
                            'type': 'content_filter',
                            'details': output['text']
                        })
                
                return GuardrailResult(
                    action=GuardrailAction.BLOCK,
                    message="Content blocked by guardrail policy",
                    violations=violations
                )
            
            # Apply agent-specific validation
            agent_result = self._validate_agent_specific(content, agent_type)
            if agent_result.action != GuardrailAction.ALLOW:
                return agent_result
            
            return GuardrailResult(
                action=GuardrailAction.ALLOW,
                message="Content approved",
                filtered_content=content
            )
            
        except Exception as e:
            logger.error(f"Guardrail validation failed: {e}")
            return GuardrailResult(
                action=GuardrailAction.FLAG,
                message=f"Validation error: {str(e)}"
            )
    
    def validate_output(self, content: str, agent_type: str) -> GuardrailResult:
        """
        Validate output content against guardrails
        
        Args:
            content: Output text to validate
            agent_type: Type of agent (analysis, explanation, negotiation)
            
        Returns:
            GuardrailResult with validation outcome
        """
        try:
            # Apply Bedrock guardrail for output
            response = self.bedrock_runtime.apply_guardrail(
                guardrailIdentifier=self.guardrail_id,
                guardrailVersion=self.version,
                source='OUTPUT',
                content=[{
                    'text': {
                        'text': content
                    }
                }]
            )
            
            # Process response
            if response['action'] == 'GUARDRAIL_INTERVENED':
                # Extract filtered content if available
                filtered_content = None
                violations = []
                
                for output in response.get('outputs', []):
                    if 'text' in output:
                        filtered_content = output['text']
                    
                return GuardrailResult(
                    action=GuardrailAction.ANONYMIZE,
                    message="Content filtered by guardrail",
                    filtered_content=filtered_content,
                    violations=violations
                )
            
            # Apply output-specific validation
            output_result = self._validate_output_specific(content, agent_type)
            return output_result
            
        except Exception as e:
            logger.error(f"Output validation failed: {e}")
            return GuardrailResult(
                action=GuardrailAction.FLAG,
                message=f"Output validation error: {str(e)}"
            )
    
    def _validate_agent_specific(self, content: str, agent_type: str) -> GuardrailResult:
        """Apply agent-specific validation rules"""
        
        rules = self.agent_rules.get(f"{agent_type}_agent", {})
        
        # Analysis agent specific checks
        if agent_type == "analysis":
            if self._contains_unauthorized_legal_advice(content):
                return GuardrailResult(
                    action=GuardrailAction.BLOCK,
                    message="Content contains unauthorized legal advice"
                )
        
        # Explanation agent specific checks  
        elif agent_type == "explanation":
            if rules.get("plain_language_requirement") and self._is_too_technical(content):
                return GuardrailResult(
                    action=GuardrailAction.FLAG,
                    message="Content may be too technical for target reading level"
                )
        
        # Negotiation agent specific checks
        elif agent_type == "negotiation":
            if rules.get("no_aggressive_tactics") and self._contains_aggressive_language(content):
                return GuardrailResult(
                    action=GuardrailAction.BLOCK,
                    message="Content contains aggressive negotiation tactics"
                )
        
        return GuardrailResult(
            action=GuardrailAction.ALLOW,
            message="Agent-specific validation passed"
        )
    
    def _validate_output_specific(self, content: str, agent_type: str) -> GuardrailResult:
        """Validate output-specific requirements"""
        
        # Check for required legal disclaimers
        if self._needs_legal_disclaimer(content) and not self._has_legal_disclaimer(content):
            disclaimer = ("This analysis is for informational purposes only and does not "
                         "constitute legal advice. Consult with a qualified attorney for "
                         "specific legal guidance.")
            
            filtered_content = f"{content}\n\n**Disclaimer:** {disclaimer}"
            
            return GuardrailResult(
                action=GuardrailAction.ANONYMIZE,
                message="Added required legal disclaimer",
                filtered_content=filtered_content
            )
        
        # Check for evidence citations (analysis agent)
        if agent_type == "analysis" and not self._has_sufficient_citations(content):
            return GuardrailResult(
                action=GuardrailAction.FLAG,
                message="Analysis lacks sufficient evidence citations"
            )
        
        return GuardrailResult(
            action=GuardrailAction.ALLOW,
            message="Output validation passed",
            filtered_content=content
        )
    
    def _contains_unauthorized_legal_advice(self, content: str) -> bool:
        """Check if content contains unauthorized legal advice"""
        prohibited_phrases = [
            "you should sue",
            "this will definitely win in court",
            "I recommend filing a lawsuit",
            "you have a strong legal case",
            "this violates the law"
        ]
        
        content_lower = content.lower()
        return any(phrase in content_lower for phrase in prohibited_phrases)
    
    def _is_too_technical(self, content: str) -> bool:
        """Check if content is too technical for 8th grade reading level"""
        # Simple heuristic - count complex legal terms
        complex_terms = [
            "whereas", "heretofore", "aforementioned", "notwithstanding",
            "indemnification", "subrogation", "tortious", "ipso facto"
        ]
        
        content_lower = content.lower()
        complex_count = sum(1 for term in complex_terms if term in content_lower)
        
        # Flag if more than 3 complex terms per 100 words
        word_count = len(content.split())
        return complex_count > (word_count / 100) * 3
    
    def _contains_aggressive_language(self, content: str) -> bool:
        """Check for aggressive negotiation language"""
        aggressive_phrases = [
            "demand", "insist", "refuse to accept", "take it or leave it",
            "non-negotiable", "final offer", "you must"
        ]
        
        content_lower = content.lower()
        return any(phrase in content_lower for phrase in aggressive_phrases)
    
    def _needs_legal_disclaimer(self, content: str) -> bool:
        """Check if content needs a legal disclaimer"""
        legal_keywords = [
            "legal", "law", "court", "attorney", "lawsuit", 
            "liability", "rights", "obligations", "breach", "violate"
        ]
        
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in legal_keywords)
    
    def _has_legal_disclaimer(self, content: str) -> bool:
        """Check if content already has a legal disclaimer"""
        disclaimer_indicators = [
            "not constitute legal advice",
            "informational purposes only",
            "consult with a qualified attorney",
            "disclaimer"
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in disclaimer_indicators)
    
    def _has_sufficient_citations(self, content: str) -> bool:
        """Check if analysis has sufficient evidence citations"""
        citation_indicators = [
            "source:", "according to", "as stated in", "reference:",
            "url:", "legal precedent", "case law"
        ]
        
        content_lower = content.lower()
        citation_count = sum(1 for indicator in citation_indicators if indicator in content_lower)
        
        # Require at least 1 citation per 200 words
        word_count = len(content.split())
        required_citations = max(1, word_count // 200)
        
        return citation_count >= required_citations

# Decorator for easy integration
def with_guardrail(guardrail_id: str, version: str, agent_type: str):
    """
    Decorator to add guardrail validation to agent methods
    
    Args:
        guardrail_id: Bedrock guardrail ID
        version: Guardrail version
        agent_type: Type of agent (analysis, explanation, negotiation)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Initialize guardrail
            guardrail = ContractGuardGuardrail(guardrail_id, version)
            
            # Validate input if present
            if args and isinstance(args[1], str):  # Assuming first arg after self is input text
                input_result = guardrail.validate_input(args[1], agent_type)
                if input_result.action == GuardrailAction.BLOCK:
                    return {"error": input_result.message, "violations": input_result.violations}
            
            # Execute original function
            result = func(*args, **kwargs)
            
            # Validate output if it's a string response
            if isinstance(result, str):
                output_result = guardrail.validate_output(result, agent_type)
                if output_result.action in [GuardrailAction.ANONYMIZE, GuardrailAction.ALLOW]:
                    return output_result.filtered_content or result
                elif output_result.action == GuardrailAction.BLOCK:
                    return {"error": output_result.message}
            
            return result
        return wrapper
    return decorator