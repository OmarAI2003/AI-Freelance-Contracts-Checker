"""
Local test script for Action Agent with AgentCore + Strands SDK
Run this before deploying to test locally
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the agent
from action_agent_agentcore import action_agent

def test_conversation():
    """Test a conversation flow with the agent."""
    print("=" * 60)
    print("🧪 Testing Action Agent (AgentCore + Strands SDK)")
    print("=" * 60)
    print()
    
    # Test messages
    messages = [
        "Hi, I need help with a problem",
        "My client won't pay me for the work I completed",
        "It's $5000 for web development work",
        "It was due 60 days ago, Net 30 terms in the contract",
        "I'm in the USA"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"📤 You ({i}/{len(messages)}): {message}")
        print("   Sending to agent...\n")
        
        try:
            response = action_agent(message)
            print(f"🤖 Agent Response:")
            print(f"   {response.message}")
            print("-" * 60)
            print()
        except Exception as e:
            print(f"❌ Error: {e}")
            print("-" * 60)
            print()
    
    print("=" * 60)
    print("✅ Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_conversation()
