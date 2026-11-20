from swarmauri_standard.documents.Document import Document
from swarmauri_vectorstore_git import GitVectorStore

store = GitVectorStore(
    repo_path=".",
    scope="all_refs",
    document_kinds=("commit", "log"),
)

store.build_index()
results = store.retrieve("oauth token bug", top_k=3)

for document in results:
    print(document.metadata["oid"], document.metadata["kind"])
    print(document.content[:200])
