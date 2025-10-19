# AWS Deployment Architecture - Freelancer Legal Assistant
## Production-Ready Multi-Agent System with A2A Protocol

> **AWS Hackathon Optimized Architecture**  
> Following AWS Well-Architected Framework Best Practices

---

## 🏗️ Architecture Overview

```
                           ┌─────────────────────────────────────┐
                           │      Amazon CloudFront (CDN)        │
                           │  • Global edge locations            │
                           │  • SSL/TLS termination             │
                           │  • DDoS protection                 │
                           └──────────────┬──────────────────────┘
                                          │
                           ┌──────────────▼──────────────────────┐
                           │      Amazon S3 (Static Hosting)     │
                           │  • index.html                       │
                           │  • static/css/styles.css            │
                           │  • static/js/app.js                 │
                           └──────────────┬──────────────────────┘
                                          │
                                          │ API Calls
                           ┌──────────────▼──────────────────────┐
                           │   API Gateway (REST API)            │
                           │  • /api/chat                        │
                           │  • /api/upload                      │
                           │  • /api/health                      │
                           │  • Rate limiting, throttling        │
                           │  • API keys, CORS                   │
                           └──────────────┬──────────────────────┘
                                          │
                           ┌──────────────▼──────────────────────┐
                           │   AWS Lambda (Orchestrator)         │
                           │  • Python 3.13 runtime              │
                           │  • Intent classification            │
                           │  • Agent routing logic              │
                           │  • A2A communication                │
                           │  • VPC enabled for security         │
                           └──────────────┬──────────────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    │                     │                     │
         ┌──────────▼───────┐  ┌─────────▼────────┐  ┌────────▼──────────┐
         │ DynamoDB Table   │  │  Amazon S3        │  │ Bedrock Agent     │
         │ (Session Memory) │  │  (File Storage)   │  │  Runtime          │
         │ • Conversations  │  │  • Uploads        │  │  • Action Agent✅ │
         │ • User context   │  │  • Contracts      │  │  • Analysis      │
         │ • Agent states   │  │  • Documents      │  │  • Explanation   │
         │ • TTL: 30 days   │  │  • Lifecycle mgmt │  │  • Negotiation   │
         └──────────────────┘  └───────────────────┘  └───────────────────┘
                                          │
                           ┌──────────────▼──────────────────────┐
                           │   AWS Textract (Optional)           │
                           │  • PDF/Image text extraction        │
                           │  • Contract parsing                 │
                           └─────────────────────────────────────┘
```

---

## 📦 AWS Services Used

### Core Services
1. **Amazon S3** - Static website hosting
2. **Amazon CloudFront** - CDN and SSL
3. **API Gateway** - REST API endpoints
4. **AWS Lambda** - Orchestrator function
5. **Amazon DynamoDB** - Session/memory storage
6. **AWS Bedrock AgentCore** - Agent runtime

### Supporting Services
7. **AWS IAM** - Permissions and roles
8. **AWS CloudWatch** - Logging and monitoring
9. **AWS X-Ray** - Distributed tracing
10. **AWS Secrets Manager** - API keys and credentials
11. **AWS Textract** - Document text extraction (optional)
12. **Amazon Cognito** - User authentication (future)

---

## 🚀 Deployment Steps

### Phase 1: Static Frontend (S3 + CloudFront)

#### Step 1: Create S3 Bucket for Static Hosting
```bash
# Create bucket
aws s3 mb s3://freelancer-legal-assistant-frontend --region us-east-1

# Enable static website hosting
aws s3 website s3://freelancer-legal-assistant-frontend \
    --index-document index.html \
    --error-document index.html

# Upload static files
cd d:\aws_hackathon\src\frontend
aws s3 sync . s3://freelancer-legal-assistant-frontend \
    --exclude "*.py" \
    --exclude "*.txt" \
    --exclude "__pycache__/*" \
    --exclude "uploads/*"
```

#### Step 2: Create CloudFront Distribution
```bash
# Create distribution (use CloudFormation template below)
aws cloudformation deploy \
    --template-file cloudfront-stack.yaml \
    --stack-name freelancer-legal-assistant-cdn \
    --parameter-overrides S3BucketName=freelancer-legal-assistant-frontend
```

### Phase 2: Backend API (Lambda + API Gateway)

#### Step 3: Package Lambda Function
```bash
cd d:\aws_hackathon\src\lambda
pip install -r requirements.txt -t package/
cp orchestrator_lambda.py package/
cd package
zip -r ../orchestrator.zip .
cd ..
zip -g orchestrator.zip orchestrator_lambda.py
```

#### Step 4: Deploy Lambda Function
```bash
aws lambda create-function \
    --function-name FreelancerLegalAssistantOrchestrator \
    --runtime python3.13 \
    --role arn:aws:iam::897722703585:role/FreelancerOrchestratorRole \
    --handler orchestrator_lambda.lambda_handler \
    --zip-file fileb://orchestrator.zip \
    --timeout 30 \
    --memory-size 512 \
    --environment Variables="{
        DYNAMODB_TABLE=freelancer-sessions,
        S3_UPLOADS_BUCKET=freelancer-uploads,
        ACTION_AGENT_ARN=arn:aws:bedrock-agentcore:us-east-1:897722703585:runtime/freelancer_action_agent-Q83Rk73nkD
    }"
```

