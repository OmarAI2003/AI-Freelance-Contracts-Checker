# 🚀 Deploying Negotiation Agent to AWS (Container Method)

This guide explains how to deploy your Negotiation Agent API to AWS using Docker containers on ECS Fargate.

## 📋 Prerequisites

Before starting, make sure you have:

1. **Docker Desktop** installed and running
   - Download from: https://www.docker.com/products/docker-desktop

2. **AWS CLI** installed and configured
   ```bash
   # Check if installed
   aws --version
   
   # Configure (if not already done)
   aws configure
   ```

3. **AWS Account** with these permissions:
   - Amazon ECS (Elastic Container Service)
   - Amazon ECR (Elastic Container Registry)
   - IAM (Identity and Access Management)
   - EC2 (for VPC and Security Groups)
   - CloudWatch Logs

4. **AWS Bedrock Token** from your `.env` file
   - Make sure `AWS_BEARER_TOKEN_BEDROCK` is set

5. **Claude 3 Model Access** enabled in AWS Bedrock Console
   - Go to: AWS Console → Bedrock → Model access
   - Enable "Claude 3 Sonnet" or "Claude 3.5 Sonnet"

## 🎯 Deployment Overview

```
Your Code → Docker Image → AWS ECR → ECS Fargate → Public Endpoint
```

## 📝 Step-by-Step Deployment

### Step 1: Test Locally First (Optional but Recommended)

```powershell
# Navigate to the negotiation folder
cd "d:\Activites & Competitions\AWS Hack\AI-Freelance-Contracts-Checker\src\agents\negotiation"

# Build the Docker image
docker build -t negotiation-agent:latest .

# Run locally to test
docker run -p 8000:8000 `
    -e AWS_REGION=us-east-1 `
    -e AWS_BEARER_TOKEN_BEDROCK=$env:AWS_BEARER_TOKEN_BEDROCK `
    negotiation-agent:latest

# In another terminal, test the API
curl http://localhost:8000/health
curl http://localhost:8000/

# Stop with Ctrl+C when done testing
```

### Step 2: Set Environment Variable

```powershell
# Set your Bedrock token (get from .env file)
$env:AWS_BEARER_TOKEN_BEDROCK = "your-token-here"

# Or load from .env file
Get-Content .env | ForEach-Object {
    if ($_ -match 'AWS_BEARER_TOKEN_BEDROCK=(.+)') {
        $env:AWS_BEARER_TOKEN_BEDROCK = $matches[1]
    }
}
```

### Step 3: Deploy to ECR (Elastic Container Registry)

```powershell
# Run the ECR deployment script
.\deploy-ecr.ps1
```

This will:
- ✅ Create ECR repository
- ✅ Build Docker image
- ✅ Push image to AWS

**Expected output:**
```
🚀 Starting deployment to AWS ECR...
📦 Step 1: Creating ECR repository...
🔐 Step 2: Authenticating Docker to ECR...
🏗️  Step 3: Building Docker image...
🏷️  Step 4: Tagging Docker image...
⬆️  Step 5: Pushing image to ECR...
✅ Deployment to ECR complete!

Image URI: 123456789.dkr.ecr.us-east-1.amazonaws.com/negotiation-agent:latest
```

### Step 4: Deploy to ECS (Elastic Container Service)

```powershell
# Run the ECS deployment script
.\deploy-ecs.ps1
```

This will:
- ✅ Create ECS cluster
- ✅ Create CloudWatch log group
- ✅ Set up IAM roles
- ✅ Create task definition
- ✅ Create security group
- ✅ Deploy the service
- ✅ Get public endpoint

**Expected output:**
```
🚀 Deploying Negotiation Agent to ECS Fargate...
📦 Step 1: Creating ECS cluster...
📝 Step 2: Creating CloudWatch log group...
🔑 Step 3: Setting up IAM roles...
📋 Step 4: Registering task definition...
🌐 Step 5: Getting VPC and subnet information...
🔒 Step 6: Creating security group...
🎯 Step 7: Creating/Updating ECS service...
✅ ECS Deployment complete!
⏳ Waiting for service to stabilize...

🎉 Deployment successful!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API Endpoint: http://54.123.45.67:8000
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Test the API:
curl http://54.123.45.67:8000/health
```

### Step 5: Test Your Deployed API

```powershell
# Replace with your actual public IP
$API_ENDPOINT = "http://54.123.45.67:8000"

# Test health endpoint
curl "$API_ENDPOINT/health"

# Test analyze endpoint
curl -X POST "$API_ENDPOINT/analyze" `
    -H "Content-Type: application/json" `
    -d '{"contract_text": "Payment terms: Net 90 days at $40/hour"}'

# Test explain endpoint  
curl -X POST "$API_ENDPOINT/explain" `
    -H "Content-Type: application/json" `
    -d '{"terms": "indemnification clause"}'
