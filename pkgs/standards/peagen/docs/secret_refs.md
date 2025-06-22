# Using `secretRef` for LLM Credentials

Peagen can load LLM API keys via the `secrets` plugin group instead of
hardcoding them in your configuration files. Any LLM definition may specify a
`secretRef` like `env:OPENAI_API_KEY` in place of an `api_key` value.

When Peagen encounters a `secretRef` it resolves the value using the configured
secret provider. The default provider `EnvSecret` reads from environment
variables. You can register custom providers under the
`peagen.plugins.secret_drivers` entry point group.

```yaml
kind: llm-config
id: openai-gpt4o
provider: openai
params:
  name: gpt-4o
  temperature: 0.7
  max_tokens: 3000
secretRef: env:OPENAI_API_KEY
```

At runtime the API key will be pulled from `OPENAI_API_KEY` and passed to the
OpenAI client. Other providers may fetch secrets from external stores.
