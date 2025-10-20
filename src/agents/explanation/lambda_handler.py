"""
AWS Lambda Handler for Explanation Agent

This is the entry point for AWS Lambda function.
"""
import json
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from agents.explanation.agent import ExplanationAgent

# Initialize agent globally for Lambda warm starts (reused across invocations)
agent = None

def lambda_handler(event, context):
    """
    AWS Lambda handler for Explanation Agent
    
    Expected input:
    {
        "body": "{\"clause_text\": \"...\", \"clause_type\": \"payment\"}"
    }
    
    Returns:
    {
        "statusCode": 200,
        "headers": {...},
        "body": "{...}"
    }
    """
    global agent
    
    # Initialize agent on cold start (once per Lambda container)
    if agent is None:
        print("Cold start: Initializing Explanation Agent...")
        try:
            agent = ExplanationAgent(enable_memory=False)
            print("✅ Agent initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize agent: {str(e)}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({
                    'error': 'Failed to initialize agent',
                    'details': str(e)
                })
            }
    else:
        print("Warm start: Using existing agent")
    
    try:
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': ''
            }
        
        # Parse request body
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)
        
        clause_text = body.get('clause_text')
        clause_type = body.get('clause_type')
        contract_type = body.get('contract_type')
        
        # Validate input
        if not clause_text:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing required field: clause_text',
                    'example': {
                        'clause_text': 'Payment within 90 days',
                        'clause_type': 'payment'
                    }
                })
            }
        
        print(f"Processing clause: {clause_text[:50]}...")
        print(f"Clause type: {clause_type}")
        
        # Get explanation from agent
        result = agent.explain(
            clause_text=clause_text,
            clause_type=clause_type,
            contract_type=contract_type
        )
        
        print("✅ Explanation generated successfully")
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(result)
        }
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {str(e)}")
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Invalid JSON in request body',
                'details': str(e)
            })
        }
        
    except Exception as e:
        print(f"❌ Error processing request: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            })
        }


# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        'body': json.dumps({
            'clause_text': 'Payment shall be made within 90 days of invoice submission.',
            'clause_type': 'payment'
        })
    }
    
    print("Testing Lambda handler locally...")
    response = lambda_handler(test_event, None)
    print(f"Status Code: {response['statusCode']}")
    print(f"Response: {response['body'][:200]}...")
