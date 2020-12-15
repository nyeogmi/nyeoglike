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
        from .scene_flags import SceneFlag

        assert verb in Verbs.ALL
        assert isinstance(args, Tuple)
        assert all(
            isinstance(
                a, (str, EMHandle, NotificationHandle, NPCHandle, ClaimBox, SceneFlag)
            )
            for a in args
        )

        return cls(verb, args)


class Verbs(object):
    Claim = "Claim"
    Tick = "Tick"
    AddFlag = "AddFlag"

    ALL = {Claim, Tick, AddFlag}
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
    from .scene_flags import SceneFlag

    Arg = Union[
        str,
        EMHandle,
        NotificationHandle,
        NPCHandle,
        ClaimBox,
        SceneFlag,
    ]
