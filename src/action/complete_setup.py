"""
Complete Bedrock Agent setup automatically
Adds action group with all 4 functions programmatically
"""

import boto3
import json
import time

print("\n" + "="*60)
print("🚀 Completing Bedrock Agent Setup")
print("="*60 + "\n")

# Configuration
agent_id = 'BKOO1E5O95'
lambda_arn = 'arn:aws:lambda:us-east-1:897722703585:function:ActionAgentTools-20251018-024216'
region = 'us-east-1'

bedrock = boto3.client('bedrock-agent', region_name=region)

# Step 1: Create action group with function schemas
print("Step 1: Creating action group with 4 functions...")

try:
    # Define functions in the format Bedrock expects
    function_schemas = {
        "functions": [
            {
                "name": "search_similar_cases",
                "description": "Search for similar legal cases based on issue type and jurisdiction. Use this when user describes their problem and you need to find precedents.",
                "parameters": {
                    "issue_type": {
                        "description": "Type of issue: non_payment, breach_of_contract, ip_theft, or scope_creep",
                        "required": True,
                        "type": "string"
                    },
                    "jurisdiction": {
                        "description": "Location: usa, uk, or eu",
                        "required": True,
                        "type": "string"
                    },
                    "contract_text": {
                        "description": "Full contract text for keyword extraction (optional)",
                        "required": False,
                        "type": "string"
                    }
                }
            },
            {
                "name": "generate_action_plan",
                "description": "Generate personalized action plan with AI based on user's situation. Use this after understanding their problem details.",
                "parameters": {
                    "issue_description": {
                        "description": "Description of the problem",
                        "required": True,
                        "type": "string"
                    },
                    "jurisdiction": {
                        "description": "Location: usa, uk, or eu",
                        "required": True,
                        "type": "string"
                    },
                    "amount_at_stake": {
                        "description": "Amount of money involved",
                        "required": True,
                        "type": "number"
                    },
                    "days_since_issue": {
                        "description": "Days since problem started (optional, default 30)",
                        "required": False,
                        "type": "number"
                    }
                }
            },
            {
                "name": "get_evidence_checklist",
                "description": "Get issue-specific evidence collection checklist. Use this to help user prepare for legal action.",
                "parameters": {
                    "issue_type": {
                        "description": "Type: non_payment, breach_of_contract, ip_theft, or scope_creep",
                        "required": True,
                        "type": "string"
                    }
                }
            },
            {
                "name": "get_legal_resources",
                "description": "Find jurisdiction-specific legal resources, costs, and filing information. Use this to provide practical next steps.",
                "parameters": {
                    "jurisdiction": {
                        "description": "Location: usa, uk, or eu",
                        "required": True,
                        "type": "string"
                    },
                    "issue_type": {
                        "description": "Type of issue",
                        "required": True,
                        "type": "string"
                    },
                    "amount_at_stake": {
                        "description": "Amount of money involved",
                        "required": True,
                        "type": "number"
                    }
                }
            }
        ]
    }
    
    response = bedrock.create_agent_action_group(
        agentId=agent_id,
        agentVersion='DRAFT',
        actionGroupName='ActionAgentTools',
        description='Tools for freelancer contract dispute assistance',
        actionGroupExecutor={'lambda': lambda_arn},
        functionSchema={'functions': function_schemas['functions']},
        actionGroupState='ENABLED'
    )
    
    action_group_id = response['agentActionGroup']['actionGroupId']
    print(f"✅ Action group created: {action_group_id}\n")
    
except Exception as e:
    if 'already exists' in str(e).lower():
        print("⚠️  Action group already exists, updating...\n")
        # Get existing action groups
        response = bedrock.list_agent_action_groups(
            agentId=agent_id,
            agentVersion='DRAFT'
        )
        
        for ag in response['actionGroupSummaries']:
            if ag['actionGroupName'] == 'ActionAgentTools':
                action_group_id = ag['actionGroupId']
                # Update existing
                bedrock.update_agent_action_group(
                    agentId=agent_id,
                    agentVersion='DRAFT',
                    actionGroupId=action_group_id,
                    actionGroupName='ActionAgentTools',
                    description='Tools for freelancer contract dispute assistance',
                    actionGroupExecutor={'lambda': lambda_arn},
                    functionSchema={'functions': function_schemas['functions']},
                    actionGroupState='ENABLED'
                )
                print(f"✅ Action group updated: {action_group_id}\n")
                break
    else:
        print(f"❌ Error: {e}\n")
        raise

# Step 2: Prepare agent
print("Step 2: Preparing agent...")
try:
    bedrock.prepare_agent(agentId=agent_id)
    print("✅ Agent preparation started\n")
    
    # Wait for preparation
    print("   Waiting for preparation to complete...")
    for i in range(30):
        time.sleep(10)
        try:
            response = bedrock.get_agent(agentId=agent_id)
            status = response['agent']['agentStatus']
            print(f"   Status: {status} ({i+1}/30)")
            
            if status == 'PREPARED':
                print("   ✅ Agent is prepared!\n")
                break
        except:
            pass
    
except Exception as e:
    print(f"⚠️  Preparation error (may be okay): {e}\n")

# Step 3: Create alias
print("Step 3: Creating agent alias...")
try:
    # Check if alias exists
    try:
        aliases = bedrock.list_agent_aliases(agentId=agent_id)
        alias_exists = False
        alias_id = None
        
        for alias in aliases.get('agentAliasSummaries', []):
            if alias['agentAliasName'] == 'prod':
                alias_exists = True
                alias_id = alias['agentAliasId']
                print(f"✅ Alias already exists: {alias_id}\n")
                break
        
        if not alias_exists:
            response = bedrock.create_agent_alias(
                agentId=agent_id,
                agentAliasName='prod',
                description='Production alias for Action Agent'
            )
            alias_id = response['agentAlias']['agentAliasId']
            print(f"✅ Alias created: {alias_id}\n")
    
    except Exception as e:
        print(f"⚠️  Alias error: {e}\n")
        alias_id = 'TSTALIASID'  # Default test alias

except Exception as e:
    print(f"⚠️  Error creating alias: {e}\n")
    alias_id = 'TSTALIASID'

# Save configuration
config = {
    'agent_id': agent_id,
    'alias_id': alias_id,
    'lambda_arn': lambda_arn,
    'region': region,
    'action_group': 'ActionAgentTools'
}

with open('../../config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("="*60)
print("✅ Setup Complete!")
print("="*60)
print(f"\n📋 Configuration:")
print(f"   Agent ID: {agent_id}")
print(f"   Alias ID: {alias_id}")
print(f"   Action Group: ActionAgentTools (4 functions)")
print(f"   Lambda: {lambda_arn}")

print("\n" + "="*60)
print("🧪 Test Your Agent")
print("="*60)
print("\nOption 1: AWS Console")
print(f"https://console.aws.amazon.com/bedrock/home?region={region}#/agents/{agent_id}")

print("\nOption 2: Python Test Script")
print("   python test_chat.py")

print("\n" + "="*60 + "\n")
