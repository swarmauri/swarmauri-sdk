from azure.identity import DefaultAzureCredential

from swarmauri_certs_azure.certs import AzureKeyVaultCertService

service = AzureKeyVaultCertService(
    "https://example-vault.vault.azure.net/",
    credential=DefaultAzureCredential(),
)

print(service.supports()["features"])
