import os
import json


def get_all_base_files(root_dir, save_dir):
    # Define dictionaries to store file paths and their contents
    data = {
        "paths": [],
        "core_files": [],
        "standard_files": [],
        "community_files": [],
        "experimental_files": [],
        "examples_files": [],
        "all_content": [],
    }

    # Function to recursively search for .py files and categorize them
    def find_base_files(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py") and not file.endswith(
                    ".pyc"
                ):  # Exclude .pyc files
                    relative_path = os.path.relpath(
                        os.path.join(root, file), directory
                    ).replace("\\", "/")
                    full_path = f"swarmauri/{relative_path}"
                    with open(os.path.join(root, file), "r") as f:
                        content = f.read()
                        content = f"```{full_path}\n{content}\n```"
                        entry = {"document_name": full_path, "content": content}

                        # Assign to categories based on folder structure
                        if "_core" in root:
                            data["core_files"].append(entry)
                        if "swarmauri" in root:
                            data["standard_files"].append(entry)
                        if "_community" in root:
                            data["community_files"].append(entry)
                        if "_experimental" in root:
                            data["experimental_files"].append(entry)
                        if "examples" in root:
                            data["examples_files"].append(entry)
                        # For all content irrespective of categorization
                        data["all_content"].append(entry)

    find_base_files(root_dir)

    def save_to_json(file_data, file_name):
        file_path = os.path.join(save_dir, f"{file_name}.json")
        with open(file_path, "w") as json_file:
            json.dump(file_data, json_file, indent=4)
        print(f"{file_name}.json saved into {save_dir}")

    # Save data to json files
    save_to_json(data["paths"], "combined_paths")
    save_to_json(data["core_files"], "combined_core")
    save_to_json(data["standard_files"], "combined_standard")
    save_to_json(data["community_files"], "combined_community")
    save_to_json(data["experimental_files"], "combined_experimental")
    save_to_json(data["examples_files"], "combined_examples")
    save_to_json(data["all_content"], "combined_content")

    combined_core_standard = []
    combined_core_standard.extend(data["core_files"])
    combined_core_standard.extend(data["standard_files"])
    save_to_json(combined_core_standard, "combined_core_standard")


if __name__ == "__main__":
    get_all_base_files("../pkgs", "../combined")
