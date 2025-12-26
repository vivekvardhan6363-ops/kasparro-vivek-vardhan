#!/bin/bash
# setup_ec2.sh
# Run this on your EC2 instance (Amazon Linux 2)

# 1. Install Docker
sudo yum update -y
sudo amazon-linux-extras install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user

# 2. Authenticate to ECR (You need to attach an IAM Role to this EC2 instance!)
# aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <YOUR_ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com

# 3. Pull & Run
# docker run -d -p 8000:8000 --env-file .env <YOUR_ECR_URI>:latest

# 4. Setup Cron for ETL
# (crontab -l 2>/dev/null; echo "0 * * * * docker exec \$(docker ps -q -f ancestor=<YOUR_ECR_URI>:latest) python run_etl.py") | crontab -
