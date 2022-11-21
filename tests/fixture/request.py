"""
Pipeline related fixtures.
"""

import typing

import banshee
import mock

T = typing.TypeVar("T")


def mock_handler(return_value: typing.Any = None) -> typing.Any:
    """
    Mock handle message.
    """

    async def handler(_: typing.Any) -> typing.Any:
        ...  # pragma: no cover

    m = mock.create_autospec(handler, spec_set=True)
    m.return_value = return_value

    return m


def mock_factory() -> typing.Any:
    """
    Mock factory.
    """

    def factory(reference: banshee.HandlerReference[T]) -> banshee.Handler[T]:
        return reference.handler

    return mock.create_autospec(factory, spec_set=True, side_effect=factory)


def mock_locator(
    return_value: typing.Optional[
        typing.List[banshee.HandlerReference[typing.Any]]
    ] = None,
) -> typing.Any:
    """
    Mock locator.
    """
    m = mock.create_autospec(banshee.HandlerLocator, spec_set=True)
    m.subscribers_for.return_value = return_value or []

    return m
