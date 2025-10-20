# PowerShell script for deploying to AWS ECS Fargate

# Configuration
$AWS_REGION = "us-east-1"
$AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
$ECR_REPOSITORY_NAME = "negotiation-agent"
$IMAGE_TAG = "latest"
$CLUSTER_NAME = "negotiation-agent-cluster"
$SERVICE_NAME = "negotiation-agent-service"
$TASK_FAMILY = "negotiation-agent-task"
$CONTAINER_NAME = "negotiation-agent"
$LOG_GROUP = "/ecs/negotiation-agent-task"

# Get bearer token from environment
$BEARER_TOKEN = $env:AWS_BEARER_TOKEN_BEDROCK
if (-not $BEARER_TOKEN) {
    Write-Host "ERROR: AWS_BEARER_TOKEN_BEDROCK not set!" -ForegroundColor Red
    Write-Host "Please set it first:" -ForegroundColor Yellow
    Write-Host '$env:AWS_BEARER_TOKEN_BEDROCK = "your-token-here"' -ForegroundColor Cyan
    exit 1
}

Write-Host "Deploying Negotiation Agent to ECS Fargate..." -ForegroundColor Green
Write-Host "Account ID: $AWS_ACCOUNT_ID"
Write-Host "Region: $AWS_REGION"
Write-Host ""

# Step 1: Create ECS cluster
Write-Host "Step 1: Creating ECS cluster..." -ForegroundColor Cyan
$clusterExists = aws ecs describe-clusters --clusters $CLUSTER_NAME --region $AWS_REGION --query "clusters[0].status" --output text 2>$null
if ($clusterExists -ne "ACTIVE") {
    aws ecs create-cluster --cluster-name $CLUSTER_NAME --region $AWS_REGION
} else {
    Write-Host "Cluster already exists" -ForegroundColor Yellow
}

# Step 2: Create CloudWatch log group
Write-Host ""
Write-Host "Step 2: Creating CloudWatch log group..." -ForegroundColor Cyan
$logGroupExists = aws logs describe-log-groups --log-group-name-prefix $LOG_GROUP --region $AWS_REGION --query "logGroups[0].logGroupName" --output text 2>$null
if ($logGroupExists -ne $LOG_GROUP) {
    aws logs create-log-group --log-group-name $LOG_GROUP --region $AWS_REGION
} else {
    Write-Host "Log group already exists" -ForegroundColor Yellow
}

# Step 3: Create IAM role for ECS task execution
Write-Host ""
Write-Host "Step 3: Setting up IAM roles..." -ForegroundColor Cyan
$EXECUTION_ROLE_NAME = "ecsTaskExecutionRole"
$roleExists = aws iam get-role --role-name $EXECUTION_ROLE_NAME 2>$null
if (-not $roleExists) {
    # Create trust policy JSON file
    '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]}' | Out-File -FilePath trust-policy.json -Encoding ASCII -NoNewline
    aws iam create-role --role-name $EXECUTION_ROLE_NAME --assume-role-policy-document file://trust-policy.json
    aws iam attach-role-policy --role-name $EXECUTION_ROLE_NAME --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
    Remove-Item trust-policy.json
    Start-Sleep -Seconds 10
} else {
    Write-Host "Execution role already exists" -ForegroundColor Yellow
}

# Step 4: Register task definition
Write-Host ""
Write-Host "Step 4: Registering task definition..." -ForegroundColor Cyan
$IMAGE_URI = "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPOSITORY_NAME}:${IMAGE_TAG}"
$EXECUTION_ROLE_ARN = "arn:aws:iam::${AWS_ACCOUNT_ID}:role/$EXECUTION_ROLE_NAME"

# Step 4: Register task definition
Write-Host ""
Write-Host "Step 4: Registering task definition..." -ForegroundColor Cyan
$IMAGE_URI = "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPOSITORY_NAME}:${IMAGE_TAG}"
$EXECUTION_ROLE_ARN = "arn:aws:iam::${AWS_ACCOUNT_ID}:role/$EXECUTION_ROLE_NAME"

# Create task definition JSON
$taskDefJson = @{
    family = $TASK_FAMILY
    networkMode = "awsvpc"
    requiresCompatibilities = @("FARGATE")
    cpu = "1024"
    memory = "2048"
    executionRoleArn = $EXECUTION_ROLE_ARN
    containerDefinitions = @(
        @{
            name = $CONTAINER_NAME
            image = $IMAGE_URI
            essential = $true
            portMappings = @(
                @{
                    containerPort = 8000
                    protocol = "tcp"
                }
            )
            environment = @(
                @{
                    name = "AWS_REGION"
                    value = $AWS_REGION
                },
                @{
                    name = "AWS_BEARER_TOKEN_BEDROCK"
                    value = $BEARER_TOKEN
                }
            )
            logConfiguration = @{
                logDriver = "awslogs"
                options = @{
                    "awslogs-group" = $LOG_GROUP
                    "awslogs-region" = $AWS_REGION
                    "awslogs-stream-prefix" = "ecs"
                }
            }
        }
    )
}

