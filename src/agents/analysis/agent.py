"""
Analysis Agent for detecting unfair contract clauses and assigning risk levels

This module contains the main AnalysisAgent class that orchestrates contract analysis
using the contract parser and jurisdiction checker tools.
"""

from strands import Agent
from strands.models import BedrockModel
from tools import contract_parser, jurisdiction_checker, enhanced_jurisdiction_checker
from prompts import ANALYSIS_SYSTEM_PROMPT
from document_parser import DocumentParser
# Guardrail is now handled by AgentCore configuration
import json
import os
import logging
import asyncio
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AnalysisAgent:
    """
    Main Analysis Agent for contract risk assessment
    
    Capabilities:
    - Parse contracts to extract structured data
    - Check clauses against jurisdiction laws
    - Detect scam indicators
    - Assign risk levels (LOW/MEDIUM/HIGH/CRITICAL/SCAM)
    - Provide evidence-based recommendations
    """
    
    def __init__(self, memory_id: Optional[str] = None):
        """
        Initialize Analysis Agent with optional memory
        
        Args:
            memory_id: AgentCore Memory ID for conversation persistence
        """
        # Load configuration
        # Try multiple config paths for AgentCore
        config_paths = [
            os.path.join(os.path.dirname(__file__), '../../../src/infrastructure/config.json'),
            os.path.join(os.path.dirname(__file__), 'config.json'),
            '/app/config.json'
        ]
        config_path = None
        for path in config_paths:
            if os.path.exists(path):
                config_path = path
                break
        if config_path:
            try:
                with open(config_path) as f:
                    config = json.load(f)
            except FileNotFoundError:
                logger.warning("Config file not found, using defaults")
                config = {"memory_id": "YOUR_MEMORY_ID"}
        else:
            logger.warning("No config file found, using defaults")
            config = {"memory_id": "YOUR_MEMORY_ID"}
        
        # Use provided memory_id or fall back to config
        self.memory_id = memory_id or config.get('memory_id')
        
        # Guardrail is handled by AgentCore
        
        # Initialize Bedrock model (Claude 3 Haiku)
        self.model = BedrockModel(
            model_id='anthropic.claude-3-haiku-20240307-v1:0',
            region_name='us-east-1'
        )
        
        # Initialize memory client if memory_id provided
        self.memory_client = None
        if self.memory_id and self.memory_id != "YOUR_MEMORY_ID":
            try:
                from bedrock_agentcore.memory import MemoryClient
                self.memory_client = MemoryClient(
                    region_name=os.environ.get('AWS_REGION', 'us-east-1')
                )
                logger.info("Memory client initialized successfully")
            except ImportError:
                logger.info("Memory client not available (bedrock_agentcore not installed)")
            except Exception as e:
                logger.warning(f"Could not initialize memory client: {e}")
        
        # Create the Strands agent
        self.agent = None  # Will be created per session
    
    def _create_agent(self, session_id: str = "default") -> Agent:
        """
        Create a new agent instance for a session
        
        Args:
            session_id: Session identifier for memory isolation
            
        Returns:
            Configured Strands Agent
        """
        agent = Agent(
            name="ContractGuard Analysis Agent",
            model=self.model,
            system_prompt=ANALYSIS_SYSTEM_PROMPT,
            tools=[contract_parser, jurisdiction_checker, enhanced_jurisdiction_checker]
        )
        
        return agent
    
    async def analyze_file(self, file_path: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a contract file (PDF/DOCX) and return risk assessment
        
        Args:
            file_path: Path to contract file (PDF or DOCX)
            session_id: Optional session ID for memory isolation
            
        Returns:
            Structured risk assessment with:
            - risk_level: Overall risk (LOW/MEDIUM/HIGH/CRITICAL/SCAM)
            - contract_type: Type of contract
            - risks: List of identified risks with evidence
            - scam_indicators: List of scam red flags
            - jurisdictions_checked: Jurisdictions analyzed
        """
        # Validate file
        if not DocumentParser.validate_file(file_path):
            logger.error(f"Invalid file: {file_path}")
            return self._error_response(f"File not found or unsupported format: {file_path}")
        
        # Extract text from document
        logger.info(f"Extracting text from: {file_path}")
        contract_text = DocumentParser.extract_text_from_file(file_path)
        
        if not contract_text:
            logger.error(f"Could not extract text from: {file_path}")
            return self._error_response(f"Failed to extract text from file: {file_path}")
        
        if len(contract_text.strip()) < 50:
            logger.warning("Extracted text is very short")
            return self._error_response("Contract text too short (minimum 50 characters)")
        
        if len(contract_text) > 100000:  # 100KB limit
            logger.warning(f"Contract text truncated from {len(contract_text)} to 100000 characters")
            contract_text = contract_text[:100000]
        
        # Continue with text analysis
        return await self._analyze_text(contract_text, session_id, file_path)
    
    async def _analyze_text(self, contract_text: str, session_id: Optional[str] = None, source_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Internal method to analyze contract text
        
        Args:
            contract_text: Extracted contract text
            session_id: Optional session ID for memory isolation
            source_file: Original file path for logging
            
        Returns:
            Structured risk assessment
        """
        
        # Use default session if not provided
        if not session_id:
            session_id = "default"
        
        logger.info(f"Starting analysis for session {session_id}, text length: {len(contract_text)}, source: {source_file or 'direct text'}")
        
        # Input validation handled by AgentCore guardrail
        
        # Construct analysis request
        analysis_request = f"""Analyze this freelance contract for risks and unfair terms:

{contract_text}

Please:
1. Parse the contract to extract all key information
2. Check each clause against applicable laws
3. Identify any scam indicators
4. Assign an overall risk level
5. Provide detailed evidence and recommendations

Return your analysis in this JSON format:
{{
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL|SCAM",
  "contract_type": "service_agreement|nda|work_for_hire|msa|sow",
  "risks": [
    {{
      "clause": "clause name",
      "issue": "description of problem",
      "severity": "LOW|MEDIUM|HIGH|CRITICAL",
      "evidence": {{
        "source": "legal citation",
        "url": "source URL",
        "quote": "relevant legal text"
      }}
    }}
  ],
  "scam_indicators": ["list of scam red flags"],
  "jurisdictions_checked": ["usa-california", "uk", etc.],
  "recommendations": "suggested actions"
}}"""
        
        # Create agent for this session
        agent = self._create_agent(session_id)
        
        # Run the agent
        try:
            logger.info("Invoking analysis agent")
            response = await agent.invoke_async(analysis_request)
            
            # Parse the response
            response_text = str(response) if hasattr(response, '__str__') else response
            result = self._parse_agent_response(response_text)
            
            # Output validation handled by AgentCore guardrail
            
            # Add source file info to result
            if source_file:
                result['source_file'] = source_file
            
            logger.info(f"Analysis completed successfully, risk level: {result.get('risk_level')}")
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            return self._error_response(f"Analysis failed: {str(e)}")
    
    def _parse_agent_response(self, response: str) -> Dict[str, Any]:
        """
        Parse agent response into structured format
        
        Args:
            response: Raw agent response text
            
        Returns:
            Structured analysis result
        """
        # Try to extract JSON from response
        try:
            # Look for JSON in code blocks
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0].strip()
            else:
                # Try to find JSON object in response
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = response[start:end]
                else:
                    json_str = response
            
            result = json.loads(json_str)
            
            # Validate required fields
            if 'risk_level' not in result:
                result['risk_level'] = self._infer_risk_level(result)
            
            if 'risks' not in result:
                result['risks'] = []
            
            if 'scam_indicators' not in result:
                result['scam_indicators'] = []
            
            if 'jurisdictions_checked' not in result:
                result['jurisdictions_checked'] = []
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            # Fallback: create structured response from text
            return {
                "risk_level": "MEDIUM",
                "contract_type": "unknown",
                "risks": [{
                    "clause": "Full Contract",
                    "issue": "Manual review required - JSON parsing failed",
                    "severity": "MEDIUM",
                    "evidence": {
                        "source": "Agent Analysis",
                        "url": "",
                        "quote": response[:500]
                    }
                }],
                "scam_indicators": [],
                "jurisdictions_checked": [],
                "raw_response": response
            }
    
    def _infer_risk_level(self, analysis: Dict[str, Any]) -> str:
        """
        Infer risk level from analysis results
        
        Args:
            analysis: Partial analysis result
            
        Returns:
            Risk level string
        """
        # Check for scam indicators
        if analysis.get('scam_indicators') and len(analysis['scam_indicators']) > 0:
            return "SCAM"
        
        # Count high severity risks
        risks = analysis.get('risks', [])
        high_severity_count = sum(
            1 for risk in risks
            if risk.get('severity') in ['HIGH', 'CRITICAL']
        )
        
        if high_severity_count >= 3:
            return "CRITICAL"
        elif high_severity_count >= 1:
            return "HIGH"
        elif len(risks) >= 3:
            return "MEDIUM"
        elif len(risks) > 0:
            return "LOW"
        else:
            return "LOW"
    
    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Create standardized error response
        """
        return {
            "error": error_message,
            "risk_level": "UNKNOWN",
            "contract_type": None,
            "risks": [],
            "scam_indicators": [],
            "jurisdictions_checked": []
        }