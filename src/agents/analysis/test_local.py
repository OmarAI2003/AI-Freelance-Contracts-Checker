#!/usr/bin/env python3
"""
Test full agent capabilities locally before deployment
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from handler import agentcore_handler
import json

def test_scam_contract():
    """Test scam detection with full capabilities"""
    
    scam_contract = """
    FREELANCE AGREEMENT
    
    1. Freelancer must pay $500 upfront for training materials
    2. All payments via wire transfer to overseas account only  
    3. Client owns ALL intellectual property including past work
    4. Freelancer liable for damages up to $50,000
    5. Must work exclusively, no other projects allowed
    """
    
    print("Testing SCAM detection with full capabilities...")
    
    event = {
        "contract_text": scam_contract,
        "session_id": "local-test"
    }
    
    try:
        result = agentcore_handler(event)
        
        print(f"✅ Risk Level: {result.get('risk_level')}")
        print(f"📋 Contract Type: {result.get('contract_type')}")
        print(f"🚨 Scam Indicators: {result.get('scam_indicators', [])}")
        print(f"⚠️  Risks Found: {len(result.get('risks', []))}")
        print(f"🌍 Jurisdictions: {result.get('jurisdictions_checked', [])}")
        
        if result.get('error'):
            print(f"❌ Error: {result['error']}")
            return False
        
        return result.get('risk_level') in ['SCAM', 'CRITICAL']
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def test_fair_contract():
    """Test with fair contract"""
    
    fair_contract = """
    FREELANCE WEB DESIGN AGREEMENT
    
    1. Payment: $5000 upon project completion via bank transfer
    2. IP created for this project belongs to client
    3. Freelancer retains rights to pre-existing tools and methods
    4. Either party may terminate with 30 days written notice
    5. Freelancer may accept other non-competing projects
    """
    
    print("\nTesting fair contract...")
    
    event = {
        "contract_text": fair_contract,
        "session_id": "fair-test"
    }
    
    try:
        result = agentcore_handler(event)
        
        print(f"✅ Risk Level: {result.get('risk_level')}")
        print(f"⚠️  Risks: {len(result.get('risks', []))}")
        
        return result.get('risk_level') in ['LOW', 'MEDIUM']
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Full Agent Capabilities Locally")
    print("=" * 60)
    
    # Test 1: Scam detection
    scam_test = test_scam_contract()
    
    # Test 2: Fair contract
    fair_test = test_fair_contract()
    
    print("\n📊 LOCAL TEST RESULTS:")
    print("=" * 30)
    print(f"Scam Detection: {'✅ PASS' if scam_test else '❌ FAIL'}")
    print(f"Fair Contract:  {'✅ PASS' if fair_test else '❌ FAIL'}")
    
    if scam_test and fair_test:
        print("\nALL TESTS PASSED - Ready for deployment!")
    else:
        print("\nSome tests failed - Fix issues before deployment")