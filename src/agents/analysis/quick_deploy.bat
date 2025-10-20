@echo off
echo Building and pushing ARM64 image...
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 897722703585.dkr.ecr.us-east-1.amazonaws.com
docker build --platform linux/arm64 -t contractguard-analysis .
docker tag contractguard-analysis 897722703585.dkr.ecr.us-east-1.amazonaws.com/contractguard-analysis:latest
docker push 897722703585.dkr.ecr.us-east-1.amazonaws.com/contractguard-analysis:latest
echo Done! Go test in AgentCore console.