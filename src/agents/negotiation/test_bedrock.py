"""Test Bedrock connection and model invocation"""
import os
import json
import boto3
from dotenv import load_dotenv

def test_bedrock():
    """Test Bedrock connection"""
    load_dotenv()
    
    print("Testing AWS Bedrock Connection...")
    print(f"Region: {os.getenv('AWS_REGION', 'us-east-1')}")
    
    try:
        # Initialize Bedrock client
        bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
        
        print("✓ Bedrock client initialized")
        
        # Test model invocation
        model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        print(f"\nTesting model: {model_id}")
        
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "temperature": 0.7,
            "max_tokens": 100,
            "messages": [
                {
                    "role": "user",
                    "content": "Say 'Hello, I am working!' in one sentence."
                }
            ]
        }
        
        print("Invoking model...")
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body),
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get('body').read().decode())
        result = response_body.get("content")[0].get("text")
        
        print("✓ Model invocation successful!")
        print(f"\nModel response: {result}")
        print("\n" + "="*50)
        print("✓ All tests passed! Bedrock is working correctly.")
        print("="*50)
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print("\nPlease check:")
        print("  1. AWS credentials are configured")
        print("  2. IAM role has Bedrock permissions")
        print("  3. Model access is enabled in AWS console")
        return False

if __name__ == "__main__":
    test_bedrock()
