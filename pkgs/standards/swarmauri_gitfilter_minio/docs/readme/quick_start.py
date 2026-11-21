from swarmauri_gitfilter_minio import MinioFilter

# Create a filter from a connection string. The scheme `minios://` will use
# HTTPS while `minio://` uses plain HTTP.
filt = MinioFilter.from_uri("minio://localhost:9000/my-bucket/prefix")

# Upload a file and retrieve its URI
with open("README.md", "rb") as fh:
    uri = filt.upload("docs/README.md", fh)

# Download the file back into memory
buffer = filt.download("docs/README.md")
data = buffer.read()
