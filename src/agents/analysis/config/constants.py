"""
Configuration constants for Analysis Agent
"""

# Knowledge Base Configurations
FREELANCE_LAWS_KB = {
    "id": "XNHMT6VAJC",
    "arn": "arn:aws:aoss:us-east-1:897722703585:collection/duhjjq1gv8zqauo1a08h",
    "name": "ContractGuard-Freelance-Laws-KB",
    "description": "Knowledge base for freelance laws and regulations",
    "model": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
}

CONTRACT_TYPES_KB = {
    "id": "9LRYYFY2BR",
    "arn": "arn:aws:aoss:us-east-1:897722703585:collection/qcavvz18e6myu70e1imj",
    "name": "ContractGuard-Contract-Types-KB",
    "description": "Knowledge base for contract types (MSA, NDA, Service Agreement, SOW)",
    "model": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
}

# AWS Region
AWS_REGION = "us-east-1"

# Model ID for contract analysis
ANALYSIS_MODEL_ID = "amazon.titan-text-express-v1"

# Risk Level Classifications
RISK_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL", "SCAM"]