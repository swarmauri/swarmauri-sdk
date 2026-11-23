from swarmauri_vectorstore_fs import FsVectorStore

store = FsVectorStore(root_path=".", mode="chunk")
store.build_index()
results = store.retrieve("vector store registration", top_k=3)

for document in results:
    print(document.id, document.metadata["relative_path"])
