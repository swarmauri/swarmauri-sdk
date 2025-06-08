class FileStorageAdapter:
    def __init__(self, output_dir: str = "./peagen_artifacts", **kwargs):
        self.output_dir = output_dir
        self.kwargs = kwargs

    def upload(self, path: str, dest: str) -> str:
        return f"{self.output_dir}/{dest}"
