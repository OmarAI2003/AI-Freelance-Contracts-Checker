# PowerShell script for deploying to AWS ECS

# Configuration
$AWS_REGION = "us-east-1"
$AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
$ECR_REPOSITORY_NAME = "negotiation-agent"
$CLUSTER_NAME = "negotiation-agent-cluster"
$SERVICE_NAME = "negotiation-agent-service"
$TASK_FAMILY = "negotiation-agent-task"
$IMAGE_TAG = "latest"

$IMAGE_URI = "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPOSITORY_NAME}:${IMAGE_TAG}"

Write-Host "🚀 Deploying Negotiation Agent to ECS Fargate..." -ForegroundColor Green
Write-Host ""

# Step 1: Create ECS Cluster
Write-Host "📦 Step 1: Creating ECS cluster..." -ForegroundColor Cyan
$clusterExists = aws ecs describe-clusters --clusters $CLUSTER_NAME --region $AWS_REGION 2>$null
if (-not $clusterExists) {
    aws ecs create-cluster `
        --cluster-name $CLUSTER_NAME `
        --region $AWS_REGION `
        --capacity-providers FARGATE FARGATE_SPOT `
        --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1
} else {
    Write-Host "✓ Cluster already exists" -ForegroundColor Yellow
}

# Step 2: Create CloudWatch Log Group
Write-Host ""
Write-Host "📝 Step 2: Creating CloudWatch log group..." -ForegroundColor Cyan
$logGroupExists = aws logs describe-log-groups --log-group-name-prefix "/ecs/$TASK_FAMILY" --region $AWS_REGION 2>$null
if (-not $logGroupExists) {
    aws logs create-log-group --log-group-name "/ecs/$TASK_FAMILY" --region $AWS_REGION
} else {
    Write-Host "✓ Log group already exists" -ForegroundColor Yellow
}

# Step 3: Create IAM role if doesn't exist
Write-Host ""
Write-Host "🔑 Step 3: Setting up IAM roles..." -ForegroundColor Cyan
$roleExists = aws iam get-role --role-name ecsTaskExecutionRole 2>$null
if (-not $roleExists) {
    $trustPolicy = @"
{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "ecs-tasks.amazonaws.com"},
        "Action": "sts:AssumeRole"
    }]
}
"@
    aws iam create-role --role-name ecsTaskExecutionRole --assume-role-policy-document $trustPolicy
}

# Attach policies
aws iam attach-role-policy --role-name ecsTaskExecutionRole --policy-arn "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy" 2>$null
aws iam attach-role-policy --role-name ecsTaskExecutionRole --policy-arn "arn:aws:iam::aws:policy/AmazonBedrockFullAccess" 2>$null

# Step 4: Check for Bearer Token
if (-not $env:AWS_BEARER_TOKEN_BEDROCK) {
    Write-Host ""
    Write-Host "⚠️  Warning: AWS_BEARER_TOKEN_BEDROCK not set" -ForegroundColor Yellow
    Write-Host "Please set it: `$env:AWS_BEARER_TOKEN_BEDROCK='your-token'" -ForegroundColor Yellow
    exit 1
}

# Step 5: Register Task Definition
Write-Host ""
Write-Host "📋 Step 4: Registering task definition..." -ForegroundColor Cyan
$taskDefinition = @"
{
  "family": "$TASK_FAMILY",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "negotiation-agent",
      "image": "$IMAGE_URI",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "AWS_REGION",
          "value": "$AWS_REGION"
        },
        {
          "name": "AWS_BEARER_TOKEN_BEDROCK",
          "value": "$env:AWS_BEARER_TOKEN_BEDROCK"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/$TASK_FAMILY",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
"@

$taskDefinition | Out-File -FilePath "task-definition.json" -Encoding UTF8
aws ecs register-task-definition --cli-input-json "file://task-definition.json" --region $AWS_REGION

# Step 6: Get VPC and subnet info
Write-Host ""
Write-Host "🌐 Step 5: Getting VPC and subnet information..." -ForegroundColor Cyan
$VPC_ID = (aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text --region $AWS_REGION)
$SUBNET_IDS = (aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[*].SubnetId" --output text --region $AWS_REGION) -replace "`t", ","

# Step 7: Create security group
Write-Host ""
Write-Host "🔒 Step 6: Creating security group..." -ForegroundColor Cyan
$sgExists = aws ec2 describe-security-groups --filters "Name=group-name,Values=negotiation-agent-sg" "Name=vpc-id,Values=$VPC_ID" --query "SecurityGroups[0].GroupId" --output text --region $AWS_REGION 2>$null
if ($sgExists -and $sgExists -ne "None") {
    $SECURITY_GROUP_ID = $sgExists
    Write-Host "✓ Security group already exists" -ForegroundColor Yellow
} else {
    $SECURITY_GROUP_ID = (aws ec2 create-security-group --group-name negotiation-agent-sg --description "Security group for negotiation agent" --vpc-id $VPC_ID --region $AWS_REGION --query 'GroupId' --output text)
}

# Allow inbound traffic on port 8000
aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP_ID --protocol tcp --port 8000 --cidr "0.0.0.0/0" --region $AWS_REGION 2>$null

# Step 8: Create or update service
Write-Host ""
Write-Host "🎯 Step 7: Creating/Updating ECS service..." -ForegroundColor Cyan
$serviceExists = aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $AWS_REGION 2>$null | Select-String "ACTIVE"
if ($serviceExists) {
    aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --task-definition $TASK_FAMILY --force-new-deployment --region $AWS_REGION
} else {
    aws ecs create-service `
        --cluster $CLUSTER_NAME `
        --service-name $SERVICE_NAME `
        --task-definition $TASK_FAMILY `
        --desired-count 1 `
        --launch-type FARGATE `
        --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}" `
        --region $AWS_REGION
}

Write-Host ""
Write-Host "✅ ECS Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Cluster: $CLUSTER_NAME" -ForegroundColor Yellow
Write-Host "Service: $SERVICE_NAME" -ForegroundColor Yellow
Write-Host "Task Definition: $TASK_FAMILY" -ForegroundColor Yellow
Write-Host ""
Write-Host "⏳ Waiting for service to stabilize (this may take 2-3 minutes)..." -ForegroundColor Cyan
Write-Host ""

# Wait for service to be stable
aws ecs wait services-stable --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $AWS_REGION

# Get the public IP
Write-Host ""
Write-Host "🔍 Getting public endpoint..." -ForegroundColor Cyan
$TASK_ARN = (aws ecs list-tasks --cluster $CLUSTER_NAME --service-name $SERVICE_NAME --region $AWS_REGION --query 'taskArns[0]' --output text)

if ($TASK_ARN -and $TASK_ARN -ne "None") {
    $ENI_ID = (aws ecs describe-tasks --cluster $CLUSTER_NAME --tasks $TASK_ARN --region $AWS_REGION --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text)
    
    $PUBLIC_IP = (aws ec2 describe-network-interfaces --network-interface-ids $ENI_ID --region $AWS_REGION --query 'NetworkInterfaces[0].Association.PublicIp' --output text)
    
    Write-Host ""
    Write-Host "🎉 Deployment successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "API Endpoint: http://${PUBLIC_IP}:8000" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Test the API:" -ForegroundColor Cyan
    Write-Host "curl http://${PUBLIC_IP}:8000/health" -ForegroundColor White
    Write-Host ""
    Write-Host "Share this endpoint with your friend for integration!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "⚠️  Could not get task information. Service may still be starting." -ForegroundColor Yellow
    Write-Host "Run the following command in a few minutes to get the endpoint:" -ForegroundColor Yellow
}
