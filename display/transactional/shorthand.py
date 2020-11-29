from ..keys import Key
from ..screen import Drawer
from .transactional import Client


class IO(object):
    def __init__(self, client: Client):
        self._client = client

    def draw(self) -> Drawer:
        return self._client.screen.draw()

    def lock(self):
        return self._client.screen.lock()

    def getch(self) -> Key:
        return self._client.getch()

    def sleep(self, t: float):
        self._client.sleep(t)