$taskDefJson | ConvertTo-Json -Depth 10 | Out-File -FilePath task-definition.json -Encoding ASCII
aws ecs register-task-definition --cli-input-json file://task-definition.json --region $AWS_REGION
Remove-Item task-definition.json

# Step 5: Get VPC and subnet information
Write-Host ""
Write-Host "Step 5: Getting VPC and subnet information..." -ForegroundColor Cyan
$VPC_ID = aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text --region $AWS_REGION
$SUBNETS = aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[*].SubnetId" --output text --region $AWS_REGION
$SUBNET_LIST = $SUBNETS -replace '\s+', ','

Write-Host "VPC ID: $VPC_ID"
Write-Host "Subnets: $SUBNET_LIST"

# Step 6: Create security group
Write-Host ""
Write-Host "Step 6: Creating security group..." -ForegroundColor Cyan
$SG_NAME = "negotiation-agent-sg"
$SG_ID = aws ec2 describe-security-groups --filters "Name=group-name,Values=$SG_NAME" "Name=vpc-id,Values=$VPC_ID" --query "SecurityGroups[0].GroupId" --output text --region $AWS_REGION 2>$null

if ($SG_ID -eq "None" -or -not $SG_ID) {
    $SG_ID = aws ec2 create-security-group --group-name $SG_NAME --description "Security group for negotiation agent" --vpc-id $VPC_ID --region $AWS_REGION --query "GroupId" --output text
    
    # Allow inbound traffic on port 8000
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8000 --cidr 0.0.0.0/0 --region $AWS_REGION
    
    Write-Host "Created security group: $SG_ID"
} else {
    Write-Host "Security group already exists: $SG_ID" -ForegroundColor Yellow
}

# Step 7: Create or update ECS service
Write-Host ""
Write-Host "Step 7: Creating/Updating ECS service..." -ForegroundColor Cyan
$serviceExists = aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $AWS_REGION --query "services[0].status" --output text 2>$null

if ($serviceExists -ne "ACTIVE") {
    aws ecs create-service `
        --cluster $CLUSTER_NAME `
        --service-name $SERVICE_NAME `
        --task-definition $TASK_FAMILY `
        --desired-count 1 `
        --launch-type FARGATE `
        --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_LIST],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" `
        --region $AWS_REGION
} else {
    Write-Host "Service already exists, updating..." -ForegroundColor Yellow
    aws ecs update-service `
        --cluster $CLUSTER_NAME `
        --service $SERVICE_NAME `
        --task-definition $TASK_FAMILY `
        --force-new-deployment `
        --region $AWS_REGION
}

Write-Host ""
Write-Host "ECS Deployment complete!" -ForegroundColor Green
Write-Host "Waiting for service to stabilize..." -ForegroundColor Yellow
Write-Host ""

# Wait for service to be stable
aws ecs wait services-stable --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $AWS_REGION

# Get the public IP
Write-Host ""
Write-Host "Getting public endpoint..." -ForegroundColor Cyan
$TASK_ARN = aws ecs list-tasks --cluster $CLUSTER_NAME --service-name $SERVICE_NAME --region $AWS_REGION --query "taskArns[0]" --output text

if ($TASK_ARN -and $TASK_ARN -ne "None") {
    $ENI_ID = aws ecs describe-tasks --cluster $CLUSTER_NAME --tasks $TASK_ARN --region $AWS_REGION --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value" --output text
    $PUBLIC_IP = aws ec2 describe-network-interfaces --network-interface-ids $ENI_ID --region $AWS_REGION --query "NetworkInterfaces[0].Association.PublicIp" --output text
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Deployment successful!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "API Endpoint: http://${PUBLIC_IP}:8000" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Test the API:" -ForegroundColor Cyan
    Write-Host "  curl http://${PUBLIC_IP}:8000/health"
    Write-Host "  curl http://${PUBLIC_IP}:8000/"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Service is starting up..." -ForegroundColor Yellow
    Write-Host "Run this command in a few minutes to get the endpoint:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host '$TASK_ARN = aws ecs list-tasks --cluster negotiation-agent-cluster --service-name negotiation-agent-service --region us-east-1 --query "taskArns[0]" --output text' -ForegroundColor Cyan
    Write-Host '$ENI_ID = aws ecs describe-tasks --cluster negotiation-agent-cluster --tasks $TASK_ARN --region us-east-1 --query "tasks[0].attachments[0].details[?name==''networkInterfaceId''].value" --output text' -ForegroundColor Cyan
    Write-Host '$PUBLIC_IP = aws ec2 describe-network-interfaces --network-interface-ids $ENI_ID --region us-east-1 --query "NetworkInterfaces[0].Association.PublicIp" --output text' -ForegroundColor Cyan
    Write-Host 'Write-Host "API Endpoint: http://${PUBLIC_IP}:8000"' -ForegroundColor Cyan
    Write-Host ""
}
