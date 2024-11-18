__long_desc__ = """
# Swarmauri Standard SDK

The Swarmauri Standard SDK offers a comprehensive suite of tools designed for building distributed, extensible systems using the Swarmauri framework. 

## Standard
- **Base Classes**: Provide a foundation for constructing Swarmauri components, with standardized methods and properties.
- **Mixins**: Reusable code fragments designed to be integrated into various classes, offering shared functionality across different components.
- **Concrete Classes**: Ready-to-use, pre-implemented classes that fulfill standard system needs while adhering to Swarmauri principles. **These classes are the first in line for ongoing support and maintenance, ensuring they remain stable, performant, and up to date with future SDK developments.**

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

Visit us at: https://swarmauri.com
Follow us at: https://github.com/swarmauri 
"""
from .__version__ import __version__

__all__ = [
    "__version__",
    # other packages you want to expose
]
