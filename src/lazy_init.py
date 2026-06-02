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

    @wraps(init)
    def new_init(self: Any, *args: Any, **kwargs: Any) -> None:
        # Bind the call to the signature and fill in any defaults, so that
        # parameters with default values are assigned too (not just the ones
        # explicitly passed).
        bound = sig.bind(self, *args, **kwargs)
        bound.apply_defaults()
        for name, value in bound.arguments.items():
            if name == 'self':
                continue
            kind = sig.parameters[name].kind
            if kind is inspect.Parameter.VAR_KEYWORD:
                # **kwargs: assign each captured keyword as its own attribute.
                for kwarg_name, kwarg_value in value.items():
                    setattr(self, kwarg_name, kwarg_value)
            elif kind is inspect.Parameter.VAR_POSITIONAL:
                # *args has no natural attribute name; skip it.
                continue
            else:
                setattr(self, name, value)

        # Call original __init__
        init(self, *args, **kwargs)

    return new_init  # type: ignore[return-value]
