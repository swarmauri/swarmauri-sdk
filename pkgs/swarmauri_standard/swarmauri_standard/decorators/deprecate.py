import warnings
import functools


def _construct_deprecation_message(
    item_type: str, item_name: str, since: str, removed_in: str, alternative: str = None
) -> str:
    """
    Helper function to construct a deprecation message.

    :param item_type: A string indicating what is being deprecated (e.g. "class", "method", "import path").
    :param item_name: The name of the item (e.g. "OldClass", "my_old_module").
    :param since: Version when deprecation started.
    :param removed_in: Version when the deprecated item will be removed.
    :param alternative: Suggested replacement, or None if no replacement exists.
    :return: A formatted warning message.
    """
    base_msg = (
        f"The {item_type} '{item_name}' is deprecated as of version {since} "
        f"and will be removed in version {removed_in}. "
    )
    if alternative:
        base_msg += f"Use '{alternative}' instead."
    else:
        base_msg += "No replacement is available."
    return base_msg


def deprecated_import_path(
    item_name: str, since: str, removed_in: str, alternative: str = None
):
    """
    A decorator to trigger a DeprecationWarning at import time for a deprecated import path.

    How It Works:
    -------------
    1. You apply this decorator to a dummy class (or function) at the top-level of the
       deprecated module.
    2. When the module is imported, Python reads the decorated class, triggering
       this decorator's code immediately, thus issuing the warning.

    Example Usage in old_module.py:
    -------------------------------
        from my_deprecations import deprecate_import_path

        @deprecate_import_path(
            item_name='old_module',
            since='1.0.0',
            removed_in='2.0.0',
            alternative='new_module'
        )
        class _ImportDeprecationTrigger:
            # This class is never actually used; it just triggers the warning at import time.
            pass

        def some_old_function():
            return "Doing old stuff..."

    Then, any code `import old_module` will emit a DeprecationWarning (provided
    DeprecationWarnings are not filtered out by default).
    """
    # Construct the warning message once, outside the inner decorator
    warning_msg = _construct_deprecation_message(
        item_type="import path",
        item_name=item_name,
        since=since,
        removed_in=removed_in,
        alternative=alternative,
    )

    def decorator(obj):
        # Trigger the warning at import time (when Python first sees the decorated object).
        warnings.warn(
            warning_msg,
            category=DeprecationWarning,
            stacklevel=2,  # Ensures warning points to the user's import line (or near it).
        )
        return obj  # Return the object unmodified (usually a dummy class).

    return decorator


def deprecated_class(since: str, removed_in: str, alternative: str = None):
    """
    Class decorator that marks the class as deprecated. A DeprecationWarning
    is raised whenever an instance of the class is created.
    """

    def decorator(cls):
        original_init = cls.__init__
        item_name = cls.__name__

        @functools.wraps(original_init)
        def new_init(self, *args, **kwargs):
            message = _construct_deprecation_message(
                item_type="class",
                item_name=item_name,
                since=since,
                removed_in=removed_in,
                alternative=alternative,
            )
            warnings.warn(message, category=DeprecationWarning, stacklevel=2)
            return original_init(self, *args, **kwargs)

        cls.__init__ = new_init
        return cls

    return decorator


def deprecated_method(since: str, removed_in: str, alternative: str = None):
    """
    Method (or function) decorator that raises a DeprecationWarning whenever
    the decorated method is called.
    """

    def decorator(func):
        item_name = func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            message = _construct_deprecation_message(
                item_type="method",
                item_name=item_name,
                since=since,
                removed_in=removed_in,
                alternative=alternative,
            )
            warnings.warn(message, category=DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator
