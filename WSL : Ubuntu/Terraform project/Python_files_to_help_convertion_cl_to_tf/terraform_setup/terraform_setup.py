import os
import subprocess
from pathlib import Path

# Ask user for the desired setup mode
print("Choose setup mode:")
print("1 - Full setup (create main.tf, set AWS credentials, run terraform init)")
print("2 - Credentials only (set AWS credentials, run terraform init without touching main.tf)")
mode = input("Enter 1 or 2: ").strip()

# Terraform configuration content
terraform_code = '''terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-west-1"
}
'''

# Step 1: Create main.tf if in full mode
if mode == "1":
    with open("main.tf", "w") as f:
        f.write(terraform_code)
    print("main.tf file created.")

# Step 2: Get AWS credentials from user
print("\nPaste your AWS credentials (access key, secret key, session token if applicable).")
print("Press Enter on an empty line to finish:")

lines = []
while True:
    try:
        line = input()
        if line.strip() == "":
            break
        lines.append(line.strip())
    except EOFError:
        break

if len(lines) < 2:
    print("Error: At least 2 lines are required (access key and secret key).")
    exit(1)

# Step 3: Write credentials to ~/.aws/credentials
aws_dir = Path.home() / ".aws"
aws_dir.mkdir(parents=True, exist_ok=True)
credentials_file = aws_dir / "credentials"

with open(credentials_file, "w") as f:
    f.write("[default]\n")
    for line in lines:
        f.write(line + "\n")

print("AWS credentials written to ~/.aws/credentials.")

# Step 4: Run terraform init
print("\nRunning 'terraform init'...")
try:
    subprocess.run(["terraform", "init"], check=True)
    print("Terraform initialized successfully.")
except subprocess.CalledProcessError:
    print("Error: Terraform initialization failed. Make sure Terraform is installed.")
