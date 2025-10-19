"""API endpoints for the Negotiation Agent"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from .agent import NegotiationAgent

app = FastAPI()
agent = NegotiationAgent()

class AnalyzeRequest(BaseModel):
    contract_text: str

class ExplainRequest(BaseModel):
    terms: str

class NegotiateRequest(BaseModel):
    current_terms: str
    desired_changes: List[str]
    context: Optional[Dict[str, str]] = None

class LegalAdviceRequest(BaseModel):
    contract_text: str
    question: str

@app.post("/analyze")
async def analyze_contract(request: AnalyzeRequest):
    try:
        result = agent.analyze_contract(request.contract_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain")
async def explain_terms(request: ExplainRequest):
    try:
        result = agent.explain_terms(request.terms)
        return {"explanation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/negotiate")
async def negotiate_terms(request: NegotiateRequest):
    try:
        result = agent.negotiate_terms(
            request.current_terms,
            request.desired_changes,
            request.context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/legal-advice")
async def get_legal_advice(request: LegalAdviceRequest):
    try:
        result = agent.get_legal_advice(
            request.contract_text,
            request.question
        )
        return {"advice": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))