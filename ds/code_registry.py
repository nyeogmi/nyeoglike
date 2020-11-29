from typing import Callable, NamedTuple, Generic, TypeVar, Union

_REGISTRY = {}

T = TypeVar("T", Callable, type)


class Ref(Generic[T]):
    _name: str

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def resolve(self) -> T:
        return _REGISTRY[self._name]


def ref(obj: Union[T, str]) -> Union[Ref[T], Callable[[T], Ref[T]]]:
    if isinstance(obj, str):
        return ref_named(obj)
    return ref_unnamed(obj)


def ref_unnamed(obj: T) -> Ref[T]:
    assert isinstance(obj, (Callable, type))
    return ref_named(obj.__name__)(obj)


def ref_named(name) -> Callable[[T], Ref[T]]:
    # TODO: Better error message
    assert name not in _REGISTRY

    def dec(t: T) -> Ref[T]:
        _REGISTRY[name] = t
        return Ref(name)

    return dec
