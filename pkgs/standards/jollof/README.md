# Jollof

A universal plugin management system for managing plugin domains and groups across arbitrary projects. It provides discovery, registration, and instance loading from JSON, YAML, or TOML configurations.

## Features
- Entry point discovery and registration
- Domain and group aware plugin registry
- Configuration based instantiation via Pydantic with JSON/YAML/TOML helpers
- Utilities for dumping plugin configuration to multiple formats

## Usage
```python
from jollof import PluginManager

pm = PluginManager(domain="example")
```
