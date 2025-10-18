#!/usr/bin/env python3
"""
ContractGuard AI - Simplified Infrastructure Setup Script

This script creates essential AWS resources:
- S3 buckets for document storage
- IAM roles with proper permissions
- Generates config.json with all resource IDs

Note: Bedrock Knowledge Bases will be created by each developer when they're ready
with their own documents. This avoids the complexity of OpenSearch/Kendra setup.

Usage:
    python setup_simple.py

Requirements:
    - AWS credentials configured (or set via environment variables)
    - S3 access
    - IAM permissions
"""

import boto3
import json
import sys
from datetime import datetime
from botocore.exceptions import ClientError

class ContractGuardInfrastructure:
    def __init__(self, region='us-east-1'):
        """Initialize AWS clients"""
        self.region = region
        self.s3 = boto3.client('s3', region_name=region)
        self.iam = boto3.client('iam')
        
        try:
            self.account_id = boto3.client('sts').get_caller_identity()['Account']
        except Exception as e:
            print(f"❌ Error getting AWS account ID: {e}")
            print("   Make sure AWS credentials are configured")
            sys.exit(1)
        
        # Unique suffix for resource names
        self.suffix = datetime.now().strftime('%Y%m%d-%H%M%S')
        
    def create_s3_buckets(self):
        """Create S3 buckets for document storage"""
        print("\n📦 Creating S3 buckets for document storage...")
        
        buckets = {
            'legal': f'contractguard-legal-docs-{self.suffix}',
            'contracts': f'contractguard-contracts-{self.suffix}',
            'uploads': f'contractguard-uploads-{self.suffix}'
        }
        
        for name, bucket_name in buckets.items():
            try:
                # Create bucket
                if self.region == 'us-east-1':
                    self.s3.create_bucket(Bucket=bucket_name)
                else:
                    self.s3.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': self.region}
                    )
                
                # Enable versioning
                self.s3.put_bucket_versioning(
                    Bucket=bucket_name,
                    VersioningConfiguration={'Status': 'Enabled'}
                )
                
                # Add CORS for uploads bucket
                if name == 'uploads':
                    self.s3.put_bucket_cors(
                        Bucket=bucket_name,
                        CORSConfiguration={
                            'CORSRules': [{
                                'AllowedHeaders': ['*'],
                                'AllowedMethods': ['GET', 'PUT', 'POST'],
                                'AllowedOrigins': ['*'],
                                'MaxAgeSeconds': 3000
                            }]
                        }
                    )
                
                print(f"   ✅ Created S3 bucket: {bucket_name}")
                
            except ClientError as e:
                if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                    print(f"   ⚠️  Bucket {bucket_name} already exists, skipping")
                else:
                    print(f"   ❌ Error creating bucket {bucket_name}: {e}")
                    raise
        
        return buckets
    
    def create_iam_role(self):
        """Create IAM role for Bedrock agents"""
        print("\n🔐 Creating IAM role for Bedrock agents...")
        
        role_name = f'ContractGuardAgentRole-{self.suffix}'
        
        # Trust policy for Bedrock
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "bedrock.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }
        
        try:
            # Create role
            response = self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='Role for ContractGuard Bedrock Agents'
            )
            role_arn = response['Role']['Arn']
            print(f"   ✅ Created IAM role: {role_name}")
            
            # Attach policies for S3 and Bedrock
            policy_document = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:GetObject",
                            "s3:PutObject",
                            "s3:ListBucket"
                        ],
                        "Resource": [
                            f"arn:aws:s3:::contractguard-*",
                            f"arn:aws:s3:::contractguard-*/*"
                        ]
                    },
                    {
                        "Effect": "Allow",
                        "Action": [
                            "bedrock:InvokeModel",
                            "bedrock:InvokeModelWithResponseStream"
                        ],
                        "Resource": "*"
                    }
                ]
            }
            
            self.iam.put_role_policy(
                RoleName=role_name,
                PolicyName='ContractGuardAgentPolicy',
                PolicyDocument=json.dumps(policy_document)
            )
            
            print(f"   ✅ Attached policies to role")
            
            return {
                'role_name': role_name,
                'role_arn': role_arn
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                print(f"   ⚠️  Role {role_name} already exists")
                response = self.iam.get_role(RoleName=role_name)
                return {
                    'role_name': role_name,
                    'role_arn': response['Role']['Arn']
                }
            else:
                print(f"   ❌ Error creating IAM role: {e}")
                raise
    
    def save_config(self, config):
        """Save configuration to config.json"""
        config_path = 'config.json'
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n💾 Configuration saved to: {config_path}")
        print("\n" + "="*70)
        print("⚠️  IMPORTANT: Do NOT commit config.json to git!")
        print("   It's already in .gitignore - keep resource IDs private")
        print("="*70)
    
    def setup_all(self):
        """Run complete infrastructure setup"""
        print("\n" + "="*70)
        print("🚀 ContractGuard AI - Simplified Infrastructure Setup")
        print("="*70)
        print(f"   AWS Account: {self.account_id}")
        print(f"   Region: {self.region}")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        try:
            # Step 1: Create S3 buckets
            buckets = self.create_s3_buckets()
            
            # Step 2: Create IAM role
            iam_role = self.create_iam_role()
            
            # Step 3: Generate Memory ID
            memory_id = f'contractguard-memory-{self.suffix}'
            print(f"\n🧠 Memory ID generated: {memory_id}")
            print(f"   This will be used when deploying agents with AgentCore")
            
            # Step 4: Save configuration
            config = {
                "region": self.region,
                "account_id": self.account_id,
                "legal_bucket": buckets['legal'],
                "contracts_bucket": buckets['contracts'],
                "uploads_bucket": buckets['uploads'],
                "agent_role_name": iam_role['role_name'],
                "agent_role_arn": iam_role['role_arn'],
                "memory_id": memory_id,
                "model_id": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                "embedding_model": "amazon.titan-embed-text-v1",
                "setup_date": datetime.now().isoformat(),
                "note": "Developers will create their own Knowledge Bases when ready"
            }
            
            self.save_config(config)
            
            # Success summary
            print("\n" + "="*70)
            print("✅ Infrastructure Setup Complete!")
            print("="*70)
            print("\n📋 Next Steps:")
            print("\n1. Share config.json with your team:")
            print("   - Developer 1 (Analysis Agent)")
            print("   - Developer 2 (Explanation Agent)")
            print("   - Developer 3 (Negotiation Agent)")
            print("\n2. Each developer uploads their documents to S3:")
            print(f"   Legal docs     → s3://{buckets['legal']}/")
            print(f"   Contract docs  → s3://{buckets['contracts']}/")
            print(f"   User uploads   → s3://{buckets['uploads']}/")
            print("\n3. Developers create Knowledge Bases when needed:")
            print("   - Use AWS Console or CLI")
            print("   - Point to their S3 bucket")
            print("   - Add KB ID to their agent code")
            print("\n4. Start building agents!")
            print("   - See docs/DEV*.md for implementation guides")
            print("   - Each agent uses the model: " + config['model_id'])
            print("\n" + "="*70)
            
            return config
            
        except Exception as e:
            print("\n" + "="*70)
            print("❌ Setup Failed!")
            print("="*70)
            print(f"Error: {e}")
            print("\nPlease check:")
            print("- AWS credentials are configured")
            print("- You have sufficient IAM permissions (s3:*, iam:*)")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Main entry point"""
    print("\nContractGuard AI - Simplified Infrastructure Setup")
    print("This will create S3 buckets and IAM roles in us-east-1\n")
    
    # Confirm with user
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Setup cancelled.")
        sys.exit(0)
    
    # Run setup
    infra = ContractGuardInfrastructure(region='us-east-1')
    infra.setup_all()


if __name__ == "__main__":
    main()
