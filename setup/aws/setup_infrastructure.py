"""AWS Infrastructure Setup Script"""

import boto3
import json
from botocore.exceptions import ClientError

def create_dynamodb_tables():
    """Create DynamoDB tables for market rates and case law"""
    dynamodb = boto3.client('dynamodb')
    
    # Create market rates table
    try:
        dynamodb.create_table(
            TableName='freelance_market_rates',
            KeySchema=[
                {'AttributeName': 'role', 'KeyType': 'HASH'},
                {'AttributeName': 'jurisdiction', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'role', 'AttributeType': 'S'},
                {'AttributeName': 'jurisdiction', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("Created market rates table")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("Market rates table already exists")
        else:
            raise e

    # Create case law table
    try:
        dynamodb.create_table(
            TableName='freelance_case_law',
            KeySchema=[
                {'AttributeName': 'issue_type', 'KeyType': 'HASH'},
                {'AttributeName': 'jurisdiction', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'issue_type', 'AttributeType': 'S'},
                {'AttributeName': 'jurisdiction', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("Created case law table")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("Case law table already exists")
        else:
            raise e

def create_s3_bucket():
    """Create S3 bucket for contract documents"""
    s3 = boto3.client('s3')
    
    try:
        s3.create_bucket(
            Bucket='freelance-contract-documents',
            CreateBucketConfiguration={
                'LocationConstraint': 'us-east-1'
            }
        )
        print("Created S3 bucket")
        
        # Enable versioning for document history
        s3.put_bucket_versioning(
            Bucket='freelance-contract-documents',
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print("Enabled bucket versioning")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print("S3 bucket already exists")
        else:
            raise e

def setup_bedrock():
    """Configure Bedrock for access to Claude"""
    bedrock = boto3.client('bedrock')
    
    try:
        # Enable model access
        bedrock.put_model_invocation_logging_configuration(
            loggingConfig={
                'modelId': 'anthropic.claude-3-sonnet-20240229',
                'enabled': True
            }
        )
        print("Configured Bedrock for Claude access")
    except ClientError as e:
        print(f"Error configuring Bedrock: {e}")

def main():
    """Main setup function"""
    print("Setting up AWS infrastructure...")
    
    create_dynamodb_tables()
    create_s3_bucket()
    setup_bedrock()
    
    print("Setup complete!")

if __name__ == "__main__":
    main()