# AWS Deployment Guide

## 🎯 Quick Start

Deploy everything with one command:

```powershell
cd d:\aws_hackathon
.\aws\deploy.ps1
```

This will:
1. ✅ Package Lambda function with dependencies
2. ✅ Deploy CloudFormation stack (S3, Lambda, API Gateway, CloudFront)
3. ✅ Update Lambda code
4. ✅ Deploy frontend to S3
5. ✅ Invalidate CloudFront cache
6. ✅ Test deployment

## 📦 What Gets Deployed

### Infrastructure (CloudFormation)
- **S3 Buckets**: Frontend hosting + file uploads
- **Lambda Function**: Orchestrator with A2A protocol
- **API Gateway**: HTTP API for chat, health, upload endpoints
- **CloudFront**: CDN for global distribution
- **IAM Roles**: Lambda execution with Bedrock permissions
- **CloudWatch**: Logs and alarms

### No DynamoDB! 🎉
We're using **Bedrock AgentCore's built-in session memory** instead of DynamoDB tables. This simplifies:
- Architecture (fewer moving parts)
- Cost (no DynamoDB charges)
- Development (no manual session management)
- Maintenance (AgentCore handles everything)

## 🔑 Key Features

### A2A Communication
The orchestrator uses Agent-to-Agent protocol to communicate with Bedrock AgentCore agents:

```python
response = bedrock_agent_runtime.invoke_agent(
    agentId=agent_id,
    sessionId=session_id,  # AgentCore remembers context!
    inputText=message,
    enableTrace=True
)
```

### Built-in Memory
AgentCore automatically maintains conversation memory:
- No manual context building
- No DynamoDB queries
- Just pass the same `sessionId` for continuity

### Intent Classification
Automatic routing based on keywords:
- "analyze contract" → Analysis Agent
- "what does mean" → Explanation Agent  
- "negotiate terms" → Negotiation Agent
- "won't pay" → Action Agent ✅ (DEPLOYED!)

## 📊 Architecture

```
Internet
    ↓
CloudFront (CDN)
    ↓
S3 (Frontend)  ←→  API Gateway
                       ↓
                   Lambda (Orchestrator)
                       ↓
                   Bedrock AgentCore
                   - Action Agent ✅
                   - Analysis Agent ⏳
                   - Explanation Agent ⏳
                   - Negotiation Agent ⏳
```

## 🚀 Deployment Steps

### Prerequisites
```powershell
# Verify AWS credentials
aws sts get-caller-identity

# Expected output:
# Account: 897722703585
# UserId: AIDAR...
# Arn: arn:aws:iam::897722703585:user/Moustafa
```

### Deploy
```powershell
cd d:\aws_hackathon
.\aws\deploy.ps1
```

### What Happens
1. **Lambda Package** (~30 seconds)
   - Installs boto3
   - Creates deployment ZIP

2. **CloudFormation** (~5-10 minutes)
   - Creates all AWS resources
   - Sets up IAM permissions
   - Configures networking

3. **Lambda Deploy** (~10 seconds)
   - Updates function code
   - Configures environment variables

4. **Frontend Deploy** (~20 seconds)
   - Syncs files to S3
   - Updates API URL
   - Sets content types

5. **Cache Invalidation** (~5 seconds)
   - Clears CloudFront cache

6. **Testing** (~10 seconds)
   - Lambda health check
   - API Gateway test

**Total time**: ~10 minutes

## 🧪 Testing

### Test Locally First
```powershell
cd src\frontend
python quick_start.py
# Visit http://localhost:5000
```

### Test Production
After deployment, test at your CloudFront URL:

```
Try these messages:
1. "My client won't pay me" → Action Agent (REAL!)
2. "Can you review this contract?" → Analysis Agent (Dummy)
3. "What does indemnification mean?" → Explanation Agent (Dummy)
4. "I want to negotiate payment terms" → Negotiation Agent (Dummy)
```

### Health Check
```powershell
# Lambda
aws lambda invoke `
  --function-name freelancer-legal-assistant-orchestrator `
  --payload '{"httpMethod":"GET","path":"/api/health"}' `
  response.json
cat response.json

# API Gateway
$API_URL = "https://your-api-id.execute-api.us-east-1.amazonaws.com"
Invoke-WebRequest "$API_URL/api/health"
```

## 📝 Post-Deployment

### View Logs
```powershell
aws logs tail /aws/lambda/freelancer-legal-assistant-orchestrator --follow
```

### Update Lambda Code
```powershell
cd src\lambda
# Make changes to orchestrator_lambda.py
# Then redeploy:
.\..\..\aws\deploy.ps1
```

### Update Frontend
```powershell
cd src\frontend
# Make changes to HTML/CSS/JS
# Then sync:
$BUCKET = "freelancer-legal-assistant-frontend-897722703585"
aws s3 sync . s3://$BUCKET/ --exclude "*.py" --exclude "*.txt"

