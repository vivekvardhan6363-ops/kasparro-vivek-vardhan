# deploy_ecr.ps1
# Usage: .\deployment\deploy_ecr.ps1

Write-Host "Checking AWS CLI..."
if (-not (Get-Command "aws" -ErrorAction SilentlyContinue)) {
    Write-Error "AWS CLI not found. Please install it: https://aws.amazon.com/cli/"
    exit 1
}

$REGION = "ap-south-1"
$REPO_NAME = "antigravity-backend-etl"

Write-Host "Logging in to ECR ($REGION)..."
$Token = aws ecr get-login-password --region $REGION
if (-not $Token) { exit 1 }
$Token | docker login --username AWS --password-stdin "$(aws ecr get-authorization-token --region $REGION --query 'authorizationData[].proxyEndpoint' --output text)"

Write-Host "Creating Repository '$REPO_NAME'..."
aws ecr create-repository --repository-name $REPO_NAME --region $REGION --image-scanning-configuration scanOnPush=true
# Ignore error if already exists

$ACCOUNT_ID = aws sts get-caller-identity --query Account --output text
$ECR_URI = "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}"

Write-Host "Building Docker Image..."
docker build -t ${REPO_NAME}:latest .

Write-Host "Tagging Image..."
docker tag ${REPO_NAME}:latest ${ECR_URI}:latest

Write-Host "Pushing to ECR..."
docker push ${ECR_URI}:latest

Write-Host "✅ Image Pushed Successfully: ${ECR_URI}:latest"
Write-Host "You can now pull this image on your EC2 instance."
