"""
AWS Lambda function to execute Action Agent tools
This is deployed as the action group executor for Bedrock Agent
"""

import json
import boto3
import asyncio
from typing import Dict

# Import tools from our Action Agent
import sys
import os
sys.path.append(os.path.dirname(__file__))

from tools import ActionAgentTools


def lambda_handler(event, context):
    """
    Lambda handler for Bedrock Agent action group
    
    Event format from Bedrock:
    {
        "messageVersion": "1.0",
        "agent": {...},
        "inputText": "user's message",
        "sessionId": "...",
        "actionGroup": "ActionAgentTools",
        "function": "search_similar_cases",
        "parameters": [
            {"name": "issue_type", "value": "non_payment"},
            {"name": "jurisdiction", "value": "usa"}
        ]
    }
    """
    
    print(f"Received event: {json.dumps(event)}")
    
    # Extract function name and parameters
    function_name = event.get('function')
    parameters = event.get('parameters', [])
    
    # Convert parameters list to dict
    params_dict = {param['name']: param['value'] for param in parameters}
    
    # Initialize tools
    tools = ActionAgentTools()
    
    try:
        # Route to appropriate tool
        if function_name == 'search_similar_cases':
            result = asyncio.run(tools.search_similar_cases(
                issue_type=params_dict.get('issue_type'),
                jurisdiction=params_dict.get('jurisdiction'),
                contract_text=params_dict.get('contract_text', '')
            ))
            
        elif function_name == 'generate_action_plan':
            result = asyncio.run(tools.generate_action_plan(
                issue_description=params_dict.get('issue_description'),
                jurisdiction=params_dict.get('jurisdiction'),
                amount_at_stake=float(params_dict.get('amount_at_stake', 0)),
                days_since_issue=int(params_dict.get('days_since_issue', 30))
            ))
            
        elif function_name == 'get_evidence_checklist':
            result = tools.get_evidence_checklist(
                issue_type=params_dict.get('issue_type')
            )
            
        elif function_name == 'get_legal_resources':
            result = tools.get_legal_resources(
                jurisdiction=params_dict.get('jurisdiction'),
                issue_type=params_dict.get('issue_type'),
                amount_at_stake=float(params_dict.get('amount_at_stake', 0))
            )
            
        else:
            result = {'error': f'Unknown function: {function_name}'}
        
        # Return response in Bedrock Agent format
        response = {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event['actionGroup'],
                'function': function_name,
                'functionResponse': {
                    'responseBody': {
                        'TEXT': {
                            'body': json.dumps(result)
                        }
                    }
                }
            }
        }
        
        print(f"Returning response: {json.dumps(response)}")
        return response
        
    except Exception as e:
        print(f"Error executing tool: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return error response
        error_response = {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event['actionGroup'],
                'function': function_name,
                'functionResponse': {
                    'responseBody': {
                        'TEXT': {
                            'body': json.dumps({'error': str(e)})
                        }
                    }
                }
            }
        }
        
        return error_response
