#!/usr/bin/env python3
"""
AWS Bedrock Guardrail Deployment Script for AI-Freelance-Contracts-Checker

This script creates and deploys a comprehensive guardrail for all three agents:
- Analysis Agent
- Explanation Agent  
- Negotiation Agent
"""

import boto3
import json
import os
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GuardrailDeployer:
    def __init__(self, region: str = 'us-east-1'):
        self.bedrock = boto3.client('bedrock', region_name=region)
        self.region = region
        
    def create_guardrail(self) -> str:
        """Create the comprehensive guardrail and return its ID"""
        
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), 'guardrail_config.json')
        with open(config_path) as f:
            config = json.load(f)['guardrail']
        
        # Step 1: Basic guardrail details
        guardrail_config = {
            'name': config['step1_details']['name'],
            'description': config['step1_details']['description'],
            'tags': config['step1_details']['tags']
        }
        
        # Step 2: Content filters
        content_policy_config = {
            'filtersConfig': [
                {
                    'type': 'HATE',
                    'inputStrength': config['step2_content_filters']['hate_speech']['strength'],
                    'outputStrength': config['step2_content_filters']['hate_speech']['strength']
                },
                {
                    'type': 'INSULTS', 
                    'inputStrength': config['step2_content_filters']['insults']['strength'],
                    'outputStrength': config['step2_content_filters']['insults']['strength']
                },
                {
                    'type': 'SEXUAL',
                    'inputStrength': config['step2_content_filters']['sexual_content']['strength'],
                    'outputStrength': config['step2_content_filters']['sexual_content']['strength']
                },
                {
                    'type': 'VIOLENCE',
                    'inputStrength': config['step2_content_filters']['violence']['strength'],
                    'outputStrength': config['step2_content_filters']['violence']['strength']
                },
                {
                    'type': 'MISCONDUCT',
                    'inputStrength': config['step2_content_filters']['misconduct']['strength'],
                    'outputStrength': config['step2_content_filters']['misconduct']['strength']
                },
                {
                    'type': 'PROMPT_ATTACK',
                    'inputStrength': config['step2_content_filters']['prompt_attack']['strength'],
                    'outputStrength': config['step2_content_filters']['prompt_attack']['strength']
                }
            ]
        }
        
        # Step 3: Topic policy (denied topics)
        topic_policy_config = {
            'topicsConfig': [
                {
                    'name': topic['name'],
                    'definition': topic['definition'],
                    'examples': topic['examples'],
                    'type': 'DENY'
                }
                for topic in config['step3_denied_topics']
            ]
        }
        
        # Step 4: Word policy (word filters)
        word_policy_config = {
            'wordsConfig': [
                {
                    'text': 'legal advice'
                },
                {
                    'text': 'attorney-client privilege'
                },
                {
                    'text': 'definitive legal outcome'
                }
            ],
            'managedWordListsConfig': [
                {
                    'type': 'PROFANITY'
                }
            ]
        }
        
        # Step 5: Sensitive information policy
        sensitive_info_policy_config = {
            'piiEntitiesConfig': [
                {'type': 'SSN', 'action': 'ANONYMIZE'},
                {'type': 'CREDIT_DEBIT_CARD_NUMBER', 'action': 'ANONYMIZE'},
                {'type': 'BANK_ACCOUNT_NUMBER', 'action': 'ANONYMIZE'},
                {'type': 'PHONE', 'action': 'ANONYMIZE'},
                {'type': 'EMAIL', 'action': 'ANONYMIZE'},
                {'type': 'PASSPORT_NUMBER', 'action': 'ANONYMIZE'},
                {'type': 'DRIVER_ID', 'action': 'ANONYMIZE'}
            ],
            'regexesConfig': [
                {
                    'name': 'salary_ranges',
                    'description': 'Detect specific salary amounts',
                    'pattern': r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?',
                    'action': 'ANONYMIZE'
                }
            ]
        }
        
        # Step 6: Contextual grounding check
        contextual_grounding_config = {
            'filtersConfig': [
                {
                    'type': 'GROUNDING',
                    'threshold': config['step6_contextual_grounding']['grounding_threshold']
                },
                {
                    'type': 'RELEVANCE', 
                    'threshold': 0.8
                }
            ]
        }
        
        try:
            # Create the guardrail
            response = self.bedrock.create_guardrail(
                name=guardrail_config['name'],
                description=guardrail_config['description'],
                topicPolicyConfig=topic_policy_config,
                contentPolicyConfig=content_policy_config,
                wordPolicyConfig=word_policy_config,
                sensitiveInformationPolicyConfig=sensitive_info_policy_config,
                contextualGroundingPolicyConfig=contextual_grounding_config,
                tags=guardrail_config['tags']
            )
            
            guardrail_id = response['guardrailId']
            logger.info(f"Guardrail created successfully: {guardrail_id}")
            
            # Create a version
            version_response = self.bedrock.create_guardrail_version(
                guardrailIdentifier=guardrail_id,
                description="Initial production version"
            )
            
            version = version_response['version']
            logger.info(f"Guardrail version created: {version}")
            
            return guardrail_id, version
            
        except Exception as e:
            logger.error(f"Failed to create guardrail: {e}")
            raise
    
    def update_agent_configs(self, guardrail_id: str, version: str):
        """Update agent configurations to use the guardrail"""
        
        agents_config = {
            'analysis': {
                'path': 'src/agents/analysis/.bedrock_agentcore.yaml',
                'agent_name': 'contractguard-analysis'
            },
            'explanation': {
                'path': 'src/agents/explanation/.bedrock_agentcore.yaml', 
                'agent_name': 'contractguard-explanation'
            },
            'negotiation': {
                'path': 'src/agents/negotiation/.bedrock_agentcore.yaml',
                'agent_name': 'contractguard-negotiation'
            }
        }
        
        guardrail_config = {
            'guardrailIdentifier': guardrail_id,
            'guardrailVersion': version
        }
        
        for agent_type, config in agents_config.items():
            config_path = os.path.join(
                os.path.dirname(__file__), 
                '..', '..', config['path']
            )
            
            if os.path.exists(config_path):
                # Read existing config
                with open(config_path) as f:
                    agent_config = f.read()
                
                # Add guardrail configuration
                guardrail_section = f"""
guardrails:
  {config['agent_name']}:
    guardrailIdentifier: {guardrail_id}
    guardrailVersion: "{version}"
    trace: true
"""
                
                # Append to config
                with open(config_path, 'a') as f:
                    f.write(guardrail_section)
                
                logger.info(f"Updated {agent_type} agent config with guardrail")
            else:
                logger.warning(f"Config file not found: {config_path}")

def main():
    """Deploy the comprehensive guardrail"""
    deployer = GuardrailDeployer()
    
    try:
        # Create guardrail
        guardrail_id, version = deployer.create_guardrail()
        
        # Update agent configurations
        deployer.update_agent_configs(guardrail_id, version)
        
        # Save guardrail info
        guardrail_info = {
            'guardrail_id': guardrail_id,
            'version': version,
            'region': deployer.region,
            'status': 'deployed'
        }
        
        info_path = os.path.join(
            os.path.dirname(__file__), 
            'guardrail_info.json'
        )
        
        with open(info_path, 'w') as f:
            json.dump(guardrail_info, f, indent=2)
        
        print(f"✅ Guardrail deployed successfully!")
        print(f"   ID: {guardrail_id}")
        print(f"   Version: {version}")
        print(f"   Region: {deployer.region}")
        
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        raise

if __name__ == '__main__':
    main()