"""
Single message test to verify agent is working
"""
import boto3
import json
import uuid

def test_single_message():
    # Load config
    with open('d:/aws_hackathon/src/config.json', 'r') as f:
        config = json.load(f)
    
    # Create client
    client = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
    
    # Create session
    session_id = str(uuid.uuid4())
    
    # Send single message
    message = "My client won't pay me $5000 for web development work that was due 60 days ago. I'm in the USA. What should I do?"
    
    print("=" * 60)
    print("🧪 Single Message Test")
    print("=" * 60)
    print(f"\n📤 You: {message}")
    print("   Sending to agent...\n")
    
    try:
        response = client.invoke_agent(
            agentId=config['agent_id'],
            agentAliasId=config['alias_id'],
            sessionId=session_id,
            inputText=message
        )
        
        # Collect response
        full_response = ""
        for event in response['completion']:
            if 'chunk' in event:
                chunk_data = event['chunk']
                if 'bytes' in chunk_data:
                    full_response += chunk_data['bytes'].decode('utf-8')
        
        print("🤖 Agent Response:")
        print(f"   {full_response}")
        print("\n" + "=" * 60)
        print("✅ Test Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n" + "=" * 60)

if __name__ == "__main__":
    test_single_message()
