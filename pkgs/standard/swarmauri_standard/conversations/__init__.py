from swarmauri.utils._lazy_import import _lazy_import

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
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded conversations classes to __all__
__all__ = [class_name for _, class_name in conversations_files]
