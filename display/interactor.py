from ds.vecs import V2

from .keys import Key
from .screen import Screen

from typing import Protocol, runtime_checkable


@runtime_checkable
class Interactor(Protocol):
    def view(self) -> Screen:
        raise NotImplementedError()

    def handle_key(self, key: Key):
        raise NotImplementedError()

    def should_quit(self):
        raise NotImplementedError()
