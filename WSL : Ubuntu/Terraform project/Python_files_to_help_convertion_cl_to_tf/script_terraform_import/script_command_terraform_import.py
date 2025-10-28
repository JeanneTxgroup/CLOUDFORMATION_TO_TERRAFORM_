import json

# Path to your terraform.tfstate
TFSTATE_FILE = "terraform.tfstate"

with open(TFSTATE_FILE, "r") as file:
    tfstate = json.load(file)

modules = tfstate.get("modules", [])

# Store all lines here
output_lines = []
import_commands = []
stock_type = set()

# Variable to store type
the_type = None

for module in modules:
    resources = module.get("resources", {})
    for key, data in resources.items():
        if not the_type:
            # Take the type of the first resource encountered
            the_type = data.get("type")

        # Logical name of the resource
        name_logical = key.split('.')[-1].replace("-", "_")

        # Resource ID
        id = (data.get("primary", {}).get("id")
              or data.get("primary", {}).get("attributes", {}).get("id")
              or "NO ID FOUND")
        
        # Resource name for import
        name = (data.get("primary", {}).get("attributes", {}).get("name") 
                or data.get("primary", {}).get("attributes", {}).get("tags.Name") 
                or "NO_NAME_FOUND")
        name = name.replace("-", "_")  # Replace all - with _

        # Formatted line
        line = f"Type: {the_type:<25} | Name: {name:<30} | ID: {id} | Logical Name: {name_logical}"
        output_lines.append(line)
        output_lines.append("")  # Empty line

        # Terraform import line
        import_line = f"terraform import {the_type}.{name} {id}"
        import_commands.append(import_line)
        stock_type.add(the_type)

# Output file name
OUTPUT_FILE = f"Import_for_{the_type}.txt"

# Add terraform import commands
output_lines.append("# Terraform import commands:")
output_lines.extend(import_commands)

# Write to file
with open(OUTPUT_FILE, "w") as out_file:
    out_file.write("\n".join(output_lines))