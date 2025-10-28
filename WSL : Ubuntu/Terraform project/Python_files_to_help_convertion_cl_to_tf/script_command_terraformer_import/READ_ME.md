# Extract CloudFormation Resource Types to Terraform Types

This script extracts resource types from a CloudFormation YAML template and maps them to their known Terraform equivalents. Unrecognized resource types are listed only once at the end of the generated output file.

---

## Features

- Parses a CloudFormation YAML template
- Ignores CloudFormation tags like !Ref, !Sub, etc.
- Extracts CloudFormation resource types
- Maps CloudFormation resource types to Terraform types
- Generates a `.txt` file listing all recognized Terraform types
- Adds a single list of unrecognized CloudFormation types as a comment at the end of the file

---

## Usage

1. Place your CloudFormation YAML template file (e.g., `template.yaml`)
2. Run the script specifying the input template and output file:

```bash
python3 extract_types.py template.yaml output.txt

## Example Output

aws_instance
aws_s3_bucket
aws_iam_role

# Unrecognized CFN types:
AWS::My::CustomResource
AWS::Another::UnknownType