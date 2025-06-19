class GithubFilter:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def upload(self, path: str, dest: str) -> str:
        return f"github://{dest}"

    def download(self, key: str):
        raise NotImplementedError

    # ---------------------------------------------------------------- oid helpers
    def clean(self, data: bytes) -> str:
        import hashlib
        import io
        oid = "sha256:" + hashlib.sha256(data).hexdigest()
        try:
            self.download(oid)
        except Exception:
            self.upload(io.BytesIO(data), oid)
        return oid

    def smudge(self, oid: str) -> bytes:
        with self.download(oid) as fh:
            return fh.read()
