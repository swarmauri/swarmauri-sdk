import os
from swarmauri.documents.concrete.Document import Document

def load_documents_from_folder(self, folder_path: str):
    """Recursively walks through a folder and read documents from all files in a folder."""
    documents = []
    # Traverse through all directories and files
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()
                    document = Document(content=file_content, metadata={"filepath": file_path})
                    documents.append(document)
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON file: {file_name}")
    return documents
