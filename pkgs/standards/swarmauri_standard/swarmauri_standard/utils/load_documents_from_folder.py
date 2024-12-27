import os
import logging
import json
from swarmauri_standard.documents.Document import Document


def load_documents_from_folder(folder_path: str, include_extensions=None, exclude_extensions=None,
                               include_folders=None, exclude_folders=None):
    """
    Recursively walks through a folder and reads documents from files based on inclusion and exclusion criteria.
    
    Args:
        folder_path (str): The path to the folder containing files.
        include_extensions (list or None): A list of file extensions to explicitly include (e.g., ["txt", "json"]).
        exclude_extensions (list or None): A list of file extensions to explicitly exclude (e.g., ["log", "tmp"]).
        include_folders (list or None): A list of folder names to explicitly include.
        exclude_folders (list or None): A list of folder names to explicitly exclude.
        
    Returns:
        list: A list of Document objects with content and metadata.
    """
    documents = []
    include_all_files = not include_extensions and not exclude_extensions  # Include all files if no filters are provided
    include_all_folders = not include_folders and not exclude_folders  # Include all folders if no filters are provided

    # Traverse through all directories and files
    for root, dirs, files in os.walk(folder_path):
        # Folder filtering based on include/exclude folder criteria
        current_folder_name = os.path.basename(root)
        if not include_all_folders:
            if include_folders and current_folder_name not in include_folders:
                logging.info(f"Skipping folder due to inclusion filter: {current_folder_name}")
                continue
            if exclude_folders and current_folder_name in exclude_folders:
                logging.info(f"Skipping folder due to exclusion filter: {current_folder_name}")
                continue

        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_extension = file_name.split(".")[-1]
            
            # File filtering based on include/exclude file criteria
            if include_all_files or (include_extensions and file_extension in include_extensions) or \
               (exclude_extensions and file_extension not in exclude_extensions):
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        file_content = f.read()
                        document = Document(content=file_content, metadata={"filepath": file_path})
                        documents.append(document)
                except json.JSONDecodeError:
                    logging.warning(f"Skipping invalid JSON file: {file_name}")
                except Exception as e:
                    logging.error(f"Error reading file {file_name}: {e}")
            else:
                logging.info(f"Skipping file due to file filter: {file_name}")
                
    return documents
