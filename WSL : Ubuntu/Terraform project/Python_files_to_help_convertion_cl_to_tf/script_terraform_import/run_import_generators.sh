#!/bin/bash
set -e

ROOT_DIR="generated/aws"
SCRIPT_NAME="script_command_terraform_import.py"
SCRIPT_PATH="$(pwd)/$SCRIPT_NAME"

if [ ! -f "$SCRIPT_PATH" ]; then
  echo "Error: $SCRIPT_NAME not found in the project root."
  exit 1
fi

find "$ROOT_DIR" -type f -name "terraform.tfstate" | while read -r tfstate_file; do
  dir=$(dirname "$tfstate_file")
  echo "Found directory: $dir"
  
  # Copy the Python script into the directory
  cp "$SCRIPT_PATH" "$dir/"
  
  # Execute the script in the directory
  (
    cd "$dir"
    echo "Running $SCRIPT_NAME in $(pwd)..."
    python3 "$SCRIPT_NAME"
  )
  
  echo "Completed for $dir"
  echo "------------------------------------------"
done

echo "All import files have been generated successfully using your script."

