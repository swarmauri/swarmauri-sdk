#!/bin/bash

# Function to add directories to PYTHONPATH temporarily
add_to_pythonpath() {
    local paths=("$@")
    for path in "${paths[@]}"; do
        absolute_path=$(cd "$path" && pwd)
        if [[ ":$PYTHONPATH:" != *":$absolute_path:"* ]]; then
            export PYTHONPATH="$absolute_path${PYTHONPATH:+:$PYTHONPATH}"
            echo "Added to PYTHONPATH: $absolute_path"
        else
            echo "Path already in PYTHONPATH: $absolute_path"
        fi
    done
}
# List of paths to add (modify these as needed)
paths_to_add=(
    "/Users/michaeldecent/Swarmauri/swarmauri-sdk/pkgs/core"
    "/Users/michaeldecent/Swarmauri/swarmauri-sdk/pkgs/base"
    "/Users/michaeldecent/Swarmauri/swarmauri-sdk/pkgs/standards"
    "/Users/michaeldecent/Swarmauri/swarmauri-sdk/pkgs/community"
    "/Users/michaeldecent/Swarmauri/swarmauri-sdk/pkgs/core/swarmauri_core"
    "/Users/michaeldecent/Swarmauri/swarmauri-sdk/pkgs/base/swarmauri_base"
    "/Users/michaeldecent/Swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_standard"
)

# Add paths to PYTHONPATH
add_to_pythonpath "${paths_to_add[@]}"

# Confirm the paths have been added
echo "Current PYTHONPATH: $PYTHONPATH"