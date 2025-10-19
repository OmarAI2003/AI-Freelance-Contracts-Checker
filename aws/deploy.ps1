# AWS Deployment Script for Freelancer Legal Assistant
# Simplified architecture using Bedrock AgentCore's built-in memory

$ErrorActionPreference = "Stop"

Write-Host "Deploying Freelancer Legal Assistant to AWS" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_NAME = "freelancer-legal-assistant"
$REGION = "us-east-1"
$ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
$ACTION_AGENT_ARN = "arn:aws:bedrock-agentcore:us-east-1:897722703585:runtime/freelancer_action_agent-Q83Rk73nkD"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Project: $PROJECT_NAME"
Write-Host "  Region: $REGION"
Write-Host "  Account: $ACCOUNT_ID"
Write-Host "  Action Agent: $ACTION_AGENT_ARN"
Write-Host ""

# ============================================================================
# PHASE 1: Package Lambda Function
# ============================================================================

Write-Host "Phase 1: Packaging Lambda Function..." -ForegroundColor Green

Set-Location "src\lambda"

# Create package directory
if (Test-Path "package") {
    Remove-Item -Recurse -Force "package"
}
New-Item -ItemType Directory -Force -Path "package" | Out-Null

# Install dependencies
Write-Host "  Installing dependencies..."
$ErrorActionPreference = "Continue"
pip install -q -r requirements.txt -t package/
$ErrorActionPreference = "Stop"

# Copy Lambda code
Write-Host "  Copying Lambda code..."
Copy-Item "orchestrator_lambda.py" "package/"

# Create ZIP
Write-Host "  Creating deployment package..."
Set-Location "package"
if (Test-Path "../orchestrator-lambda.zip") {
    Remove-Item "../orchestrator-lambda.zip"
}
Compress-Archive -Path * -DestinationPath "../orchestrator-lambda.zip" -CompressionLevel Optimal
Set-Location ".."

Write-Host "  Lambda package created: orchestrator-lambda.zip" -ForegroundColor Green
Write-Host ""

Set-Location "..\.."

# ============================================================================
# PHASE 2: Deploy CloudFormation Stack
# ============================================================================

Write-Host "Phase 2: Deploying CloudFormation Stack..." -ForegroundColor Green

$STACK_NAME = "$PROJECT_NAME-stack"

# Check if stack exists
$stackExists = $false
try {
    aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION 2>$null | Out-Null
    $stackExists = $true
    Write-Host "  Stack exists, updating..." -ForegroundColor Yellow
} catch {
    Write-Host "  Creating new stack..." -ForegroundColor Yellow
}

# Deploy stack
if ($stackExists) {
    aws cloudformation update-stack `
        --stack-name $STACK_NAME `
        --template-body file://aws/cloudformation/main-stack.yaml `
        --parameters `
            ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME `
            ParameterKey=ActionAgentARN,ParameterValue=$ACTION_AGENT_ARN `
        --capabilities CAPABILITY_NAMED_IAM `
        --region $REGION
} else {
    aws cloudformation create-stack `
        --stack-name $STACK_NAME `
        --template-body file://aws/cloudformation/main-stack.yaml `
        --parameters `
            ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME `
            ParameterKey=ActionAgentARN,ParameterValue=$ACTION_AGENT_ARN `
        --capabilities CAPABILITY_NAMED_IAM `
        --region $REGION
}

Write-Host "  Waiting for stack deployment (this may take 5-10 minutes)..." -ForegroundColor Yellow
aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $REGION 2>$null
if ($LASTEXITCODE -ne 0) {
    aws cloudformation wait stack-update-complete --stack-name $STACK_NAME --region $REGION 2>$null
}

Write-Host "  CloudFormation stack deployed" -ForegroundColor Green
Write-Host ""

# Get stack outputs
$outputs = aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs" | ConvertFrom-Json

$FRONTEND_BUCKET = ($outputs | Where-Object { $_.OutputKey -eq "FrontendBucketName" }).OutputValue
$UPLOADS_BUCKET = ($outputs | Where-Object { $_.OutputKey -eq "UploadsBucketName" }).OutputValue
$CLOUDFRONT_URL = ($outputs | Where-Object { $_.OutputKey -eq "CloudFrontURL" }).OutputValue
$API_URL = ($outputs | Where-Object { $_.OutputKey -eq "ApiGatewayURL" }).OutputValue
$LAMBDA_FUNCTION = ($outputs | Where-Object { $_.OutputKey -eq "OrchestratorFunctionName" }).OutputValue

Write-Host "Stack Outputs:" -ForegroundColor Yellow
Write-Host "  Frontend Bucket: $FRONTEND_BUCKET"
Write-Host "  Uploads Bucket: $UPLOADS_BUCKET"
Write-Host "  CloudFront URL: https://$CLOUDFRONT_URL"
Write-Host "  API URL: $API_URL"
Write-Host "  Lambda Function: $LAMBDA_FUNCTION"
Write-Host ""

# ============================================================================
# PHASE 3: Deploy Lambda Code
# ============================================================================

Write-Host "Phase 3: Deploying Lambda Code..." -ForegroundColor Green

aws lambda update-function-code `
    --function-name $LAMBDA_FUNCTION `
    --zip-file fileb://src/lambda/orchestrator-lambda.zip `
    --region $REGION | Out-Null

Write-Host "  Waiting for Lambda update..."
aws lambda wait function-updated --function-name $LAMBDA_FUNCTION --region $REGION

Write-Host "  Lambda code deployed" -ForegroundColor Green
Write-Host ""

# ============================================================================
# PHASE 4: Update Frontend Config and Deploy
# ============================================================================

