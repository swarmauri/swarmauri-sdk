from swarmauri.utils.LazyLoader import LazyLoader

# List of conversations names (file names without the ".py" extension) and corresponding class names
conversations_files = [
    ("swarmauri.conversations.concrete.Conversation", "Conversation"),
    (
        "swarmauri.conversations.concrete.MaxSystemContextConversation",
        "MaxSystemContextConversation",
    ),
    ("swarmauri.conversations.concrete.MaxSizeConversation", "MaxSizeConversation"),
    (
        "swarmauri.conversations.concrete.SessionCacheConversation",
        "SessionCacheConversation",
    ),
]

# Lazy loading of conversations classes, storing them in variables
for module_name, class_name in conversations_files:
    globals()[class_name] = LazyLoader(module_name, class_name)

# Adding the lazy-loaded conversations classes to __all__
__all__ = [class_name for _, class_name in conversations_files]
