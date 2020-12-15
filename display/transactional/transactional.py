# TODO: Use plain lists instead
import time
from typing import Callable, List

from greenlet import greenlet

from ds.vecs import V2

from ..interactor import Interactor
from ..keys import Key
from ..screen import Drawer, Screen


class UpdateTracker(object):
    def __init__(self):
        self._updated = True

    def mark_updated(self):
        self._updated = True

    def pop_updated(self):
        upd = self._updated
        self._updated = False
        return upd


class Client(object):
    def __init__(
        self, screen: Screen, host_thread: greenlet, updated: UpdateTracker, keys: list
    ):
        assert isinstance(screen, Screen)
        assert isinstance(host_thread, greenlet)
        assert isinstance(updated, UpdateTracker)
        assert isinstance(keys, list)

        self._screen = screen
        self._host_thread = host_thread
        self._updated = updated
        self._keys = keys
        self._last_wake_at = 0.0

    @property
    def screen(self):
        return self._screen

    def draw(self) -> Drawer:
        return self._screen.draw()

    def getch(self) -> Key:
        while True:
            if len(self._keys) == 0:
                self._updated.mark_updated()
                self._notify_host()
                continue

            recv = self._keys.pop(0)

            if isinstance(recv, Key):
                return recv
            else:
                raise NotImplementedError("don't know what %s is" % (recv,))

    def _notify_host(self):
        self._host_thread.switch()


class Host(Interactor):
    def __init__(
        self, screen: Screen, thread: greenlet, updated: UpdateTracker, keys: list
    ):
        assert isinstance(screen, Screen)
        assert isinstance(thread, greenlet)
        assert isinstance(updated, UpdateTracker)
        assert isinstance(keys, list)

        self._screen = screen
        self._thread = thread
        self._updated = updated
        self._keys = keys

    def view(self) -> (Screen, bool):
        return self._screen, self._updated.pop_updated()

    def mark_updated(self):
        self._updated.mark_updated()

    def handle_keys(self, keys: List[Key]):
        assert isinstance(keys, list) and all(isinstance(key, Key) for key in keys)

        if len(keys) == 0:
            return

        self._keys.extend(keys)
        self._thread.switch()

    def should_quit(self) -> bool:
        return False
        # TODO
        # if not self._thread.is_alive():
        # return True
        # return False


def transact(screen: Screen, game_f, host_f):
    from .shorthand import IO

    keys = []

    updated = UpdateTracker()
    host_greenlet = greenlet(lambda: host_f(host))
    client = Client(screen, host_greenlet, updated, keys=keys)
    game_greenlet = greenlet(lambda: game_f(IO(client)))
    host = Host(screen, game_greenlet, updated, keys=keys)

    game_greenlet.switch()
