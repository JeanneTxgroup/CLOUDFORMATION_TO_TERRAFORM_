# Terraform Setup Script for AWS

This script helps you quickly bootstrap or resume a Terraform project for AWS by:

- Creating a base `main.tf` configuration file (if needed)
- Setting up your AWS credentials
- Running `terraform init` automatically

It is useful when starting a new project, or when switching environments and needing to refresh your credentials.

---

## Features

- Two setup modes:
  - Full setup: create a fresh `main.tf`, configure credentials, run `terraform init`
  - Credentials only: only update your AWS credentials and initialize Terraform
- Automatically creates or updates your `~/.aws/credentials` file
- Supports both permanent credentials and temporary session tokens
- Runs `terraform init` to prepare the working directory

---

## Prerequisites

Make sure you have the following installed:

- Python 3
- Terraform (in your system's PATH)

---

## Usage

Run the script:

```bash
python3 terraform_setup.py
