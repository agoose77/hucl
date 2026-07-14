from typing import cast, NewType, ParamSpec, TypeVar, Callable, Protocol
from ..sansio import SansioImpl
from ..drivers import sync_driver, async_driver

APIUrl = NewType("APIUrl", str)


def ensure_api_url(maybe_url: str) -> APIUrl:
    return cast(APIUrl, maybe_url.rstrip("/"))


P = ParamSpec("P")
T = TypeVar("T")


class FlowLike[**P, T](Protocol):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> SansioImpl[T]: ...

    def sync(self, *args: P.args, **kwargs: P.kwargs) -> T: ...

    async def asyn(self, *args: P.args, **kwargs: P.kwargs) -> T: ...


def flow(impl_factory: Callable[P, SansioImpl[T]]) -> FlowLike[P, T]:
    """
    Decorator for flows.

    Provides .sync and .asyn factories for easy setup.
    """

    def sync_factory(*args, **kwargs):
        impl = impl_factory(*args, **kwargs)
        return sync_driver(impl)

    def async_factory(*args, **kwargs):
        impl = impl_factory(*args, **kwargs)
        return async_driver(impl)

    impl_factory.sync = sync_factory  # type: ignore
    impl_factory.asyn = async_factory  # type: ignore

    return cast(FlowLike[P, T], impl_factory)
