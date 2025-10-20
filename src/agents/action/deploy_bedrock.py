"""
Deploy Action Agent to AWS Bedrock as a conversational AI agent
This creates a chat interface with memory, not hardcoded responses
"""

import boto3
import json
import time
import os
from datetime import datetime

class BedrockAgentDeployer:
    def __init__(self, region='us-east-1'):
        self.region = region
        self.bedrock_agent = boto3.client('bedrock-agent', region_name=region)
        self.iam = boto3.client('iam', region_name=region)
        self.timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        
    def deploy_action_agent(self):
        """Deploy Action Agent as Bedrock Agent with conversational interface"""
        
        print("\n" + "="*60)
        print("🚀 Deploying Action Agent to AWS Bedrock")
        print("="*60 + "\n")
        
        # Step 1: Create IAM role for Bedrock Agent
        print("Step 1: Creating IAM role...")
        role_arn = self._create_agent_role()
        print(f"✅ Role created: {role_arn}\n")
        
        # Wait for role to propagate
        time.sleep(10)
        
        # Step 2: Create Bedrock Agent with conversational instructions
        print("Step 2: Creating Bedrock Agent...")
        agent_id, agent_arn = self._create_bedrock_agent(role_arn)
        print(f"✅ Agent created: {agent_id}\n")
        
        # Wait for agent to be in PREPARED or NOT_PREPARED state
        print("   Waiting for agent to be ready...")
        self._wait_for_agent_ready(agent_id)
        print("   ✅ Agent is ready\n")
        
        # Step 3: Define action group with tools
        print("Step 3: Creating action group with tools...")
        action_group_id = self._create_action_group(agent_id)
        print(f"✅ Action group created: {action_group_id}\n")
        
        # Step 4: Prepare agent (required before testing)
        print("Step 4: Preparing agent for use...")
        self._prepare_agent(agent_id)
        print("✅ Agent prepared\n")
        
        # Step 5: Create agent alias
        print("Step 5: Creating agent alias...")
        alias_id = self._create_agent_alias(agent_id)
        print(f"✅ Alias created: {alias_id}\n")
        
        # Save configuration
        config = {
            'agent_id': agent_id,
            'agent_arn': agent_arn,
            'alias_id': alias_id,
            'role_arn': role_arn,
            'region': self.region,
            'deployed_at': self.timestamp
        }
        
        with open('../../config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("\n" + "="*60)
        print("✅ Deployment Complete!")
        print("="*60)
        print(f"\n📋 Agent Details:")
        print(f"   Agent ID: {agent_id}")
        print(f"   Alias ID: {alias_id}")
        print(f"   Region: {self.region}")
        print(f"\n💬 Test the agent:")
        print(f"   python test_bedrock_chat.py")
        print("\n" + "="*60 + "\n")
        
        return config
    
    def _create_agent_role(self):
        """Create IAM role for Bedrock Agent"""
        role_name = f"ActionAgentRole-{self.timestamp}"
        
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "bedrock.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }
        
        try:
            response = self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="Role for ContractGuard Action Agent"
            )
            role_arn = response['Role']['Arn']
            
            # Attach policy for Bedrock model invocation
            policy_document = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel",
                        "bedrock:InvokeModelWithResponseStream"
                    ],
                    "Resource": "arn:aws:bedrock:*::foundation-model/*"
                }]
            }
            
            self.iam.put_role_policy(
                RoleName=role_name,
                PolicyName="BedrockModelAccess",
                PolicyDocument=json.dumps(policy_document)
            )
            
            return role_arn
            
        except Exception as e:
            print(f"❌ Error creating role: {e}")
            raise
    
    def _create_bedrock_agent(self, role_arn):
        """Create Bedrock Agent with conversational AI instructions"""
        
        # Conversational agent instruction (not hardcoded responses)
        agent_instruction = """You are a legal action assistant for freelancers who have disputes with clients AFTER signing a contract. 

Your role is to have a CONVERSATIONAL dialogue with the user to understand their situation, then use your tools to help them:

1. ENGAGE IN CONVERSATION - Ask clarifying questions about:
   - What specific problem they're facing (non-payment, contract breach, IP theft, scope creep)
   - Details of their contract (payment terms, deliverables, etc.)
   - Timeline of events
   - What they've tried so far
   - How much money is at stake
   - Their location/jurisdiction

2. USE TOOLS DYNAMICALLY - Based on the conversation, call these tools:
   - search_similar_cases: Find relevant legal precedents
   - generate_action_plan: Create personalized step-by-step plan
   - get_evidence_checklist: Provide evidence they need to collect
   - get_legal_resources: Find jurisdiction-specific legal help

3. PROVIDE GUIDANCE - Explain the results in simple terms, suggest next steps, answer follow-up questions

IMPORTANT: 
- Be conversational and empathetic, not robotic
- Ask questions before making assumptions
- Use tools based on what the user says, not predetermined scripts
- Explain legal concepts in plain English
- Provide actionable advice, not just information
- Remember context from earlier in the conversation

START by greeting the user and asking about their situation."""

        try:
            response = self.bedrock_agent.create_agent(
                agentName=f"ActionAgent-{self.timestamp}",
                agentResourceRoleArn=role_arn,
                description="Conversational AI agent for freelancer contract disputes",
                foundationModel="anthropic.claude-3-5-sonnet-20240620-v1:0",
                instruction=agent_instruction,
                idleSessionTTLInSeconds=1800  # 30 minutes session memory
            )
            
            return response['agent']['agentId'], response['agent']['agentArn']
            
        except Exception as e:
            print(f"❌ Error creating agent: {e}")
            raise
    
    def _create_action_group(self, agent_id):
        """Create action group with 4 tools"""
        
        # Define tools in OpenAPI format (as JSON string)
        action_group_schema_json = """{
            "openapi": "3.0.0",
            "info": {
                "title": "Action Agent Tools",
                "version": "1.0.0",
                "description": "Tools for helping freelancers with contract disputes"
            },
            "paths": {
                "/search_similar_cases": {
                    "post": {
                        "description": "Search for similar legal cases and precedents",
                        "requestBody": {
                            "required": true,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "issue_type": {
                                                "type": "string",
                                                "enum": ["non_payment", "breach_of_contract", "ip_theft", "scope_creep"],
                                                "description": "Type of legal issue"
                                            },
                                            "jurisdiction": {
                                                "type": "string",
                                                "enum": ["usa", "uk", "eu"],
                                                "description": "Legal jurisdiction"
                                            },
                                            "contract_text": {
                                                "type": "string",
                                                "description": "Full contract text for keyword extraction"
                                            }
                                        },
                                        "required": ["issue_type", "jurisdiction"]
                                    }
                                }
                            }
                        }
                    }
                },
                "/generate_action_plan": {
                    "post": {
                        "description": "Generate personalized action plan with AI",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "issue_description": {"type": "string"},
                                            "jurisdiction": {"type": "string"},
                                            "amount_at_stake": {"type": "number"},
                                            "days_since_issue": {"type": "integer"}
                                        },
                                        "required": ["issue_description", "jurisdiction", "amount_at_stake"]
                                    }
                                }
                            }
                        }
                    }
                },
                "/get_evidence_checklist": {
                    "post": {
                        "description": "Get issue-specific evidence checklist",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "issue_type": {
                                                "type": "string",
                                                "enum": ["non_payment", "breach_of_contract", "ip_theft", "scope_creep"]
                                            }
                                        },
                                        "required": ["issue_type"]
                                    }
                                }
                            }
                        }
                    }
                },
                "/get_legal_resources": {
                    "post": {
                        "description": "Get jurisdiction-specific legal resources",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "jurisdiction": {"type": "string"},
                                            "issue_type": {"type": "string"},
                                            "amount_at_stake": {"type": "number"}
                                        },
                                        "required": ["jurisdiction", "issue_type", "amount_at_stake"]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        try:
            # Create Lambda function for action group
            lambda_arn = self._create_action_lambda()
            
            response = self.bedrock_agent.create_agent_action_group(
                agentId=agent_id,
                agentVersion='DRAFT',
                actionGroupName='ActionAgentTools',
                description='Tools for freelancer legal disputes',
                actionGroupExecutor={'lambda': lambda_arn},
                apiSchema={'payload': json.dumps(action_group_schema)},
                actionGroupState='ENABLED'
            )
            
            return response['agentActionGroup']['actionGroupId']
            
        except Exception as e:
            print(f"❌ Error creating action group: {e}")
            raise
    
    def _create_action_lambda(self):
        """Create Lambda function that executes the tools"""
        import zipfile
        import shutil
        
        lambda_client = boto3.client('lambda', region_name=self.region)
        function_name = f"ActionAgentTools-{self.timestamp}"
        
        # Create deployment package
        print("      Creating Lambda deployment package...")
        
        # Use temp directory (works on Windows)
        import tempfile
        temp_dir = tempfile.gettempdir()
        zip_path = os.path.join(temp_dir, f'lambda_package_{self.timestamp}.zip')
        
        # Create a zip file with lambda_function.py and tools.py
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write('lambda_function.py', 'lambda_function.py')
            zipf.write('tools.py', 'tools.py')
        
        print(f"      Package created: {zip_path}")
        
        # Read zip file
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        # Create Lambda execution role
        lambda_role_arn = self._create_lambda_role()
        
        print("      Waiting for Lambda role to propagate...")
        time.sleep(10)
        
        # Create Lambda function
        try:
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.13',
                Role=lambda_role_arn,
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': zip_content},
                Description='Action Agent tools executor for Bedrock',
                Timeout=60,
                MemorySize=512
            )
            
            lambda_arn = response['FunctionArn']
            
            # Grant Bedrock permission to invoke Lambda
            lambda_client.add_permission(
                FunctionName=function_name,
                StatementId='AllowBedrockInvoke',
                Action='lambda:InvokeFunction',
                Principal='bedrock.amazonaws.com'
            )
            
            print(f"      ✅ Lambda function created: {lambda_arn}")
            return lambda_arn
            
        except Exception as e:
            print(f"      ❌ Error creating Lambda: {e}")
            raise
    
    def _create_lambda_role(self):
        """Create IAM role for Lambda execution"""
        role_name = f"ActionAgentLambdaRole-{self.timestamp}"
        
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }
        
        try:
            response = self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="Role for Action Agent Lambda function"
            )
            role_arn = response['Role']['Arn']
            
            # Attach basic Lambda execution policy
            self.iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            )
            
            # Attach policy for Bedrock model invocation
            policy_document = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel",
                        "bedrock:InvokeModelWithResponseStream"
                    ],
                    "Resource": "arn:aws:bedrock:*::foundation-model/*"
                }]
            }
            
            self.iam.put_role_policy(
                RoleName=role_name,
                PolicyName="BedrockAccess",
                PolicyDocument=json.dumps(policy_document)
            )
            
            return role_arn
            
        except Exception as e:
            print(f"      ❌ Error creating Lambda role: {e}")
            raise
    
    def _wait_for_agent_ready(self, agent_id):
        """Wait for agent to be in a state where we can add action groups"""
        max_attempts = 30
        for i in range(max_attempts):
            try:
                response = self.bedrock_agent.get_agent(agentId=agent_id)
                status = response['agent']['agentStatus']
                
                if status in ['PREPARED', 'NOT_PREPARED', 'FAILED']:
                    return
                
                print(f"      Status: {status}, waiting... ({i+1}/{max_attempts})")
                time.sleep(10)
                
            except Exception as e:
                print(f"      Error checking status: {e}")
                time.sleep(10)
        
        raise Exception("Agent did not become ready in time")
    
    def _prepare_agent(self, agent_id):
        """Prepare agent for use"""
        try:
            self.bedrock_agent.prepare_agent(agentId=agent_id)
            
            # Wait for preparation to complete
            time.sleep(30)
            
        except Exception as e:
            print(f"❌ Error preparing agent: {e}")
            raise
    
    def _create_agent_alias(self, agent_id):
        """Create agent alias for production use"""
        try:
            response = self.bedrock_agent.create_agent_alias(
                agentId=agent_id,
                agentAliasName='prod',
                description='Production alias for Action Agent'
            )
            
            return response['agentAlias']['agentAliasId']
            
        except Exception as e:
            print(f"❌ Error creating alias: {e}")
            raise


if __name__ == '__main__':
    deployer = BedrockAgentDeployer(region='us-east-1')
    config = deployer.deploy_action_agent()
    
    print("✅ Action Agent deployed successfully!")
    print(f"   Config saved to: config.json")
