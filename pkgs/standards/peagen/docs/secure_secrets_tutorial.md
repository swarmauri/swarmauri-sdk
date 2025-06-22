# Secure Secrets Quickstart

This tutorial shows how to manage encrypted secrets with Peagen.

## 1. Create and upload your key

Generate a local key pair. Provide a passphrase if desired:

```bash
peagen keys create --passphrase
```

Upload the public key to your gateway:

```bash
peagen login --passphrase <PASS> --gateway-url http://localhost:8000/rpc
```

## 2. Add a secret

Store a secret locally, encrypting it for the gateway and worker:

```bash
peagen local secrets add OPENAI_API_KEY sk-... \
  --recipients /path/to/gateway_pub.asc \
  --recipients /path/to/worker_pub.asc
```

To keep the secret on the gateway, run:

```bash
peagen remote secrets add OPENAI_API_KEY sk-... \
  --recipient worker_pub.asc --gateway-url http://localhost:8000/rpc
```

## 3. Submit a run

```bash
peagen remote --gateway-url http://localhost:8000/rpc process projects.yaml --watch
```

## 4. Push commits using a deploy key

Store your private deploy key as an encrypted secret on the gateway:

```bash
peagen remote secrets add DEPLOY_KEY "$(cat ~/.ssh/id_rsa)" \
  --recipient worker_pub.asc --gateway-url http://localhost:8000/rpc
```

Configure your worker with the secret name so pushes use the key:

```bash
export DEPLOY_KEY_SECRET=DEPLOY_KEY
```

Workers will automatically fetch the deploy key secret when pushing.

See [call_flows/peagen_secure_secrets_arch.mmd](call_flows/peagen_secure_secrets_arch.mmd) for the encryption architecture.
