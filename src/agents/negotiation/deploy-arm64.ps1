param(
    [string]$Region = "us-east-1",
    [string]$Repository = "negotiation-agent",
    [string]$ImageTag = "arm64"
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Building ARM64 Docker Image for AgentCore" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Resolve AWS account dynamically to avoid mismatches
$AWS_ACCOUNT_ID = aws sts get-caller-identity --query Account --output text
if (-not $AWS_ACCOUNT_ID) {
    Write-Host "Failed to resolve AWS account ID. Ensure AWS CLI is configured." -ForegroundColor Red
    exit 1
}

$AWS_REGION = $Region
$ECR_REPOSITORY_NAME = $Repository
$IMAGE_TAG = $ImageTag
$ECR_REGISTRY = "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
$IMAGE_URI = "${ECR_REGISTRY}/${ECR_REPOSITORY_NAME}:${IMAGE_TAG}"

Write-Host "Configuration:" -ForegroundColor Green
Write-Host "  AWS Account ID: $AWS_ACCOUNT_ID" -ForegroundColor White
Write-Host "  AWS Region: $AWS_REGION" -ForegroundColor White
Write-Host "  ECR Repository: $ECR_REPOSITORY_NAME" -ForegroundColor White
Write-Host "  Image Tag: $IMAGE_TAG" -ForegroundColor White
Write-Host "  Target Architecture: linux/arm64" -ForegroundColor Yellow
Write-Host ""

Write-Host "[1/6] Checking ECR repository..." -ForegroundColor Cyan
$repoExists = aws ecr describe-repositories --repository-names $ECR_REPOSITORY_NAME --region $AWS_REGION 2>$null
if (-not $repoExists) {
    Write-Host "  Creating ECR repository: $ECR_REPOSITORY_NAME" -ForegroundColor Yellow
    aws ecr create-repository --repository-name $ECR_REPOSITORY_NAME --region $AWS_REGION | Out-Null
    Write-Host "  Repository created" -ForegroundColor Green
} else {
    Write-Host "  Repository already exists" -ForegroundColor Green
}

Write-Host "`n[2/6] Setting up Docker Buildx..." -ForegroundColor Cyan
$builderExists = docker buildx ls | Select-String "arm-builder"
if (-not $builderExists) {
    Write-Host "  Creating new buildx builder..." -ForegroundColor Yellow
    docker buildx create --name arm-builder --use | Out-Null
    docker buildx inspect --bootstrap | Out-Null
    Write-Host "  Buildx builder created" -ForegroundColor Green
} else {
    Write-Host "  Using existing buildx builder..." -ForegroundColor Yellow
    docker buildx use arm-builder | Out-Null
    Write-Host "  Buildx builder ready" -ForegroundColor Green
}

Write-Host "`n[3/6] Building Docker image for ARM64..." -ForegroundColor Cyan
Write-Host "  This may take a few minutes..." -ForegroundColor Yellow
docker buildx build --platform linux/arm64 -t ${ECR_REPOSITORY_NAME}:${IMAGE_TAG} . --load
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Docker build failed" -ForegroundColor Red
    exit 1
}
Write-Host "  Image built successfully" -ForegroundColor Green

Write-Host "`n[4/6] Tagging image for ECR..." -ForegroundColor Cyan
docker tag ${ECR_REPOSITORY_NAME}:${IMAGE_TAG} $IMAGE_URI
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Docker tag failed" -ForegroundColor Red
    exit 1
}
Write-Host "  Image tagged" -ForegroundColor Green

Write-Host "`n[5/6] Logging in to AWS ECR..." -ForegroundColor Cyan

function Invoke-EcrLoginWithRetry {
    param([int]$MaxRetries = 4)
    for ($i = 1; $i -le $MaxRetries; $i++) {
        aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
        Write-Host "  ECR login attempt $i failed. Retrying in $([int](5 * $i))s..." -ForegroundColor Yellow
        Start-Sleep -Seconds (5 * $i)
    }
    return $false
}

if (-not (Invoke-EcrLoginWithRetry -MaxRetries 5)) {
    Write-Host "  ECR login failed after retries" -ForegroundColor Red
    exit 1
}
Write-Host "  Logged in to ECR" -ForegroundColor Green

Write-Host "`n[6/6] Pushing ARM64 image to ECR..." -ForegroundColor Cyan
Write-Host "  This may take a few minutes..." -ForegroundColor Yellow

function Invoke-PushWithRetry {
    param([string]$ImageUri, [int]$MaxRetries = 3)

    for ($i = 1; $i -le $MaxRetries; $i++) {
        docker push $ImageUri
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
        Write-Host "  Push attempt $i failed. Retrying in $([int](5 * $i))s..." -ForegroundColor Yellow
        Start-Sleep -Seconds (5 * $i)
    }
    return $false
}

if (-not (Invoke-PushWithRetry -ImageUri $IMAGE_URI -MaxRetries 4)) {
    Write-Host "  Docker push failed after retries" -ForegroundColor Red
    exit 1
}
Write-Host "  Image pushed successfully" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Verifying Image Architecture" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

docker buildx imagetools inspect $IMAGE_URI | Select-String "Platform"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Deployment Complete" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Image URI:" -ForegroundColor Cyan
Write-Host "  $IMAGE_URI" -ForegroundColor White
Write-Host "`nArchitecture: linux/arm64" -ForegroundColor Cyan
Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "  1. Go to AWS Bedrock AgentCore console" -ForegroundColor White
Write-Host "  2. Use this image URI in your agent" -ForegroundColor White
Write-Host "  3. Select Public security option" -ForegroundColor White
Write-Host ""
