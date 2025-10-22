"""
FastAPI Server for Explanation Agent
Provides REST API endpoint for contract clause explanation
"""

import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from agents.explanation.agent import ExplanationAgent

# Initialize FastAPI app
app = FastAPI(
    title="Contract Explanation Agent API",
    description="AI agent that translates legal jargon into plain English for freelancers",
    version="1.0.0"
)

# Enable CORS for integration with other services
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent (singleton)
agent = None

def get_agent():
    """Get or create the explanation agent"""
    global agent
    if agent is None:
        print("Initializing ExplanationAgent...")
        agent = ExplanationAgent()
        print("✅ Agent initialized!")
    return agent


# Request/Response models
class ExplanationRequest(BaseModel):
    clause_text: str = Field(..., description="The contract clause to explain", min_length=1)
    clause_type: Optional[str] = Field(None, description="Type of clause (e.g., payment, IP, termination)")
    contract_type: Optional[str] = Field(None, description="Type of contract (e.g., freelance, employment)")

class ExplanationResponse(BaseModel):
    plain_english: str
    potential_issues: list[str]
    key_points: list[str]
    risk_level: str
    context_questions: list[str]
    better_version: Optional[dict]
    disclaimer: str
    confidence: str
    training_cutoff_notice: str


# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Contract Explanation Agent",
        "version": "1.0.0",
        "endpoints": {
            "explain": "/explain (POST)",
            "health": "/health (GET)",
            "docs": "/docs (GET)"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Check if agent can be initialized
        get_agent()
        return {
            "status": "healthy",
            "agent_initialized": agent is not None,
            "aws_credentials": bool(os.getenv('AWS_ACCESS_KEY_ID')),
            "aws_region": os.getenv('AWS_DEFAULT_REGION', 'not set')
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/explain", response_model=ExplanationResponse)
async def explain_clause(request: ExplanationRequest):
    """
    Explain a contract clause in plain English
    
    **Parameters:**
    - **clause_text**: The contract clause to explain (required)
    - **clause_type**: Optional type hint (payment, IP, termination, etc.)
    - **contract_type**: Optional contract type (freelance, employment, etc.)
    
    **Returns:**
    - Plain English explanation
    - Potential issues and red flags
    - Key points to understand
    - Risk assessment
    - Suggested improvements
    """
    try:
        # Get agent
        explanation_agent = get_agent()
        
        # Call agent
        print(f"\n📝 Processing clause: {request.clause_text[:50]}...")
        result = explanation_agent.explain(
            clause_text=request.clause_text,
            clause_type=request.clause_type,
            contract_type=request.contract_type
        )
        
        print("✅ Explanation generated successfully")
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing clause: {str(e)}"
        )


@app.post("/batch-explain")
async def batch_explain(clauses: list[ExplanationRequest]):
    """
    Explain multiple clauses at once
    
    **Parameters:**
    - **clauses**: List of clause explanation requests
    
    **Returns:**
    - List of explanations in the same order
    """
    try:
        explanation_agent = get_agent()
        results = []
        
        for i, clause_req in enumerate(clauses, 1):
            print(f"\n[{i}/{len(clauses)}] Processing: {clause_req.clause_text[:50]}...")
            result = explanation_agent.explain(
                clause_text=clause_req.clause_text,
                clause_type=clause_req.clause_type,
                contract_type=clause_req.contract_type
            )
            results.append(result)
        
        print(f"\n✅ All {len(clauses)} clauses processed")
        return {"results": results, "total": len(clauses)}
        
    except Exception as e:
        print(f"❌ Batch error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error in batch processing: {str(e)}"
        )


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting Contract Explanation Agent API Server")
    print("=" * 60)
    print("\n📋 Configuration:")
    print(f"   AWS Region: {os.getenv('AWS_DEFAULT_REGION', 'not set')}")
    print(f"   AWS Credentials: {'✅ Set' if os.getenv('AWS_ACCESS_KEY_ID') else '❌ Not set'}")
    print("\n🌐 Server will start at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("❤️  Health Check: http://localhost:8000/health")
    print("\n" + "=" * 60 + "\n")
    
    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",  # Allow external connections
        port=8000,
        log_level="info"
    )
