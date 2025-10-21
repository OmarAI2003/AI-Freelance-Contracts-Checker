"""
Tools for the Analysis Agent with Knowledge Base integration
"""

from strands import tool
import boto3
import json
from typing import Dict, List, Any

# AgentCore browser tool
try:
    from bedrock_agentcore.tools import browser
except ImportError:
    browser = None  # Fallback for local testing

# Initialize Bedrock clients for KB access
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

@tool
def contract_parser(contract_text: str) -> dict:
    """
    Parse contract using Contract Types Knowledge Base (9LRYYFY2BR)
    """
    try:
        # Query Contract Types KB directly
        kb_response = bedrock_agent_runtime.retrieve_and_generate(
            input={'text': f"Analyze contract type and extract key clauses: {contract_text[:1500]}"},
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': '9LRYYFY2BR',
                    'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0'
                }
            }
        )
        
        analysis = kb_response['output']['text']
        
        # Extract contract type
        contract_type = "unknown"
        if "nda" in analysis.lower() or "non-disclosure" in analysis.lower():
            contract_type = "nda"
        elif "msa" in analysis.lower() or "master service" in analysis.lower():
            contract_type = "msa"
        elif "sow" in analysis.lower() or "statement of work" in analysis.lower():
            contract_type = "sow"
        elif "service agreement" in analysis.lower():
            contract_type = "service_agreement"
        
        return {
            "contract_type": contract_type,
            "parties": {"client": "Client", "freelancer": "Freelancer"},
            "jurisdiction": ["usa"],
            "key_clauses": {"analysis": analysis[:200]}
        }
        
    except Exception as e:
        pass
    
    return {
        "contract_type": "unknown",
        "parties": {"client": None, "freelancer": None},
        "jurisdiction": [],
        "key_clauses": {}
    }

@tool
def jurisdiction_checker(clause_text: str, clause_type: str, jurisdictions: List[str]) -> List[Dict]:
    """
    Check clause compliance using Freelance Laws Knowledge Base (XNHMT6VAJC)
    """
    results = []
    
    for jurisdiction in jurisdictions:
        try:
            # Query Freelance Laws KB directly
            query = f"Check {clause_type} clause compliance with {jurisdiction} freelance laws: {clause_text}"
            
            kb_response = bedrock_agent_runtime.retrieve_and_generate(
                input={'text': query},
                retrieveAndGenerateConfiguration={
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'knowledgeBaseId': 'XNHMT6VAJC',
                        'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0'
                    }
                }
            )
            
            analysis = kb_response['output']['text']
            violations = []
            
            if any(word in analysis.lower() for word in ['violation', 'illegal', 'unenforceable', 'breach', 'unfair']):
                violations.append({
                    "issue": f"Potential {clause_type} compliance issue",
                    "legal_basis": f"{jurisdiction} freelance law",
                    "severity": "MEDIUM"
                })
            
            results.append({
                "jurisdiction": jurisdiction,
                "compliant": len(violations) == 0,
                "violations": violations
            })
            
        except Exception as e:
            results.append({
                "jurisdiction": jurisdiction,
                "compliant": None,
                "error": str(e),
                "violations": []
            })
    
    return results

@tool
def enhanced_jurisdiction_checker(clause_text: str, clause_type: str, jurisdiction: str) -> Dict:
    """
    Enhanced jurisdiction checking with web validation using AgentCore Browser Tool
    """
    # First check KB
    kb_result = jurisdiction_checker(clause_text, clause_type, [jurisdiction])[0]
    
    # Use browser tool for web validation if violations found or compliance unclear
    web_validation = {}
    if browser and (not kb_result.get("compliant") or kb_result.get("violations")):
        try:
            # Search for current legal information
            search_query = f"{jurisdiction} freelance {clause_type} law 2024 enforceability legal requirements"
            web_results = browser.search(search_query)
            
            if web_results:
                web_validation = {
                    "search_performed": True,
                    "sources_found": len(web_results),
                    "top_result": web_results[0].get('title', '') if web_results else ""
                }
            
        except Exception as e:
            web_validation = {"error": str(e)}
    
    return {
        "jurisdiction": jurisdiction,
        "kb_analysis": kb_result,
        "web_validation": web_validation,
        "final_assessment": kb_result
    }

