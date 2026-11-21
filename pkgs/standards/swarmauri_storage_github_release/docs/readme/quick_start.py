from io import BytesIO

from pydantic import SecretStr

from swarmauri_storage_github_release import GithubReleaseStorageAdapter

adapter = GithubReleaseStorageAdapter(
    token=SecretStr("ghp_example-token"),
    org="example-org",
    repo="example-repo",
    tag="v1.0.0",
    prefix="artifacts",
    release_name="Example release",
    message="Artifacts published by our workflow.",
)

print(adapter.root_uri)

uri = adapter.upload("artifact.txt", BytesIO(b"important payload"))
downloaded_payload = adapter.download("artifact.txt").read()
assets = list(adapter.iter_prefix(""))

print(uri)
print(downloaded_payload)
print(assets)
