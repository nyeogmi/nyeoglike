from typing import List, Protocol, runtime_checkable

from ds.vecs import V2

from .keys import Key
from .screen import Screen


@runtime_checkable
class Interactor(Protocol):
    def view(self) -> (Screen, bool):  # bool: whether it is changed
        raise NotImplementedError()

    def mark_updated(self):
        raise NotImplementedError()

    def handle_keys(self, keys: List[Key]):
        raise NotImplementedError()

    def should_quit(self):
        raise NotImplementedError()
