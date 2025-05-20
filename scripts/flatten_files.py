import os


def get_all_base_files(root_dir, save_dir):  # Define the root directory
    # Paths of all files
    paths = []

    # All code in codebase
    all_content = []

    # Base.py file content of every folder
    core_files_content = []

    # Concrete only
    standard_files_content = []

    # Community concrete
    community_files_content = []

    # Community concrete
    experimental_files_content = []

    # Community concrete
    examples_files_content = []

    # Function to recursively search for base.py files
    def find_base_files(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                sub_str = root + "\\" + file
                sub_str = sub_str.replace(directory, "swarmauri")
                sub_str = sub_str.replace("\\", "/")
                if ".pyc" not in sub_str:
                    paths.append(sub_str)

                    # Add all content except .pyc
                    with open(os.path.join(root, file), "r") as f:
                        content = f.read()
                        all_content.append(f"```{sub_str}")
                        all_content.append(content)
                        all_content.append("```")

                    if "core" in root:
                        # print(root, file)
                        with open(os.path.join(root, file), "r") as f:
                            content = f.read()
                            core_files_content.append(f"```{sub_str}")
                            core_files_content.append(content)
                            core_files_content.append("```")

                    if "standard" in root:
                        with open(os.path.join(root, file), "r") as f:
                            content = f.read()
                            standard_files_content.append(f"```{sub_str}")
                            standard_files_content.append(content)
                            standard_files_content.append("```")

                    if "community" in root:
                        with open(os.path.join(root, file), "r") as f:
                            content = f.read()
                            community_files_content.append(f"```{sub_str}")
                            community_files_content.append(content)
                            community_files_content.append("```")

                    if "experimental" in root:
                        with open(os.path.join(root, file), "r") as f:
                            content = f.read()
                            experimental_files_content.append(f"```{sub_str}")
                            experimental_files_content.append(content)
                            experimental_files_content.append("```")

                    if "examples" in root:
                        with open(os.path.join(root, file), "r") as f:
                            content = f.read()
                            examples_files_content.append(f"```{sub_str}")
                            examples_files_content.append(content)
                            examples_files_content.append("```")

    # Find all base.py files in the root directory
    find_base_files(root_dir)

    # Combine the content of base.py files
    combined_paths = "\n".join(paths)
    combined_core = "\n\n".join(core_files_content)
    combined_standard = "\n\n".join(standard_files_content)
    combined_community = "\n\n".join(community_files_content)
    combined_experimental = "\n\n".join(experimental_files_content)
    combined_examples = "\n\n".join(examples_files_content)
    combined_content = "\n\n".join(all_content)

    ## Write all paths to file
    output_file_path = os.path.join(save_dir, "combined_paths.md")
    with open(output_file_path, "w") as output_file:
        output_file.write(combined_paths)

    print(f"combined_paths.md files into {output_file_path}")

    ## Write all core files to file
    output_file_path = os.path.join(save_dir, "combined_core.md")
    with open(output_file_path, "w") as output_file:
        output_file.write(combined_core)

    print(f"combined_core.md files into {output_file_path}")

    ## Write all standard files to file
    output_file_path = os.path.join(save_dir, "combined_standard.md")
    with open(output_file_path, "w") as output_file:
        output_file.write(combined_standard)

    print(f"combined_standard.md files into {output_file_path}")

    ## Write all community files to file
    output_file_path = os.path.join(save_dir, "combined_community.md")
    with open(output_file_path, "w") as output_file:
        output_file.write(combined_community)

    print(f"combined_community.py files into {output_file_path}")

    ## Write all experimental files to file
    output_file_path = os.path.join(save_dir, "combined_experimental.md")
    with open(output_file_path, "w") as output_file:
        output_file.write(combined_experimental)

    print(f"combined_experimental.md files into {output_file_path}")

    ## Write all examples files to file
    output_file_path = os.path.join(save_dir, "combined_examples.md")
    with open(output_file_path, "w") as output_file:
        output_file.write(combined_examples)

    print(f"combined_examples.md files into {output_file_path}")

    ## Write all files to file
    output_file_path = os.path.join(save_dir, "combined_content.md")
    with open(output_file_path, "w") as output_file:
        output_file.write(combined_content)

    print(f"combined_content.md files into {output_file_path}")

    ##########

    ## Write all core+standard files to file
    output_file_path = os.path.join(save_dir, "combined_core_standard.md")
    output = combined_core + combined_standard
    # print(output)
    with open(output_file_path, "w") as output_file:
        output_file.write(output)

    print(f"combined_core_standard.md files into {output_file_path}")

    ## Write all core+standard+community files to file
    output_file_path = os.path.join(save_dir, "combined_core_standard_community.md")
    output = combined_core + combined_standard + combined_community
    # (output)
    with open(output_file_path, "w") as output_file:
        output_file.write(output)

    print(f"combined_core_standard.md files into {output_file_path}")

    ####


if __name__ == "__main__":
    get_all_base_files("../swarmauri", "../combined")
