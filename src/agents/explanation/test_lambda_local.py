"""
Test Lambda Handler Locally
Simulates API Gateway event and tests the lambda_handler function
"""

import json
import sys
import os

# Add project src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', '..', '..')
sys.path.insert(0, src_dir)

# Now import directly from the agent module
from agents.explanation.agent import ExplanationAgent

def test_local():
    """Test the Lambda handler with a sample API Gateway event"""
    
    print("=" * 60)
    print("Testing Lambda Handler Locally")
    print("=" * 60)
    
    # Test clause
    clause_text = "Payment is due within 90 days of invoice date."
    clause_type = "payment"
    contract_type = "freelance"
    
    print("\n📤 Test Input:")
    print(f"   Clause: {clause_text}")
    print(f"   Type: {clause_type}")
    
    print("\n⏳ Initializing agent and calling explanation...")
    print("   (this may take 15-30 seconds for Claude response)\n")
    
    try:
        # Initialize agent
        print("Initializing ExplanationAgent...")
        agent = ExplanationAgent()
        print("✅ Agent initialized!\n")
        
        # Call the agent
        print("Calling agent.explain()...")
        result = agent.explain(
            clause_text=clause_text,
            clause_type=clause_type,
            contract_type=contract_type
        )
        print("✅ Got response from agent!\n")
        
        print("\n" + "=" * 60)
        print("✅ Agent Response:")
        print("=" * 60)
        
        explanation = result
        
        print(f"\n🔍 Plain English:")
        print(f"   {explanation.get('plain_english', 'N/A')}")
        
        print(f"\n⚠️  Potential Issues:")
        for i, issue in enumerate(explanation.get('potential_issues', []), 1):
            print(f"   {i}. {issue}")
        
        print(f"\n💡 Key Points:")
        for i, point in enumerate(explanation.get('key_points', []), 1):
            print(f"   {i}. {point}")
        
        print(f"\n🚨 Risk Level: {explanation.get('risk_level', 'N/A')}")
        print(f"📊 Confidence: {explanation.get('confidence', 'N/A')}")
        
        if explanation.get('better_version'):
            better = explanation['better_version']
            print(f"\n✨ Suggested Improvement:")
            print(f"   {better.get('improved_text', 'N/A')}")
            print(f"   Why: {better.get('why_better', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("✅ TEST SUCCESSFUL!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED!")
        print("=" * 60)
        print(f"\nError: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🚀 Starting local Lambda test...\n")
    success = test_local()
    sys.exit(0 if success else 1)
