![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/dm/swarmauri" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/swarmauri/README.md">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/swarmauri/README.md&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
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
- **Intensional and Extensional Programming**: Leverages both rule-based (intensional) and set-based (extensional) approaches to building and manipulating complex data structures, offering developers a wide range of tools for system design.

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

### Plugin Manager
- [plugin_manager.py](swarmauri/plugin_manager.py): Oversees the loading, initialization, and management of plugins to extend the functionality of the Swarmauri framework.

## Contributing

Contributions are welcome! If you'd like to add a new feature, fix a bug, or improve documentation, kindly go through the [contributions guidelines](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) first.
