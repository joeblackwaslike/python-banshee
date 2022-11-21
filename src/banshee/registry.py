"""
A registry of handlers.
"""
from __future__ import annotations

import collections
import collections.abc
import inspect
import typing

import banshee.errors
import banshee.request
import typing_extensions

T = typing.TypeVar("T")
H = typing.TypeVar(
    "H",
    bound=typing.Union[typing.Type, collections.abc.Callable],
)


class Registry(banshee.request.HandlerLocator):
    """
    Registry.

    Provides a means to register and lookup objects.
    """

    __slots__ = ("_subscriptions",)

    _subscriptions: collections.defaultdict[
        type,
        list[banshee.request.HandlerReference[typing.Any]],
    ]

    def __init__(self) -> None:
        self._subscriptions = collections.defaultdict(list)

    def _name_for(self, target: object) -> str:
        """
        Name for reference.

        :param target: object for which to infer a name

        :returns: unique name
        """
        # pylint: disable=too-many-return-statements

        if target is Ellipsis:
            # return strings as strings

            return "..."

        if target is type(None):
            # return strings as strings

            return "None"

        if typing_extensions.get_args(target):
            # make sure we capture generic arguments

            obj = typing.cast(typing.Any, target)
            return type(obj).__repr__(obj)

        if inspect.isclass(target) or inspect.isfunction(target):
            # plain old functions and classes

            if target.__module__ == "builtins":
                # no module prefix for built-in types

                return target.__name__

            return f"{target.__module__}.{target.__name__}"

        return target.__name__ if isinstance(target, typing.TypeVar) else repr(target)

    def subscribe(
        self,
        handler: typing.Type | collections.abc.Callable[..., typing.Any],
        to: typing.Type,
        name: str | None = None,
    ) -> None:
        """
        Subscribe.

        Add a subscription for a function or class to a request class.

        When no name is provided, then the registry will try and infer a unique name
        based on the module and name of the decorated function or class.

        :param handler: callable or type to act as subscriber
        :param to: type of request for subscription
        :param name: optional unique name for the handler
        """
        self._subscriptions[to].append(
            banshee.request.HandlerReference(
                name=name or self._name_for(handler),
                handler=handler,
            )
        )

    def subscribe_to(
        self,
        to: typing.Type,
        name: str | None = None,
    ) -> collections.abc.Callable[[H], H]:
        """
        Subscribe to.

        A decorator to subscribe the decorated function or class to requests of the
        specified type.

        When no name is provided, then the registry will try and infer a unique name
        based on the module and name of the decorated function or class.

        :param to: type of request for subscription
        :param name: optional unique name for the handler

        :returns: decorator function
        """

        def _decorator(handler: H) -> H:
            self.subscribe(handler, to=to, name=name)

            return handler

        return _decorator

    def subscribers_for(
        self,
        message: banshee.message.Message[T],
    ) -> collections.abc.Iterable[banshee.request.HandlerReference[T]]:
        return tuple(self._subscriptions.get(type(message.request), []))