Write-Host "Phase 4: Deploying Frontend..." -ForegroundColor Green

# Update app.js with API URL
$appJsPath = "src\frontend\static\js\app.js"
$appJsContent = Get-Content $appJsPath -Raw
$appJsContent = $appJsContent -replace "const API_BASE_URL = '[^']*'", "const API_BASE_URL = '$API_URL'"
Set-Content $appJsPath $appJsContent

Write-Host "  Updated API URL in app.js"

# Sync frontend files to S3
Write-Host "  Uploading frontend files to S3..."
aws s3 sync src/frontend/ s3://$FRONTEND_BUCKET/ `
    --exclude "*.py" `
    --exclude "*.txt" `
    --exclude "__pycache__/*" `
    --exclude "*.md" `
    --exclude "uploads/*" `
    --region $REGION `
    --quiet

# Set correct content types
aws s3 cp s3://$FRONTEND_BUCKET/index.html s3://$FRONTEND_BUCKET/index.html --content-type "text/html" --metadata-directive REPLACE --region $REGION --quiet
aws s3 cp s3://$FRONTEND_BUCKET/static/css/styles.css s3://$FRONTEND_BUCKET/static/css/styles.css --content-type "text/css" --metadata-directive REPLACE --region $REGION --quiet
aws s3 cp s3://$FRONTEND_BUCKET/static/js/app.js s3://$FRONTEND_BUCKET/static/js/app.js --content-type "application/javascript" --metadata-directive REPLACE --region $REGION --quiet

Write-Host "  Frontend deployed to S3" -ForegroundColor Green
Write-Host ""

# ============================================================================
# PHASE 5: Invalidate CloudFront Cache
# ============================================================================

Write-Host "Phase 5: Invalidating CloudFront Cache..." -ForegroundColor Green

$DISTRIBUTION_ID = (aws cloudfront list-distributions --query "DistributionList.Items[?Comment=='$PROJECT_NAME CDN'].Id" --output text --region $REGION)

if ($DISTRIBUTION_ID) {
    aws cloudfront create-invalidation `
        --distribution-id $DISTRIBUTION_ID `
        --paths "/*" `
        --region $REGION | Out-Null
    
    Write-Host "  CloudFront cache invalidated" -ForegroundColor Green
} else {
    Write-Host "  CloudFront distribution not found" -ForegroundColor Yellow
}
Write-Host ""

# ============================================================================
# PHASE 6: Test Deployment
# ============================================================================

Write-Host "Phase 6: Testing Deployment..." -ForegroundColor Green

# Test Lambda
Write-Host "  Testing Lambda health check..."
$healthPayload = @{
    httpMethod = "GET"
    path = "/api/health"
} | ConvertTo-Json -Compress

$healthResponse = aws lambda invoke `
    --function-name $LAMBDA_FUNCTION `
    --payload "$healthPayload" `
    --region $REGION `
    response.json 2>&1

if ($LASTEXITCODE -eq 0) {
    $responseBody = Get-Content response.json | ConvertFrom-Json
    Write-Host "  Lambda health check passed" -ForegroundColor Green
    Remove-Item response.json
} else {
    Write-Host "  Lambda health check failed" -ForegroundColor Red
}

# Test API Gateway
Write-Host "  Testing API Gateway..."
try {
    $apiResponse = Invoke-WebRequest -Uri "$API_URL/api/health" -Method GET -UseBasicParsing
    if ($apiResponse.StatusCode -eq 200) {
        Write-Host "  API Gateway health check passed" -ForegroundColor Green
    }
} catch {
    Write-Host "  API Gateway might still be warming up" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# DEPLOYMENT COMPLETE
# ============================================================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your application is live at:" -ForegroundColor Yellow
Write-Host "   https://$CLOUDFRONT_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "API Endpoint:" -ForegroundColor Yellow
Write-Host "   $API_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "Resources Created:" -ForegroundColor Yellow
Write-Host "   S3 Frontend Bucket: $FRONTEND_BUCKET"
Write-Host "   S3 Uploads Bucket: $UPLOADS_BUCKET"
Write-Host "   Lambda Function: $LAMBDA_FUNCTION"
Write-Host "   API Gateway: $API_URL"
Write-Host "   CloudFront Distribution: https://$CLOUDFRONT_URL"
Write-Host ""
Write-Host "Agent Status:" -ForegroundColor Yellow
Write-Host "   Action Agent: DEPLOYED (Real - AWS Bedrock AgentCore)"
Write-Host "   Analysis Agent: DUMMY (Awaiting Dev 1)"
Write-Host "   Explanation Agent: DUMMY (Awaiting Dev 2)"
Write-Host "   Negotiation Agent: DUMMY (Awaiting Dev 3)"
Write-Host ""
Write-Host "Key Features:" -ForegroundColor Yellow
Write-Host "   A2A Protocol: Agent-to-Agent communication"
Write-Host "   Built-in Memory: Bedrock AgentCore session management"
Write-Host "   Intent Classification: Automatic routing to specialist agents"
Write-Host "   Unified Interface: Single chat for all 4 agents"
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Test the application: https://$CLOUDFRONT_URL"
Write-Host "   2. Try: 'My client won't pay me' (Action Agent - Real!)"
Write-Host "   3. Monitor: aws logs tail /aws/lambda/$LAMBDA_FUNCTION --follow"
Write-Host "   4. When teammates deploy agents, update Lambda environment variables"
Write-Host ""
Write-Host "Estimated Cost: ~`$70/month (moderate usage)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Happy Hacking!" -ForegroundColor Cyan
