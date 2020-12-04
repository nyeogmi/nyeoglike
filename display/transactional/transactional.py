from ..interactor import Interactor
from ..keys import Key
from ..screen import Drawer, Screen
from ds.vecs import V2
from typing import Callable
from greenlet import greenlet

# TODO: Use plain lists instead
from queue import Queue, Empty

import time


class Client(object):
    def __init__(self, screen: Screen, host_thread: greenlet, keys: Queue):
        assert isinstance(screen, Screen)
        assert isinstance(host_thread, greenlet)
        assert isinstance(keys, Queue)

        self._screen = screen
        self._host_thread = host_thread
        self._keys = keys
        self._last_wake_at = 0.0

    @property
    def screen(self):
        return self._screen

    def draw(self) -> Drawer:
        return self._screen.draw()

    def getch(self) -> Key:
        while True:
            try:
                got = self._keys.get_nowait()
            except Empty:
                self._notify_host()
                continue

            (t, recv) = got

            if t < self._last_wake_at:
                continue

            if isinstance(recv, Key):
                return recv
            else:
                raise NotImplementedError("don't know what %s is" % (recv,))

    def _notify_host(self):
        self._host_thread.switch()


class Host(Interactor):
    def __init__(self, screen: Screen, thread: greenlet, keys: Queue):
        assert isinstance(screen, Screen)
        assert isinstance(thread, greenlet)
        assert isinstance(keys, Queue)

        self._screen = screen
        self._thread = thread
        self._keys = keys

    def view(self) -> (Screen, bool):
        # TODO: Figure out if it's been updated
        return (self._screen, True)

    def handle_key(self, key: Key):
        assert isinstance(key, Key)
        push_at = time.time()
        self._keys.put((push_at, key))

        self._thread.switch()

    def should_quit(self) -> bool:
        pass
        # TODO
        # if not self._thread.is_alive():
            # return True
        # return False


def transact(screen: Screen, game_f, host_f):
    from .shorthand import IO

    keys = Queue()

    host_greenlet = greenlet(lambda: host_f(host))
    client = Client(screen, host_greenlet, keys=keys)
    game_greenlet = greenlet(lambda: game_f(IO(client)))
    host = Host(screen, thread=game_greenlet, keys=keys)

    game_greenlet.switch()