"""
Test AWS Connection and Bedrock Access

This script verifies:
1. AWS credentials are valid
2. Bedrock service is accessible
3. Claude 3.7 Sonnet model can be invoked
"""
import boto3
import json
from botocore.exceptions import ClientError


def test_aws_connection():
    """Test AWS credentials and Bedrock access"""
    
    print("Testing AWS Connection...")
    print("="*60)
    
    # Test 1: AWS Credentials
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print("✅ AWS Credentials Valid")
        print(f"   Account: {identity['Account']}")
        print(f"   User ARN: {identity['Arn']}")
    except Exception as e:
        print(f"❌ AWS Credentials Failed: {str(e)}")
        print("\n💡 Fix: Make sure environment variables are set:")
        print("   $env:AWS_ACCESS_KEY_ID")
        print("   $env:AWS_SECRET_ACCESS_KEY")
        print("   $env:AWS_DEFAULT_REGION")
        return False
    
    # Test 2: Bedrock Access
    try:
        bedrock = boto3.client('bedrock', region_name='us-east-1')
        # List foundation models
        response = bedrock.list_foundation_models()
        print("✅ Bedrock Access Valid")
        print(f"   Available models: {len(response['modelSummaries'])}")
    except Exception as e:
        print(f"❌ Bedrock Access Failed: {str(e)}")
        print("\n💡 Fix: Make sure your IAM user has Bedrock permissions")
        return False
    
    # Test 3: Claude 3.7 Sonnet Access
    try:
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
        
        # Simple test prompt
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "messages": [
                {
                    "role": "user",
                    "content": "Say 'Hello, I am Claude!'"
                }
            ]
        }
        
        print("⏳ Testing Claude 3.7 Sonnet invocation...")
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        message = response_body['content'][0]['text']
        
        print("✅ Claude 3.7 Sonnet Access Valid")
        print(f"   Model invoked successfully!")
        print(f"   Claude says: {message}")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDeniedException':
            print("❌ Claude 3.7 Sonnet Access Denied")
            print("\n💡 Fix: Request model access in Bedrock console:")
            print("   1. Go to: https://console.aws.amazon.com/bedrock")
            print("   2. Click 'Model access' in sidebar")
            print("   3. Click 'Manage model access'")
            print("   4. Check 'Claude 3.7 Sonnet'")
            print("   5. Click 'Request model access'")
            print("   6. Wait for approval (usually instant)")
        elif error_code == 'ValidationException':
            print("❌ Claude 3.7 Sonnet Not Available in Region")
            print("\n💡 Fix: Try region us-west-2:")
            print("   $env:AWS_DEFAULT_REGION='us-west-2'")
        else:
            print(f"❌ Claude Test Failed: {error_code}")
            print(f"   Message: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"❌ Claude Test Failed: {str(e)}")
        return False
    
    print("="*60)
    print("🎉 All AWS Tests Passed!")
    print("You're ready to run the Explanation Agent!")
    print("\nNext step: python test_real_agent.py")
    return True


if __name__ == "__main__":
    success = test_aws_connection()
    
    if not success:
        print("\n" + "="*60)
        print("⚠️  Tests Failed - Please fix issues above")
        print("="*60)
        exit(1)
