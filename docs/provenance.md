# Provenance Hashing

Peagen tracks task lineage using canonical SHA-256 hashes. YAML files are
normalised to JSON with sorted keys before hashing. The resulting digest
is stored as a lowercase hexadecimal string.

```python
from pathlib import Path
from peagen.utils import hashing

payload_h = hashing.payload_hash({"foo": "bar"})
rev_h = hashing.revision_hash(None, payload_h)
edge_h = hashing.edge_hash(rev_h, payload_h, "worker-1", None)
root_h = hashing.fanout_root_hash([edge_h])
```