```

## 🌐 Integration with Website

Share this information with your friend:

### API Endpoint
```
http://YOUR_PUBLIC_IP:8000
```

### Available Endpoints

1. **GET /** - API information
2. **GET /health** - Health check
3. **POST /analyze** - Analyze contract
4. **POST /explain** - Explain terms
5. **POST /negotiate** - Generate negotiation strategy
6. **POST /legal-advice** - Get legal guidance

### JavaScript Integration Example

```javascript
const API_BASE_URL = "http://54.123.45.67:8000";

// Analyze Contract
async function analyzeContract(contractText) {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contract_text: contractText })
    });
    return await response.json();
}

// Explain Terms
async function explainTerms(terms) {
    const response = await fetch(`${API_BASE_URL}/explain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ terms: terms })
    });
    return await response.json();
}

// Negotiate Terms
async function negotiateTerms(currentTerms, desiredChanges, context) {
    const response = await fetch(`${API_BASE_URL}/negotiate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            current_terms: currentTerms,
            desired_changes: desiredChanges,
            context: context
        })
    });
    return await response.json();
}

// Get Legal Advice
async function getLegalAdvice(contractText, question) {
    const response = await fetch(`${API_BASE_URL}/legal-advice`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            contract_text: contractText,
            question: question
        })
    });
    return await response.json();
}
```

## 📊 Monitoring

### View Logs
```powershell
# View CloudWatch logs
aws logs tail /ecs/negotiation-agent-task --follow
```

### Check Service Status
```powershell
aws ecs describe-services `
    --cluster negotiation-agent-cluster `
    --services negotiation-agent-service
```

### Get Task Details
```powershell
# List running tasks
aws ecs list-tasks `
    --cluster negotiation-agent-cluster `
    --service-name negotiation-agent-service

# Describe specific task
aws ecs describe-tasks `
    --cluster negotiation-agent-cluster `
    --tasks TASK_ARN_HERE
```

## 🔄 Update Deployment

To update your agent with new code:

```powershell
# 1. Build and push new image
.\deploy-ecr.ps1

# 2. Force new deployment
aws ecs update-service `
    --cluster negotiation-agent-cluster `
    --service negotiation-agent-service `
    --force-new-deployment
```

## 💰 Cost Estimation

### ECS Fargate Costs
- **CPU**: $0.04048 per vCPU per hour
- **Memory**: $0.004445 per GB per hour
- **Your configuration** (1 vCPU, 2GB RAM): ~$0.05/hour = ~$36/month

### Data Transfer
- **First 100 GB/month**: Free
- **After 100 GB**: $0.09/GB

### ECR Storage
- **$0.10 per GB/month**

**Total estimated cost**: $40-60/month for 24/7 operation

## 🛑 Stopping the Service (to save costs)

```powershell
# Stop the service (keeps everything but stops running tasks)
aws ecs update-service `
    --cluster negotiation-agent-cluster `
    --service negotiation-agent-service `
    --desired-count 0

# Start again when needed
aws ecs update-service `
    --cluster negotiation-agent-cluster `
    --service negotiation-agent-service `
    --desired-count 1
```

## 🗑️ Complete Cleanup

To delete all resources:

```powershell
# Delete service
aws ecs delete-service `
    --cluster negotiation-agent-cluster `
    --service negotiation-agent-service `
    --force

# Delete cluster
aws ecs delete-cluster --cluster negotiation-agent-cluster

# Delete ECR repository
aws ecr delete-repository --repository-name negotiation-agent --force

# Delete security group (get ID first)
$SG_ID = (aws ec2 describe-security-groups --filters "Name=group-name,Values=negotiation-agent-sg" --query "SecurityGroups[0].GroupId" --output text)
aws ec2 delete-security-group --group-id $SG_ID

# Delete log group
aws logs delete-log-group --log-group-name /ecs/negotiation-agent-task
```

## ❓ Troubleshooting

### Container won't start
1. Check CloudWatch logs: `aws logs tail /ecs/negotiation-agent-task --follow`
2. Verify environment variables are set correctly
3. Test Docker image locally first

### Can't connect to API
1. Check security group allows port 8000 from 0.0.0.0/0
2. Verify task has public IP assigned
3. Check if service is running: `aws ecs describe-services --cluster negotiation-agent-cluster --services negotiation-agent-service`

### AWS_BEARER_TOKEN_BEDROCK not working
1. Verify token is valid in `.env` file
2. Make sure environment variable is set before running deploy-ecs.ps1
3. Check CloudWatch logs for authentication errors

### High AWS costs
1. Scale down to 0 when not in use
2. Use Fargate Spot for non-production (50-70% cheaper)
3. Reduce CPU/memory if possible
4. Set up auto-scaling to scale down during low traffic

## 📚 Additional Resources

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [AWS ECR Documentation](https://docs.aws.amazon.com/ecr/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)

## ✅ Next Steps

1. ✅ Deploy the agent
2. ✅ Get the public endpoint
3. ✅ Share with your friend
4. ✅ Test all 4 endpoints
5. ⭐ (Optional) Set up custom domain with Route 53
6. ⭐ (Optional) Add HTTPS with Application Load Balancer
7. ⭐ (Optional) Implement authentication
8. ⭐ (Optional) Set up CI/CD with GitHub Actions

---

**Need help?** Check the troubleshooting section or review CloudWatch logs!
