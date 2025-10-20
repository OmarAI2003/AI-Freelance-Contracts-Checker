# 🚀 Quick Start - Deploy in 5 Minutes

## What You'll Do
Deploy your Negotiation Agent API to AWS so your friend can integrate it with the website.

## Prerequisites Checklist
- [ ] Docker Desktop installed and running
- [ ] AWS CLI installed (`aws --version`)
- [ ] AWS credentials configured (`aws configure`)
- [ ] Claude 3 model enabled in AWS Bedrock Console

## Step-by-Step

### 1. Open PowerShell and Navigate to Project
```powershell
cd "d:\Activites & Competitions\AWS Hack\AI-Freelance-Contracts-Checker\src\agents\negotiation"
```

### 2. Set Your Bearer Token
```powershell
# Load from .env file
Get-Content .env | ForEach-Object {
    if ($_ -match 'AWS_BEARER_TOKEN_BEDROCK=(.+)') {
        $env:AWS_BEARER_TOKEN_BEDROCK = $matches[1]
    }
}

# Verify it's set
echo $env:AWS_BEARER_TOKEN_BEDROCK
```

### 3. Deploy to ECR (2-5 minutes)
```powershell
.\deploy-ecr.ps1
```

Wait for: ✅ Deployment to ECR complete!

### 4. Deploy to ECS (3-5 minutes)
```powershell
.\deploy-ecs.ps1
```

Wait for the endpoint to appear:
```
🎉 Deployment successful!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API Endpoint: http://54.123.45.67:8000
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5. Test the API
```powershell
# Replace with your actual IP
$API = "http://54.123.45.67:8000"

# Test it works
curl "$API/health"
```

### 6. Share with Your Friend
Send them:
- **Endpoint**: `http://YOUR_IP:8000`
- **Documentation**: Show them [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md ) (JavaScript integration examples)

## That's It! 🎉

Your agent is now running on AWS and ready for integration.

## What's Running?
- ✅ Docker container with your agent
- ✅ Running on AWS ECS Fargate
- ✅ Publicly accessible API
- ✅ 4 endpoints: /analyze, /explain, /negotiate, /legal-advice

## Costs
- **~$40-60/month** for 24/7 operation
- **Stop when not in use** to save money:
  ```powershell
  aws ecs update-service --cluster negotiation-agent-cluster --service negotiation-agent-service --desired-count 0
  ```

## Troubleshooting
- **Script fails?** → Check [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md ) Troubleshooting section
- **No endpoint?** → Wait 2-3 minutes and run `.\deploy-ecs.ps1` again
- **Connection fails?** → Check security group allows port 8000

## Need More Help?
Read the full guide: [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md )
