#!/bin/bash

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY_NAME="negotiation-agent"
IMAGE_TAG="latest"

echo "🚀 Starting deployment to AWS ECR..."
echo "AWS Account ID: $AWS_ACCOUNT_ID"
echo "Region: $AWS_REGION"
echo "Repository: $ECR_REPOSITORY_NAME"

# Step 1: Create ECR repository if it doesn't exist
echo ""
echo "📦 Step 1: Creating ECR repository..."
aws ecr describe-repositories --repository-names $ECR_REPOSITORY_NAME --region $AWS_REGION 2>/dev/null || \
    aws ecr create-repository \
        --repository-name $ECR_REPOSITORY_NAME \
        --region $AWS_REGION \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256

# Step 2: Authenticate Docker to ECR
echo ""
echo "🔐 Step 2: Authenticating Docker to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Step 3: Build Docker image
echo ""
echo "🏗️  Step 3: Building Docker image..."
docker build -t $ECR_REPOSITORY_NAME:$IMAGE_TAG .

# Step 4: Tag the image
echo ""
echo "🏷️  Step 4: Tagging Docker image..."
docker tag $ECR_REPOSITORY_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$IMAGE_TAG

# Step 5: Push to ECR
echo ""
echo "⬆️  Step 5: Pushing image to ECR..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$IMAGE_TAG

# Step 6: Get image URI
IMAGE_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$IMAGE_TAG"

echo ""
echo "✅ Deployment to ECR complete!"
echo ""
echo "Image URI: $IMAGE_URI"
echo ""
echo "Next steps:"
echo "1. Run './deploy-ecs.sh' to deploy to ECS Fargate"
echo ""