# Invalidate CloudFront
$DIST_ID = "YOUR_DISTRIBUTION_ID"
aws cloudfront create-invalidation --distribution-id $DIST_ID --paths "/*"
```

### Add Teammate Agents
When Dev 1, 2, or 3 deploy their agents:

```powershell
# Update Lambda environment variables
aws lambda update-function-configuration `
  --function-name freelancer-legal-assistant-orchestrator `
  --environment Variables="{
    S3_UPLOADS_BUCKET=freelancer-legal-assistant-uploads-897722703585,
    ACTION_AGENT_ARN=arn:aws:bedrock-agentcore:us-east-1:897722703585:runtime/freelancer_action_agent-Q83Rk73nkD,
    ANALYSIS_AGENT_ARN=arn:aws:bedrock-agentcore:us-east-1:897722703585:runtime/analysis_agent-XXXXX,
    EXPLANATION_AGENT_ARN=arn:aws:bedrock-agentcore:us-east-1:897722703585:runtime/explanation_agent-XXXXX,
    NEGOTIATION_AGENT_ARN=arn:aws:bedrock-agentcore:us-east-1:897722703585:runtime/negotiation_agent-XXXXX
  }"
```

## 🔍 Monitoring

### CloudWatch Dashboard
```powershell
# View metrics in AWS Console:
# CloudWatch → Dashboards → freelancer-legal-assistant
```

Key metrics:
- **Lambda Invocations**: How many requests
- **Lambda Errors**: Should be < 1%
- **Lambda Duration**: Target < 5 seconds
- **API Gateway 4xx**: Client errors
- **API Gateway 5xx**: Server errors (should be 0)

### Alarms
Pre-configured alarms will trigger when:
- Lambda errors > 10 in 5 minutes
- API Gateway 5xx errors > 5 in 5 minutes

### X-Ray Tracing
View distributed traces:
```powershell
# AWS Console → X-Ray → Traces
# See full request flow: API Gateway → Lambda → Bedrock
```

## 💰 Cost Breakdown

**Monthly estimate (moderate usage):**
- S3: $1 (1GB storage, 10K requests)
- CloudFront: $8.50 (1GB transfer, 10K requests)
- API Gateway: $3.50 (1M requests)
- Lambda: $4 (100K invocations @ 512MB, 5s avg)
- Bedrock: ~$50 (10K agent invocations @ $0.005 each)
- **Total: ~$67/month**

**Free tier benefits:**
- Lambda: First 1M requests free
- API Gateway: First 1M requests free
- CloudFront: 1TB free for 12 months

## 🛠️ Troubleshooting

### "Stack already exists" Error
```powershell
# Update instead of create
aws cloudformation update-stack --stack-name freelancer-legal-assistant-stack ...
```

### "Access Denied" on Bedrock
Check Lambda IAM role has:
```json
{
  "Effect": "Allow",
  "Action": ["bedrock:InvokeAgent"],
  "Resource": "arn:aws:bedrock-agentcore:us-east-1:897722703585:runtime/*"
}
```

### "CORS Error" in Browser
Verify API Gateway CORS settings:
- AllowOrigins: `*`
- AllowMethods: `GET, POST, OPTIONS`
- AllowHeaders: `*`

### Lambda Timeout
Increase timeout in CloudFormation:
```yaml
Timeout: 60  # seconds
```

### Cold Start Performance
Add CloudWatch Events to keep warm:
```powershell
# Ping Lambda every 5 minutes
aws events put-rule --schedule-expression "rate(5 minutes)" --name keep-lambda-warm
```

## 🔒 Security Notes

### Current Setup (Development)
- ✅ CORS: Allows all origins (`*`)
- ✅ HTTPS: Enforced via CloudFront
- ✅ IAM: Least privilege for Lambda
- ✅ Encryption: S3 SSE-AES256

### Production Hardening
1. **Restrict CORS**: Set specific domain
2. **Add WAF**: AWS WAF on CloudFront
3. **Add Cognito**: User authentication
4. **Add API Keys**: Rate limiting per user
5. **Add Secrets Manager**: For sensitive config

## 📚 Resources

### AWS Documentation
- [Bedrock AgentCore](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/)

### Project Files
- Lambda code: `src/lambda/orchestrator_lambda.py`
- CloudFormation: `aws/cloudformation/main-stack.yaml`
- Frontend: `src/frontend/`
- Deployment script: `aws/deploy.ps1`

## 🎓 Hackathon Tips

### Presentation Points
✅ **A2A Protocol**: "We implemented Agent-to-Agent communication for bonus points!"
✅ **Built-in Memory**: "Using Bedrock AgentCore's native session management - no external DB needed!"
✅ **Unified Interface**: "Single chat interface routing to 4 specialist agents"
✅ **AWS Best Practices**: "Serverless, CDN, monitoring, cost-optimized"

### Demo Flow
1. Show CloudFront URL (live!)
2. Upload contract document
3. Test Action Agent: "My client won't pay me"
4. Show CloudWatch logs (real-time!)
5. Explain architecture diagram
6. Highlight cost efficiency (~$70/month)

### Team Coordination
- Share your CloudFront URL with teammates
- Coordinate agent ARN exchange
- Test A2A integration together
- Prepare unified presentation

## 🚀 Next Steps

1. ✅ Deploy with `.\aws\deploy.ps1`
2. ⏳ Test at CloudFront URL
3. ⏳ Monitor CloudWatch logs
4. ⏳ Coordinate with teammates
5. ⏳ Prepare demo script
6. ⏳ Win the hackathon! 🏆

Good luck! 🎉
