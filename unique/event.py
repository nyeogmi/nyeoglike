from typing import NamedTuple, Tuple, Union


class Event(NamedTuple):
    verb: str
    args: Tuple["Arg", ...]

    @classmethod
    def new(cls, verb: str, args: Tuple["Arg", ...]) -> "Event":
        from .eventmonitor import EMHandle
        from .inventory import ClaimBox
        from .notifications import NotificationHandle
        from .npc import NPCHandle

        assert verb in Verbs.ALL
        assert isinstance(args, Tuple)
        assert all(isinstance(a, (str, EMHandle, NotificationHandle, NPCHandle, ClaimBox)) for a in args)

        return cls(verb, args)


class Verbs(object):
    Claim = "Claim"
    Tick = "Tick"

    ALL = {
        Claim,
        Tick
    }
    QUEST_ONLY = {Claim}

    @classmethod
    def quest_only(cls, verb: str):
        return verb in cls.QUEST_ONLY


# -- Typechecking --
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .eventmonitor import EMHandle
    from .inventory import ClaimBox
    from .notifications import NotificationHandle
    from .npc import NPCHandle

    Arg = Union[
        str,
        EMHandle,
        NotificationHandle,
        NPCHandle,
        ClaimBox,
    ]


