"""Decorator to automatically assign __init__ parameters to instance attributes.

This decorator wraps an __init__ method to automatically bind all parameters
to self attributes, eliminating boilerplate assignment code.

Source: https://stackoverflow.com/questions/5048329/python-decorator-for-automatic-binding-init-arguments

Example:
    @lazy_init
    def __init__(self, name, age, email):
        # No need for self.name = name, etc.
        pass
"""

import inspect
from functools import wraps
from typing import Callable, TypeVar, Any

F = TypeVar('F', bound=Callable[..., None])


def lazy_init(init: F) -> F:
    """Decorator that automatically assigns __init__ parameters to self attributes.

    Args:
        init: The __init__ method to wrap

    Returns:
        Wrapped __init__ method that auto-assigns parameters
    """
    sig = inspect.signature(init)
    param_names = [
        name for name in sig.parameters.keys()
        if name != 'self'
    ]

    @wraps(init)
    def new_init(self: Any, *args: Any, **kwargs: Any) -> None:
        # Bind positional arguments
        for name, value in zip(param_names, args):
            setattr(self, name, value)

        # Bind keyword arguments
        for name, value in kwargs.items():
            setattr(self, name, value)

        # Call original __init__
        init(self, *args, **kwargs)

    return new_init  # type: ignore[return-value]
