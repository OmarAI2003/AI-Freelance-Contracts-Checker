#!/usr/bin/env python3
"""
Simplified AWS Bedrock Guardrail Deployment Script
"""

import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_guardrail_config():
    """Create guardrail configuration for AWS CLI deployment"""
    
    config_path = os.path.join(os.path.dirname(__file__), 'guardrail_config.json')
    with open(config_path) as f:
        config = json.load(f)['guardrail']
    
    # AWS CLI compatible configuration
    aws_config = {
        "name": config['step1_details']['name'],
        "description": config['step1_details']['description'],
        "topicPolicyConfig": {
            "topicsConfig": [
                {
                    "name": topic['name'],
                    "definition": topic['definition'],
                    "examples": topic['examples'],
                    "type": "DENY"
                }
                for topic in config['step3_denied_topics']
            ]
        },
        "contentPolicyConfig": {
            "filtersConfig": [
                {"type": "HATE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
                {"type": "INSULTS", "inputStrength": "MEDIUM", "outputStrength": "MEDIUM"},
                {"type": "SEXUAL", "inputStrength": "HIGH", "outputStrength": "HIGH"},
                {"type": "VIOLENCE", "inputStrength": "MEDIUM", "outputStrength": "MEDIUM"},
                {"type": "MISCONDUCT", "inputStrength": "HIGH", "outputStrength": "HIGH"},
                {"type": "PROMPT_ATTACK", "inputStrength": "HIGH", "outputStrength": "HIGH"}
            ]
        },
        "wordPolicyConfig": {
            "wordsConfig": [
                {"text": "legal advice"},
                {"text": "attorney-client privilege"}
            ],
            "managedWordListsConfig": [
                {"type": "PROFANITY"}
            ]
        },
        "sensitiveInformationPolicyConfig": {
            "piiEntitiesConfig": [
                {"type": "SSN", "action": "ANONYMIZE"},
                {"type": "CREDIT_DEBIT_CARD_NUMBER", "action": "ANONYMIZE"},
                {"type": "BANK_ACCOUNT_NUMBER", "action": "ANONYMIZE"},
                {"type": "PHONE", "action": "ANONYMIZE"},
                {"type": "EMAIL", "action": "ANONYMIZE"}
            ]
        },
        "contextualGroundingPolicyConfig": {
            "filtersConfig": [
                {"type": "GROUNDING", "threshold": 0.8},
                {"type": "RELEVANCE", "threshold": 0.8}
            ]
        }
    }
    
    # Save AWS CLI config
    output_path = os.path.join(os.path.dirname(__file__), 'aws_guardrail_config.json')
    with open(output_path, 'w') as f:
        json.dump(aws_config, f, indent=2)
    
    logger.info(f"AWS CLI config saved to: {output_path}")
    
    # Generate deployment commands
    commands = [
        "# Deploy guardrail using AWS CLI:",
        f"aws bedrock create-guardrail --cli-input-json file://{output_path}",
        "",
        "# Create version:",
        "aws bedrock create-guardrail-version --guardrail-identifier <GUARDRAIL_ID> --description 'Production version'",
        "",
        "# Update agent configs with guardrail ID and version"
    ]
    
    commands_path = os.path.join(os.path.dirname(__file__), 'deployment_commands.txt')
    with open(commands_path, 'w') as f:
        f.write('\n'.join(commands))
    
    logger.info(f"Deployment commands saved to: {commands_path}")
    
    return output_path, commands_path

def main():
    """Generate deployment configuration"""
    try:
        config_path, commands_path = create_guardrail_config()
        
        print("Guardrail configuration generated successfully!")
        print(f"Config file: {config_path}")
        print(f"Commands file: {commands_path}")
        print("\nNext steps:")
        print("1. Configure AWS CLI credentials")
        print("2. Run the commands in deployment_commands.txt")
        print("3. Update agent configurations with guardrail ID")
        
    except Exception as e:
        logger.error(f"Configuration generation failed: {e}")
        raise

if __name__ == '__main__':
    main()