![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/dm/swarmauri" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri.svg"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/l/swarmauri" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/v/swarmauri?label=swarmauri&color=green" alt="PyPI - swarmauri"/></a>
</p>

---

# Swarmauri SDK

The Swarmauri SDK offers a comprehensive suite of tools designed for building distributed, extensible systems using the Swarmauri framework.

## Swarmauri Namespace Microkernel

The `swarmauri` package is implemented as a namespace microkernel. When the
package is imported it registers a custom importer that consults the interface
and plugin citizenship registries to locate actual implementations. This design
keeps the namespace lightweight while still allowing first-party and community
plugins to be discovered and loaded on demand. New resource kinds are declared
in `interface_registry.py`, then mapped to plugin modules via
`plugin_citizenship_registry.py`. For a deeper look at the import flow, see
[`docs/callflow.md`](docs/callflow.md).

## Core 
- **Core Interfaces**: Define the fundamental communication and data-sharing protocols between components in a Swarmauri-based system.

## Standard
- **Base Classes**: Provide a foundation for constructing Swarmauri components, with standardized methods and properties.
- **Mixins**: Reusable code fragments designed to be integrated into various classes, offering shared functionality across different components.
- **Concrete Classes**: Ready-to-use, pre-implemented classes that fulfill standard system needs while adhering to Swarmauri principles. **These classes are the first in line for ongoing support and maintenance, ensuring they remain stable, performant, and up to date with future SDK developments.**

## Community
- **Third-Party Plug-in Integration**: Concrete classes designed to extend the framework’s capabilities by utilizing third-party libraries and plugins.
- **Open Source Contributions**: A collaborative space for developers to contribute new components, plug-ins, and features.

## Experimental
- **In-Development Components**: Early-stage features and components that push the boundaries of the Swarmauri framework, offering innovative solutions that are still in testing phases.

# Features

- **Polymorphism**: Allows for dynamic behavior switching between components, enabling flexible, context-aware system behavior.
- **Discriminated Unions**: Provides a robust method for handling multiple possible object types in a type-safe manner.
- **Serialization**: Efficiently encode and decode data for transmission across different environments and system components, with support for both standard and custom serialization formats.
- **Intensional and Extensional Programming**: The microkernel continues to leverage both rule-based (intensional) patterns and set-based (extensional) plugin discovery, allowing you to build and manipulate complex data structures with ease.

## Use Cases

- **Modular Systems**: Develop scalable, pluggable systems that can evolve over time by adding or modifying components without disrupting the entire ecosystem.
- **Distributed Architectures**: Build systems with distributed nodes that seamlessly communicate using the SDK’s standardized interfaces.
- **Third-Party Integrations**: Extend the system's capabilities by easily incorporating third-party tools, libraries, and services.
- **Prototype and Experimentation**: Test cutting-edge ideas using the experimental components in the SDK, while retaining the reliability of core and standard features for production systems.

# Future Development

The Swarmauri SDK is an evolving platform, and the community is encouraged to contribute to its growth. Upcoming releases will focus on enhancing the framework's modularity, providing more advanced serialization methods, and expanding the community-driven component library.

## Modules Overview

### Importer
- [importer.py](swarmauri/importer.py): Handles the dynamic importing of modules and components within the Swarmauri framework.

### Interface Registry
- [interface_registry.py](swarmauri/interface_registry.py): Manages the registration and lookup of interfaces used for communication between different components.

### Plugin Citizenship Registry
- [plugin_citizenship_registry.py](swarmauri/plugin_citizenship_registry.py): Maintains a registry of plugins and their citizenship status within the Swarmauri ecosystem.

When introducing a new resource kind or class, remember to update both the
`plugin_citizenship_registry.py` and `interface_registry.py` so the framework can
discover and validate your additions.

### Plugin Manager
- [plugin_manager.py](swarmauri/plugin_manager.py): Oversees the loading, initialization, and management of plugins to extend the functionality of the Swarmauri framework.

## Contributing

Contributions are welcome! If you'd like to add a new feature, fix a bug, or improve documentation, kindly go through the [contributions guidelines](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) first.
