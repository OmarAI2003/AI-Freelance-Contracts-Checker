"""Main Negotiation Agent implementation"""

from typing import Dict, Optional, List
import os
import json
from dotenv import load_dotenv
from langchain_community.llms.bedrock import Bedrock
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .prompts import (
    NEGOTIATION_SYSTEM_PROMPT,
    CLAUSE_ANALYSIS_PROMPT,
    NEGOTIATION_TACTICS_PROMPT
)

class NegotiationAgent:
    def __init__(self):
        """Initialize Negotiation Agent"""
        load_dotenv()
        
        # Initialize Bedrock client with bearer token
        import boto3
        session = boto3.Session(region_name=os.getenv("AWS_REGION"))
        
        bedrock_runtime = session.client(
            service_name='bedrock-runtime',
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id="",
            aws_secret_access_key="",
            aws_session_token=os.getenv("AWS_BEARER_TOKEN_BEDROCK")
        )
        
        # Use invoke directly with raw request format for Claude 3
        self.bedrock_client = bedrock_runtime
        self.model_kwargs = {
            "anthropic_version": "bedrock-2023-05-31",
            "temperature": 0.7,
            "max_tokens": 2048
        }
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        
        # Initialize output parser
        self.output_parser = StrOutputParser()
    
    def analyze_contract(self, contract_text: str) -> Dict[str, str]:
        """Analyze a contract and identify key terms and potential issues"""
        
        prompt = CLAUSE_ANALYSIS_PROMPT + "\n\nContract Text: " + contract_text + "\n\nAnalysis:"
        
        request_body = {
            **self.model_kwargs,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
            
        response = self.bedrock_client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request_body),
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get('body').read().decode())
        
        return {
            "analysis": response_body.get("content")[0].get("text")
        }
    
    def explain_terms(self, terms: str) -> str:
        """Explain contract terms in simple language"""
        
        prompt = """Please explain these contract terms in simple, clear language that a freelancer can understand:

Terms: """ + terms + """

Explanation:"""

        request_body = {
            **self.model_kwargs,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
            
        response = self.bedrock_client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request_body),
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get('body').read().decode())
        
        return response_body.get("content")[0].get("text")
    
    def negotiate_terms(self, 
                       current_terms: str,
                       desired_changes: List[str],
                       context: Optional[Dict] = None) -> Dict[str, str]:
        """Generate negotiation strategy and response"""
        
        # Convert list to bullet points
        changes_text = "\n".join(f"- {change}" for change in desired_changes)
        context_text = "\n".join(f"{k}: {v}" for k,v in (context or {}).items())
        
        prompt = f"""{NEGOTIATION_SYSTEM_PROMPT}

Current Terms: {current_terms}

Desired Changes:
{changes_text}

Additional Context: {context_text}

Please provide:
1. Analysis of the situation
2. Negotiation strategy
3. Counter-proposal draft
4. Email template"""

        request_body = {
            **self.model_kwargs,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
            
        response = self.bedrock_client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request_body),
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get('body').read().decode())
        
        return {
            "strategy": response_body.get("content")[0].get("text")
        }
    
    def get_legal_advice(self, contract_text: str, question: str) -> str:
        """Get legal analysis and advice about specific contract terms"""
        
        prompt = """Please provide legal analysis and advice regarding this contract question.
Note: This is general guidance, not legal advice. Consult a lawyer for specific legal advice.

Contract Text:
""" + contract_text + """

Question:
""" + question + """

Analysis:"""

        request_body = {
            **self.model_kwargs,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
            
        response = self.bedrock_client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request_body),
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get('body').read().decode())
        
        return response_body.get("content")[0].get("text")