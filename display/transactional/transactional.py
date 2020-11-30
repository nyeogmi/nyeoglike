from ..interactor import Interactor
from ..keys import Key
from ..screen import Drawer, Screen
from ds.vecs import V2
from threading import Thread
from typing import Callable

from queue import Queue, Empty

import time


class Client(object):
    def __init__(self, screen: Screen, send: Queue, recv: Queue):
        assert isinstance(screen, Screen)
        assert isinstance(send, Queue)
        assert isinstance(recv, Queue)

        self._screen = screen
        self._send = send
        self._recv = recv
        self._last_wake_at = 0.0

    @property
    def screen(self):
        return self._screen

    def draw(self) -> Drawer:
        return self._screen.draw()

    def getch(self) -> Key:
        self._notify_host()

        while True:
            (t, recv) = self._recv.get()

            if t < self._last_wake_at:
                continue

            if isinstance(recv, Key):
                return recv
            else:
                raise NotImplementedError("don't know what %s is" % (recv,))

    def sleep(self, t):
        self._notify_host()
        time.sleep(t)
        self._last_wake_at = time.time()

    def _notify_host(self):
        # this is thread unsafe but it's faster
        self._send.put(self._screen)  # .snapshot())


class Host(Interactor):
    def __init__(self, screen: Screen, thread: Thread, send: Queue, recv: Queue):
        assert isinstance(screen, Screen)
        assert isinstance(thread, Thread)
        assert isinstance(send, Queue)
        assert isinstance(recv, Queue)

        self._screen = screen
        self._thread = thread
        self._send = send
        self._recv = recv

    def view(self) -> (Screen, bool):
        try:
            # TODO: Set an "updated" flag when this is received, only have pygame redraw on update
            self._screen = self._recv.get(timeout=0.0)
            assert isinstance(self._screen, Screen)
            return self._screen, True
        except Empty as e:
            return self._screen, False

    def handle_key(self, key: Key):
        assert isinstance(key, Key)
        push_at = time.time()
        self._send.put((push_at, key))

    def should_quit(self) -> bool:
        if not self._thread.is_alive():
            return True
        return False


def transact(screen: Screen, f) -> Host:
    from .shorthand import IO

    c2h = Queue()
    h2c = Queue()

    client = Client(screen, send=c2h, recv=h2c)
    thread = Thread(target=f, args=(IO(client),))
    thread.daemon = True  # Kill it if program isn't running any more
    host = Host(screen.snapshot(), thread=thread, send=h2c, recv=c2h)
    thread.start()

    return host
