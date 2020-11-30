from ds.vecs import V2

from .keys import Key
from .screen import Screen

from typing import Protocol, runtime_checkable


@runtime_checkable
class Interactor(Protocol):
    def view(self) -> (Screen, bool):  # bool: whether it is changed
        raise NotImplementedError()

    def handle_key(self, key: Key):
        raise NotImplementedError()

    def should_quit(self):
        raise NotImplementedError()
