from enum import Enum
from typing import TYPE_CHECKING, Dict, List, NamedTuple, Optional, Union

from ds.gensym import Gensym, Sym


class NotificationHandle(NamedTuple):
    ident: Sym


class NotificationReason(Enum):
    Misc = 0
    AnnounceQuest = 1
    FinalizeQuest = 2


class Notification(NamedTuple):
    ident: NotificationHandle
    message: Union[str, "EMHandle"]
    reason: NotificationReason
    source: Optional["NPCHandle"]


class Notifications(object):
    def __init__(self):
        self._active: List[Notification] = []
        self._sym = Gensym("NOT")

    def send(
        self,
        msg: Union[str, "EMHandle"],
        reason: NotificationReason = NotificationReason.Misc,
        source: Optional["NPCHandle"] = None,
    ) -> NotificationHandle:
        from .eventmonitor import EMHandle
        from .npc import NPCHandle

        assert isinstance(msg, (str, EMHandle))
        assert isinstance(reason, NotificationReason)
        assert source is None or isinstance(source, NPCHandle)

        handle = NotificationHandle(self._sym.gen())
        self._active.append(
            Notification(ident=handle, message=msg, reason=reason, source=source)
        )
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
            if notif.reason == NotificationReason.AnnounceQuest:
                if yes:
                    world.eventmonitors.accept_quest(notif.message)
                else:
                    world.eventmonitors.ignore_quest(notif.message)

            elif notif.reason == NotificationReason.FinalizeQuest:
                world.eventmonitors.finalize_quest(notif.message)

    # TODO: Order?
    def active_notifications(self) -> List["Notification"]:
        return list(self._active)

    def last_notification(self) -> Optional["Notification"]:
        if len(self._active):
            return self._active[-1]
        return None

    def remove_for(
        self, quest: "EMHandle", reason: Optional["NotificationReason"] = None
    ):
        from .eventmonitor import EMHandle

        assert isinstance(quest, EMHandle)
        assert reason is None or isinstance(reason, NotificationReason)

        ixs = [
            ix
            for ix, notif in enumerate(self._active)
            if notif.message == quest
            and (notif.reason == reason if reason is not None else True)
        ]
        for ix in ixs[::-1]:
            self._active.pop(ix)


if TYPE_CHECKING:
    from .eventmonitor import EMHandle
    from .npc import NPCHandle
    from .world import World
