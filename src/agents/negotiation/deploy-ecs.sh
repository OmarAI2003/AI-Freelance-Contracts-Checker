#!/bin/bash

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY_NAME="negotiation-agent"
CLUSTER_NAME="negotiation-agent-cluster"
SERVICE_NAME="negotiation-agent-service"
TASK_FAMILY="negotiation-agent-task"
IMAGE_TAG="latest"

IMAGE_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$IMAGE_TAG"

echo "🚀 Deploying Negotiation Agent to ECS Fargate..."

# Step 1: Create ECS Cluster
echo ""
echo "📦 Step 1: Creating ECS cluster..."
aws ecs create-cluster \
    --cluster-name $CLUSTER_NAME \
    --region $AWS_REGION \
    --capacity-providers FARGATE FARGATE_SPOT \
    --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1 2>/dev/null || echo "✓ Cluster already exists"

# Step 2: Create CloudWatch Log Group
echo ""
echo "📝 Step 2: Creating CloudWatch log group..."
aws logs create-log-group \
    --log-group-name /ecs/$TASK_FAMILY \
    --region $AWS_REGION 2>/dev/null || echo "✓ Log group already exists"

# Step 3: Create IAM role if doesn't exist
echo ""
echo "🔑 Step 3: Setting up IAM roles..."
aws iam get-role --role-name ecsTaskExecutionRole 2>/dev/null || \
    aws iam create-role \
        --role-name ecsTaskExecutionRole \
        --assume-role-policy-document '{
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }'

# Attach policies
aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy 2>/dev/null

aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess 2>/dev/null

# Step 4: Get AWS Bearer Token from environment
if [ -z "$AWS_BEARER_TOKEN_BEDROCK" ]; then
    echo "⚠️  Warning: AWS_BEARER_TOKEN_BEDROCK not set"
    echo "Please set it: export AWS_BEARER_TOKEN_BEDROCK=your-token"
    exit 1
fi

# Step 5: Register Task Definition
echo ""
echo "📋 Step 4: Registering task definition..."
cat > task-definition.json <<EOF
{
  "family": "$TASK_FAMILY",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole",
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
          "value": "$AWS_BEARER_TOKEN_BEDROCK"
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
EOF

aws ecs register-task-definition \
    --cli-input-json file://task-definition.json \
    --region $AWS_REGION

# Step 6: Get VPC and subnet info
echo ""
echo "🌐 Step 5: Getting VPC and subnet information..."
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text --region $AWS_REGION)
SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[*].SubnetId" --output text --region $AWS_REGION | tr '\t' ',')

# Step 7: Create security group
echo ""
echo "🔒 Step 6: Creating security group..."
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
    --group-name negotiation-agent-sg \
    --description "Security group for negotiation agent" \
    --vpc-id $VPC_ID \
    --region $AWS_REGION \
    --query 'GroupId' \
    --output text 2>/dev/null || \
    aws ec2 describe-security-groups \
        --filters "Name=group-name,Values=negotiation-agent-sg" "Name=vpc-id,Values=$VPC_ID" \
        --query "SecurityGroups[0].GroupId" \
        --output text \
        --region $AWS_REGION)

# Allow inbound traffic on port 8000
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 8000 \
    --cidr 0.0.0.0/0 \
    --region $AWS_REGION 2>/dev/null || echo "✓ Security group rule already exists"

# Step 8: Create or update service
echo ""
echo "🎯 Step 7: Creating/Updating ECS service..."
aws ecs describe-services \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $AWS_REGION 2>/dev/null | grep -q "ACTIVE" && \
aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service $SERVICE_NAME \
    --task-definition $TASK_FAMILY \
    --force-new-deployment \
    --region $AWS_REGION || \
aws ecs create-service \
    --cluster $CLUSTER_NAME \
    --service-name $SERVICE_NAME \
    --task-definition $TASK_FAMILY \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}" \
    --region $AWS_REGION

echo ""
echo "✅ ECS Deployment complete!"
echo ""
echo "Cluster: $CLUSTER_NAME"
echo "Service: $SERVICE_NAME"
echo "Task Definition: $TASK_FAMILY"
echo ""
echo "⏳ Waiting for service to stabilize (this may take 2-3 minutes)..."
echo ""

# Wait for service to be stable
aws ecs wait services-stable \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $AWS_REGION

# Get the public IP
echo ""
echo "🔍 Getting public endpoint..."
TASK_ARN=$(aws ecs list-tasks \
    --cluster $CLUSTER_NAME \
    --service-name $SERVICE_NAME \
    --region $AWS_REGION \
    --query 'taskArns[0]' \
    --output text)

if [ "$TASK_ARN" != "None" ] && [ -n "$TASK_ARN" ]; then
    ENI_ID=$(aws ecs describe-tasks \
        --cluster $CLUSTER_NAME \
        --tasks $TASK_ARN \
        --region $AWS_REGION \
        --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
        --output text)
    
    PUBLIC_IP=$(aws ec2 describe-network-interfaces \
        --network-interface-ids $ENI_ID \
        --region $AWS_REGION \
        --query 'NetworkInterfaces[0].Association.PublicIp' \
        --output text)
    
    echo ""
    echo "🎉 Deployment successful!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "API Endpoint: http://$PUBLIC_IP:8000"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Test the API:"
    echo "curl http://$PUBLIC_IP:8000/health"
    echo ""
    echo "Share this endpoint with your friend for integration!"
    echo ""
else
    echo "⚠️  Could not get task information. Service may still be starting."
    echo "Run this command in a few minutes to get the endpoint:"
    echo "aws ecs describe-tasks --cluster $CLUSTER_NAME --tasks \$(aws ecs list-tasks --cluster $CLUSTER_NAME --service-name $SERVICE_NAME --query 'taskArns[0]' --output text) --query 'tasks[0].attachments[0].details[?name==\`networkInterfaceId\`].value' --output text | xargs -I {} aws ec2 describe-network-interfaces --network-interface-ids {} --query 'NetworkInterfaces[0].Association.PublicIp' --output text"
fi
