# 🚀 Deploy to AgentCore Runtime

## **Step 1: Build Docker Image**
```bash
# Start Docker Desktop first
cd src/agents/analysis
docker build --platform linux/arm64 -t contractguard-analysis .
docker tag contractguard-analysis 897722703585.dkr.ecr.us-east-1.amazonaws.com/contractguard-analysis:latest
docker push 897722703585.dkr.ecr.us-east-1.amazonaws.com/contractguard-analysis:latest
```

## **Step 2: Host Agent in Console**
1. Click **"Host agent"** button
2. Enter:
   - **Name:** `contractguard-analysis`
   - **Docker URI:** `897722703585.dkr.ecr.us-east-1.amazonaws.com/contractguard-analysis:latest`
3. Click **"Host"**

Your agent will appear in the Runtime agents list when ready! ✅