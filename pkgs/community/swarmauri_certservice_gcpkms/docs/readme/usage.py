from swarmauri_certservice_gcpkms import GcpKmsCertService
from swarmauri_core.crypto.types import KeyRef

service = GcpKmsCertService()
key = KeyRef(
    kid="projects/my-project/locations/us-central1/keyRings/pki/cryptoKeys/root/cryptoKeyVersions/1"
)

print(service.supports()["features"])
