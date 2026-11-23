```plaintext
User Import Request
        |
        v
SwarmauriImporter.find_spec
        |
        +-----------------------------+
        | Is Namespace 'swarmauri.*'? |
        +-----------------------------+
        | Yes                         | No
        v                             v
   REGISTRY Lookup                Skip Importer
        |
        +-----------------------------+
        | Found in REGISTRY?          |
        +-----------------------------+
        | Yes                         | No
        v                             v
Dynamic Import            SwarmauriImporter._try_discover_plugin
        |                             |
        v                             v
   Resource Loaded   importlib.metadata.entry_points()
                         |
                         v
       Plugin Matches Entry Point?
                 |
       +---------+---------+
       | Yes               | No
       v                   v
Validate & Register     Plugin Not Found
        |
        +-------------------------+
        | First-Class or Second?  |
        +-------------------------+
        | First                  | Second
        v                       v
REGISTRY Update        Dynamic Module Creation
        |
        v
Dynamic Import
        |
        v
Resource Available

```