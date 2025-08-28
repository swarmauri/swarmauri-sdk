
class GithubStorageAdapter:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def upload(self, path: str, dest: str) -> str:
        return f"github://{dest}"
