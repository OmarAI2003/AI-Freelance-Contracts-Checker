"""
Test the agent with actual PDF contract file
"""

import asyncio
import json
import os
from agent import AnalysisAgent

async def test_pdf_contract():
    """Test agent with real PDF contract from test_contracts directory"""
    
    contract_file = "../../../data/test_contracts/problematic-NDA-Contract.pdf"
    
    if not os.path.exists(contract_file):
        print(f"ERROR: Test contract not found: {contract_file}")
        return None
    
    agent = AnalysisAgent()
    
    try:
        result = await agent.analyze_file(contract_file, session_id="pdf_test")
        
        print(json.dumps(result, indent=2))
        
        return result
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return None

if __name__ == "__main__":
    asyncio.run(test_pdf_contract())