#### Step 5: Create API Gateway
```bash
# Create REST API
aws apigateway create-rest-api \
    --name "FreelancerLegalAssistantAPI" \
    --description "API for Freelancer Legal Assistant" \
    --endpoint-configuration types=REGIONAL

# Create resources and methods (see API Gateway CloudFormation template)
```

### Phase 3: Data Storage (DynamoDB + S3)

#### Step 6: Create DynamoDB Table
```bash
aws dynamodb create-table \
    --table-name freelancer-sessions \
    --attribute-definitions \
        AttributeName=sessionId,AttributeType=S \
        AttributeName=timestamp,AttributeType=N \
    --key-schema \
        AttributeName=sessionId,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES \
    --tags Key=Project,Value=FreelancerLegalAssistant Key=Environment,Value=Production
```

#### Step 7: Create S3 Bucket for Uploads
```bash
aws s3 mb s3://freelancer-uploads-897722703585 --region us-east-1

# Configure lifecycle policy (auto-delete after 30 days)
aws s3api put-bucket-lifecycle-configuration \
    --bucket freelancer-uploads-897722703585 \
    --lifecycle-configuration file://s3-lifecycle.json
```

---

## 🔧 AWS Resources to Create

### 1. CloudFormation Template - Complete Infrastructure
Save as: `d:\aws_hackathon\aws\cloudformation\main-stack.yaml`

### 2. Lambda Function - Orchestrator with A2A
Save as: `d:\aws_hackathon\src\lambda\orchestrator_lambda.py`

### 3. IAM Roles and Policies
Required roles:
- Lambda execution role (with DynamoDB, S3, Bedrock permissions)
- API Gateway invocation role
- CloudFront OAI for S3 access

### 4. API Gateway Configuration
Endpoints:
- `POST /api/chat` → Lambda
- `POST /api/upload` → Lambda → S3
- `GET /api/health` → Lambda

---

## 🔐 Security Best Practices

### 1. IAM Least Privilege
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock-agent-runtime:InvokeAgent",
        "bedrock:InvokeModel"
      ],
      "Resource": [
        "arn:aws:bedrock-agentcore:us-east-1:897722703585:runtime/freelancer_action_agent-*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:UpdateItem"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:897722703585:table/freelancer-sessions"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::freelancer-uploads-897722703585/*"
    }
  ]
}
```

### 2. API Gateway Security
- API Keys for rate limiting
- CORS configuration
- Request validation
- Throttling (10,000 requests/second burst)

### 3. Encryption
- S3: Server-side encryption (SSE-S3)
- DynamoDB: Encryption at rest
- CloudFront: TLS 1.2+ only
- Secrets Manager: For API keys

### 4. Monitoring
- CloudWatch Logs for all Lambda invocations
- X-Ray tracing for distributed debugging
- CloudWatch Alarms for errors/latency
- CloudWatch Dashboards

---

## 💰 Cost Optimization

### Estimated Monthly Costs (Moderate Usage)

| Service | Usage | Est. Cost |
|---------|-------|-----------|
| S3 (Frontend) | 10 GB storage, 100K requests | $1 |
| CloudFront | 100 GB transfer | $8.50 |
| API Gateway | 1M requests | $3.50 |
| Lambda | 1M invocations, 512 MB | $4 |
| DynamoDB | 10M read/write units | $2.50 |
| Bedrock AgentCore | 1M tokens | ~$50 |
| **Total** | | **~$70/month** |

### Cost Optimization Tips
1. Use CloudFront caching (reduce API calls)
2. DynamoDB on-demand pricing (pay per use)
3. Lambda memory optimization (right-size)
4. S3 Intelligent-Tiering (automatic cost savings)
5. CloudWatch Logs retention (7 days for dev, 30 days for prod)

---

## 📊 Monitoring & Observability

### CloudWatch Dashboard
Metrics to track:
- Lambda invocation count/errors/duration
- API Gateway 4xx/5xx errors
- DynamoDB read/write capacity
- Bedrock agent invocation latency
- S3 request rates

### Alarms
1. **Lambda Errors** > 10 in 5 minutes
2. **API Gateway 5xx** > 1% error rate
3. **DynamoDB Throttles** > 0
4. **Bedrock Agent Failures** > 5%

### X-Ray Tracing
Enable for:
- Lambda function
- API Gateway
- DynamoDB calls
- Bedrock agent calls

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
```yaml
name: Deploy to AWS

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Deploy Frontend to S3
        run: |
          cd src/frontend
          aws s3 sync . s3://freelancer-legal-assistant-frontend \
            --exclude "*.py" --delete
      
      - name: Deploy Lambda Function
        run: |
          cd src/lambda
          ./package.sh
          aws lambda update-function-code \
            --function-name FreelancerLegalAssistantOrchestrator \
            --zip-file fileb://orchestrator.zip
      
      - name: Invalidate CloudFront Cache
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.CLOUDFRONT_DIST_ID }} \
            --paths "/*"
```

---

## 🎯 Next Steps

1. ✅ Create CloudFormation templates (I'll generate these next)
2. ✅ Create Lambda orchestrator function with A2A
3. ✅ Deploy to AWS
4. ✅ Test end-to-end with real Action Agent
5. ✅ Add teammates' agents when ready
6. ✅ Setup monitoring and alarms
7. ✅ Create demo environment

---

**Ready to deploy?** Let's create the actual implementation files!
