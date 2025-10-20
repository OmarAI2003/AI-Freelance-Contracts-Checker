# AWS Integration Setup

This project uses several AWS services to enhance its functionality:

1. Amazon Bedrock - For LLM access (Claude 3 Sonnet)
2. Amazon DynamoDB - For storing market rates and case law data
3. Amazon S3 - For storing contract documents and analysis reports

## Prerequisites

1. AWS Account with appropriate permissions
2. AWS CLI installed and configured
3. Python 3.8+
4. Required Python packages (install using `pip install -r requirements.txt`)

## AWS Services Setup

1. First, ensure you have AWS credentials configured:
   ```bash
   aws configure
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the infrastructure setup script:
   ```bash
   python setup_infrastructure.py
   ```

This will create:
- DynamoDB tables for market rates and case law
- S3 bucket for document storage
- Configure Bedrock access for Claude

## Environment Variables

Create a `.env` file in your project root with the following:

```env
AWS_REGION=us-east-1  # or your preferred region
AWS_PROFILE=default   # or your AWS profile name
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229
S3_BUCKET_NAME=freelance-contract-documents
MARKET_RATES_TABLE=freelance_market_rates
CASE_LAW_TABLE=freelance_case_law
```

## Data Loading

Initial data loading scripts are provided in the `setup/aws/data` directory. To load sample data:

```bash
python load_market_rates.py
python load_case_law.py
```

## Security Considerations

1. Ensure proper IAM roles and permissions
2. Enable encryption for sensitive data
3. Regular security audits and updates
4. Monitor AWS CloudWatch for usage patterns

## Cost Management

1. Use AWS Cost Explorer to monitor usage
2. Set up billing alerts
3. Consider reserved capacity for DynamoDB if usage is predictable
4. Monitor S3 storage and lifecycle policies

## Troubleshooting

1. Check AWS CloudWatch logs for errors
2. Verify IAM permissions
3. Ensure environment variables are set correctly
4. Check AWS service quotas and limits