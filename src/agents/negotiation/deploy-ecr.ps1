# PowerShell script for deploying to AWS ECR

# Configuration
$AWS_REGION = "us-east-1"
$AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
$ECR_REPOSITORY_NAME = "negotiation-agent"
$IMAGE_TAG = "latest"

Write-Host "Starting deployment to AWS ECR..." -ForegroundColor Green
Write-Host "AWS Account ID: $AWS_ACCOUNT_ID"
Write-Host "Region: $AWS_REGION"
Write-Host "Repository: $ECR_REPOSITORY_NAME"
Write-Host ""

# Step 1: Create ECR repository if it doesn't exist
Write-Host "Step 1: Creating ECR repository..." -ForegroundColor Cyan
$repoExists = aws ecr describe-repositories --repository-names $ECR_REPOSITORY_NAME --region $AWS_REGION 2>$null
if (-not $repoExists) {
    aws ecr create-repository `
        --repository-name $ECR_REPOSITORY_NAME `
        --region $AWS_REGION `
        --image-scanning-configuration scanOnPush=true `
        --encryption-configuration encryptionType=AES256
} else {
    Write-Host "Repository already exists" -ForegroundColor Yellow
}

# Step 2: Authenticate Docker to ECR
Write-Host ""
Write-Host "Step 2: Authenticating Docker to ECR..." -ForegroundColor Cyan
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

# Step 3: Build Docker image
Write-Host ""
Write-Host "Step 3: Building Docker image..." -ForegroundColor Cyan
docker build -t "${ECR_REPOSITORY_NAME}:${IMAGE_TAG}" .

# Step 4: Tag the image
Write-Host ""
Write-Host "Step 4: Tagging Docker image..." -ForegroundColor Cyan
docker tag "${ECR_REPOSITORY_NAME}:${IMAGE_TAG}" "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPOSITORY_NAME}:${IMAGE_TAG}"

# Step 5: Push to ECR
Write-Host ""
Write-Host "Step 5: Pushing image to ECR..." -ForegroundColor Cyan
docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPOSITORY_NAME}:${IMAGE_TAG}"

# Step 6: Display results
$IMAGE_URI = "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPOSITORY_NAME}:${IMAGE_TAG}"

Write-Host ""
Write-Host "Deployment to ECR complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Image URI: $IMAGE_URI" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Run deploy-ecs.ps1 to deploy to ECS Fargate"
Write-Host ""
