<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


# Swarmauri Hierarchical Key Provider

Plugin providing a policy-driven composite key provider capable of routing
key operations across multiple child providers. It implements the
`IKeyProvider` interface and exposes a single `HierarchicalKeyProvider`
class.

## Installation

```bash
pip install swarmauri_keyprovider_hierarchical
```
