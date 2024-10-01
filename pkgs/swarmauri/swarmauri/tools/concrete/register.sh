#!/bin/bash

# Find all Python files in the current directory and subdirectories
find . -type f -name "*.py" | while read -r pyfile; do
    # Check if the file contains 'SubclassUnion' import, if not, add it to the first line
    if ! grep -q "from swarmauri_core.typing import SubclassUnion" "$pyfile"; then
        echo "Adding SubclassUnion import to $pyfile"
        sed -i '1i\from swarmauri_core.typing import SubclassUnion' "$pyfile"
    fi

    # Search for the class keyword and extract the class name
    class_name=$(grep -oP '^class\s+\K\w+' "$pyfile" | head -n 1)

    if [ -n "$class_name" ]; then
        echo "Processing class $class_name in $pyfile"

        # Prepare the line to append
        subclass_union_line="SubclassUnion[ToolBase].update({\"type\": '$class_name', \"object\": $class_name})"
        
        # Append the SubclassUnion update to the bottom of the file
        echo -e "\n\n$subclass_union_line\n" >> "$pyfile"
    else
        echo "No class found in $pyfile"
    fi
done

