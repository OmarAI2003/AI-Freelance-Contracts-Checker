"""
Tools for the Analysis Agent with Knowledge Base integration
"""

from strands import tool
import boto3
import json
from typing import Dict, List, Any

# Browser tool will be available in AgentCore runtime
try:
    from bedrock_agentcore.tools import browser_tool
except ImportError:
    browser_tool = None  # Fallback for local testing

# Initialize clients
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

@tool
def contract_parser(contract_text: str) -> dict:
    """
    Parse contract using Contract Types Knowledge Base
    """
    try:
        # Query Contract Types KB
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
        
        # Extract structured data using Claude
        prompt = f"""Based on this analysis, extract JSON:

Analysis: {analysis}

Contract: {contract_text[:1000]}

Return JSON:
{{
  "contract_type": "nda|msa|service_agreement|sow",
  "parties": {{"client": "name", "freelancer": "name"}},
  "jurisdiction": ["location"],
  "key_clauses": {{"payment_terms": "text", "ip_rights": "text"}}
}}"""

        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000,
                "temperature": 0.1
            })
        )
        
        result = json.loads(response['body'].read())
        text = result['content'][0]['text']
        
        # Extract JSON
        start = text.find('{')
        end = text.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
            
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
    Check clause compliance using Freelance Laws Knowledge Base
    """
    results = []
    
    for jurisdiction in jurisdictions:
        try:
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
            
            if any(word in analysis.lower() for word in ['violation', 'illegal', 'unenforceable', 'breach']):
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
    Enhanced jurisdiction checking with web validation for critical cases
    """
    # First check KB
    kb_results = jurisdiction_checker(clause_text, clause_type, [jurisdiction])
    kb_result = kb_results[0] if kb_results else {"compliant": None, "violations": []}
    
    # Use web search for HIGH/CRITICAL violations or unknown jurisdictions
    should_web_search = (
        any(v.get("severity") in ["HIGH", "CRITICAL"] for v in kb_result.get("violations", [])) or
        kb_result.get("compliant") is None or
        not kb_result.get("violations")
    )
    
    if should_web_search:
        try:
            # Search for current laws (only if browser_tool available)
            if browser_tool is None:
                raise Exception("Browser tool not available in local testing")
            
            search_query = f"{jurisdiction} freelance {clause_type} law 2024 enforceability"
            web_results = browser_tool.search(search_query, max_results=3)
            
            # Analyze web results
            web_analysis = analyze_web_results(web_results, clause_text, clause_type, jurisdiction)
            
            # Combine KB and web results
            return {
                "jurisdiction": jurisdiction,
                "kb_analysis": kb_result,
                "web_validation": web_analysis,
                "final_assessment": combine_assessments(kb_result, web_analysis)
            }
            
        except Exception as e:
            # Fallback to KB only
            return {
                "jurisdiction": jurisdiction,
                "kb_analysis": kb_result,
                "web_validation": {"error": str(e)},
                "final_assessment": kb_result
            }
    
    # KB result sufficient
    return {
        "jurisdiction": jurisdiction,
        "kb_analysis": kb_result,
        "web_validation": "not_needed",
        "final_assessment": kb_result
    }

def analyze_web_results(web_results: List[Dict], clause_text: str, clause_type: str, jurisdiction: str) -> Dict:
    """
    Analyze web search results for legal compliance
    """
    if not web_results:
        return {"found_updates": False, "sources": []}
    
    # Extract relevant content
    sources = []
    for result in web_results:
        if any(keyword in result.get("content", "").lower() for keyword in ["law", "legal", "court", "statute"]):
            sources.append({
                "url": result.get("url", ""),
                "title": result.get("title", ""),
                "snippet": result.get("content", "")[:200]
            })
    
    return {
        "found_updates": len(sources) > 0,
        "sources": sources,
        "search_performed": True
    }

def combine_assessments(kb_result: Dict, web_analysis: Dict) -> Dict:
    """
    Combine KB and web results for final assessment
    """
    # If web found contradictory info, flag for manual review
    if web_analysis.get("found_updates") and kb_result.get("violations"):
        return {
            "compliant": False,
            "confidence": "medium",
            "recommendation": "Manual legal review recommended - conflicting sources found",
            "violations": kb_result.get("violations", []) + [{
                "issue": "Potential law updates found online",
                "severity": "MEDIUM",
                "legal_basis": "Recent legal changes detected"
            }]
        }
    
    # Otherwise use KB result
    return kb_result