from ds.gensym import Gensym, Sym
from typing import Dict, List, NamedTuple, Optional, Union, TYPE_CHECKING


class NotificationHandle(NamedTuple):
    ident: Sym


class Notifications(object):
    def __init__(self):
        self._active: List[Notification] = []
        self._sym = Gensym("NOT")

    def send(self, msg: Union[str, "EMHandle"], source: Optional["NPCHandle"] = None) -> NotificationHandle:
        from .eventmonitor import EMHandle
        assert isinstance(msg, (str, EMHandle))

        handle = NotificationHandle(self._sym.gen())
        self._active.append(Notification(ident=handle, message=msg, source=source))
        return handle

    def acknowledge(self, world: "World", handle: NotificationHandle, yes):
        from .eventmonitor import EMHandle

        for i, n in enumerate(self._active):
            if n.ident == handle:
                ix = i
                break
        else:
            return

        # you can't actually say "no" to a normal notif
        if isinstance(self._active[ix].message, str) and not yes:
            return

        notif = self._active.pop(ix)
        if notif and notif.message and isinstance(notif.message, EMHandle):
            handle = notif.message
            if yes:
                world.eventmonitors.accept_quest(handle)
            else:
                world.eventmonitors.ignore_quest(handle)

    # TODO: Order?
    def active_notifications(self) -> List["Notification"]:
        return list(self._active)

    def last_notification(self) -> Optional["Notification"]:
        if len(self._active):
            return self._active[-1]
        return None


class Notification(NamedTuple):
    ident: NotificationHandle
    message: Union[str, "EMHandle"]
    source: Optional["NPCHandle"]


if TYPE_CHECKING:
    from .eventmonitor import EMHandle
    from .npc import NPCHandle
    from .world import World
