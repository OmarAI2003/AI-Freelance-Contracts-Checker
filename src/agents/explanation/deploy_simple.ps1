# Simple Lambda Deployment Script
# Deploy Explanation Agent to AWS Lambda

Write-Host "========================================"
Write-Host " Lambda Deployment - Explanation Agent"
Write-Host "========================================"

# Get script directory
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $SCRIPT_DIR

$FUNCTION_NAME = "explanation-agent"
$ROLE_NAME = "lambda-bedrock-explanation-role"
$REGION = "us-east-1"
$ACCOUNT_ID = "897722703585"

# Step 1: Create deployment folder
Write-Host "`n[1/8] Creating deployment folder..."
$DEPLOY_DIR = "lambda_package"
if (Test-Path $DEPLOY_DIR) {
    Remove-Item $DEPLOY_DIR -Recurse -Force
}
New-Item -Path $DEPLOY_DIR -ItemType Directory | Out-Null
Write-Host "Done!"

# Step 2: Create directory structure
Write-Host "`n[2/8] Creating directory structure..."
New-Item -Path "$DEPLOY_DIR\agents\explanation" -ItemType Directory -Force | Out-Null
New-Item -Path "$DEPLOY_DIR\agents\__init__.py" -ItemType File -Force | Out-Null
New-Item -Path "$DEPLOY_DIR\agents\explanation\__init__.py" -ItemType File -Force | Out-Null
Write-Host "Done!"

# Step 3: Copy files
Write-Host "`n[3/8] Copying agent files..."
Copy-Item -Path "agent.py" -Destination "$DEPLOY_DIR\agents\explanation\"
Copy-Item -Path "prompts.py" -Destination "$DEPLOY_DIR\agents\explanation\"
Copy-Item -Path "memory_hooks.py" -Destination "$DEPLOY_DIR\agents\explanation\"
Copy-Item -Path "tools.py" -Destination "$DEPLOY_DIR\agents\explanation\"
Copy-Item -Path "__init__.py" -Destination "$DEPLOY_DIR\agents\explanation\"
Copy-Item -Path "lambda_handler.py" -Destination "$DEPLOY_DIR\"
Write-Host "Done!"

# Step 4: Install dependencies
Write-Host "`n[4/8] Installing dependencies (2-3 minutes)..."
Push-Location $DEPLOY_DIR
pip install --quiet --target . strands-agents boto3 pydantic bedrock-agentcore
Pop-Location
Write-Host "Done!"

# Step 5: Create ZIP
Write-Host "`n[5/8] Creating deployment package..."
Push-Location $DEPLOY_DIR
$ZIP_FILE = "..\explanation_agent.zip"
if (Test-Path $ZIP_FILE) {
    Remove-Item $ZIP_FILE -Force
}
Compress-Archive -Path * -DestinationPath $ZIP_FILE
Pop-Location
$SIZE = [math]::Round((Get-Item "explanation_agent.zip").Length / 1MB, 2)
Write-Host "Done! Size: $SIZE MB"

# Step 6: Check AWS CLI
Write-Host "`n[6/8] Checking AWS credentials..."
try {
    $IDENTITY = aws sts get-caller-identity 2>&1 | ConvertFrom-Json
    Write-Host "Done! Account: $($IDENTITY.Account)"
} catch {
    Write-Host "ERROR: AWS credentials not configured. Run: aws configure"
    exit 1
}

# Step 7: Create/Check IAM Role
Write-Host "`n[7/8] Setting up IAM role..."
$ROLE_ARN = "arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"

$CHECK_ROLE = aws iam get-role --role-name $ROLE_NAME 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating new IAM role..."
    
    $TRUST_POLICY = @"
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
"@
    
    $TRUST_POLICY | Out-File -FilePath "trust-policy.json" -Encoding utf8
    aws iam create-role --role-name $ROLE_NAME --assume-role-policy-document file://trust-policy.json | Out-Null
    aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
    Remove-Item "trust-policy.json"
    
    Write-Host "Waiting for IAM role to propagate (10 seconds)..."
    Start-Sleep -Seconds 10
    Write-Host "Done!"
} else {
    Write-Host "IAM role already exists"
}

# Step 8: Deploy Lambda
Write-Host "`n[8/8] Deploying Lambda function..."

$CHECK_FUNCTION = aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating new Lambda function..."
    aws lambda create-function `
        --function-name $FUNCTION_NAME `
        --runtime python3.12 `
        --role $ROLE_ARN `
        --handler lambda_handler.lambda_handler `
        --zip-file fileb://explanation_agent.zip `
        --timeout 60 `
        --memory-size 1024 `
        --region $REGION | Out-Null
} else {
    Write-Host "Updating existing Lambda function..."
    aws lambda update-function-code `
        --function-name $FUNCTION_NAME `
        --zip-file fileb://explanation_agent.zip `
        --region $REGION | Out-Null
        
    aws lambda update-function-configuration `
        --function-name $FUNCTION_NAME `
        --timeout 60 `
        --memory-size 1024 `
        --region $REGION | Out-Null
}

Write-Host "`n========================================"
Write-Host " DEPLOYMENT SUCCESSFUL!"
Write-Host "========================================"
Write-Host "`nFunction: $FUNCTION_NAME"
Write-Host "Region: $REGION"
Write-Host "Role: $ROLE_NAME"
Write-Host "`nTest command:"
Write-Host 'aws lambda invoke --function-name explanation-agent --region us-east-1 --payload "{\"body\":\"{\\\"clause_text\\\":\\\"Payment within 90 days\\\"}\"}" response.json'
Write-Host "`nNext: Create API Gateway in AWS Console"
Write-Host "========================================"
