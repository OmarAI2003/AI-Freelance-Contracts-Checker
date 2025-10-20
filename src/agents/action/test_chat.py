"""
Test chat with Bedrock Agent - Conversational Interface
"""

import boto3
import json
import uuid

# Load config
with open('../../config.json', 'r') as f:
    config = json.load(f)

agent_id = config['agent_id']
alias_id = config['alias_id']
region = config['region']

# Initialize Bedrock Agent Runtime
bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name=region)

# Generate unique session ID
session_id = str(uuid.uuid4())

print("\n" + "="*60)
print("💬 ContractGuard Action Agent - Chat Interface")
print("="*60)
print(f"\nAgent ID: {agent_id}")
print(f"Session ID: {session_id}")
print("\nType 'quit' to exit")
print("="*60 + "\n")

def chat(message):
    """Send message to Bedrock Agent and get response"""
    try:
        response = bedrock_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=alias_id,
            sessionId=session_id,
            inputText=message
        )
        
        # Collect response chunks
        full_response = ""
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    text = chunk['bytes'].decode('utf-8')
                    full_response += text
        
        return full_response
        
    except Exception as e:
        return f"Error: {str(e)}"

# Start conversation
print("🤖 Agent: Hello! I'm here to help with contract disputes. Can you tell me what happened?\n")

while True:
    user_input = input("You: ").strip()
    
    if user_input.lower() in ['quit', 'exit', 'bye']:
        print("\n👋 Goodbye!\n")
        break
    
    if not user_input:
        continue
    
    print("\n🤖 Agent: ", end="", flush=True)
    response = chat(user_input)
    print(response + "\n")
