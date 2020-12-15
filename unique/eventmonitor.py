from enum import Enum
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    List,
    NamedTuple,
    Optional,
    Protocol,
    Set,
    runtime_checkable,
)

from ds.gensym import Gensym, Sym

from .event import Event, Verbs
from .notifications import NotificationReason


class EMHandle(NamedTuple):
    ident: Sym


class EventMonitors(object):
    def __init__(self):
        self._active: Dict[EMHandle, "EventMonitor"] = {}
        self._active_keys: Set = (
            set()
        )  # arbitrary set populated by calling key() on EventMonitors
        self._sym = Gensym("EM")

        self._most_recent_status: Dict[EMHandle, QuestStatus] = {}
        self._accepted_quests: List[EMHandle] = []
        self._failed_quests: List[EMHandle] = []
        self._succeeded_quests: List[EMHandle] = []

    def add(
        self, world: "World", constructor: Callable[[EMHandle], "EventMonitor"]
    ) -> Optional[EMHandle]:
        from .world import World

        assert isinstance(world, World)

        handle = EMHandle(self._sym.gen())
        em = constructor(handle)

        if em.key() in self._active_keys:
            return

        assert isinstance(em, EventMonitor)
        self._active[handle] = em
        self._active_keys.add(em.key())

        quest_status = self._active[handle].quest_status(world)
        if quest_status:
            world.notifications.send(
                handle, NotificationReason.AnnounceQuest, quest_status.assigner
            )
            self._accepted_quests.append(handle)

            self._most_recent_status[handle] = quest_status

        return handle

    def most_recent_status(self, quest: EMHandle) -> Optional["QuestStatus"]:
        return self._most_recent_status.get(quest)

    def accept_quest(self, quest: EMHandle):
        assert isinstance(quest, EMHandle)

        # Add if not presumed-accepted
        if quest in self._active and quest not in self._accepted_quests:
            self._accepted_quests.append(quest)

    def ignore_quest(self, quest: EMHandle):
        assert isinstance(quest, EMHandle)

        # Remove if presumed-accepted
        if quest in self._accepted_quests:
            self._accepted_quests.remove(quest)

        # TODO: Remove the claims?

    # TODO: Failed quests? Succeeded quests? Limited N? Sort order?
    def accepted_quests(self) -> List["EMHandle"]:
        return list(self._accepted_quests)

    def notify(self, world: "World", event: "Event"):
        from .inventory import ClaimBox
        from .world import World

        assert isinstance(world, World)
        assert isinstance(event, Event)

        # TODO: Make sure handle order is maintained thru serialization/deserialization, so this remains deterministic
        done_ems = set()

        # TODO: For Claim, iterate in quest precedence order here -- that is, love > friend > normal
        for handle, em in self._active.items():
            quest_status = em.quest_status(world)
            verb = event.verb

            if Verbs.quest_only(verb):
                should_notify = (
                    quest_status and quest_status.outcome == QuestOutcome.InProgress
                )

                if verb == Verbs.Claim and handle not in self._accepted_quests:
                    should_notify = False
            else:
                should_notify = True

            if should_notify:
                if em.notify(world, event) == Done.Done:
                    done_ems.add(handle)

                quest_status = em.quest_status(world)

            if quest_status is not None:
                if quest_status.outcome == QuestOutcome.Failed:
                    done_ems.add(handle)
                    self._failed_quests.append(quest_status)
                    self.send_finalize_quest(world, handle, quest_status)

                elif quest_status.outcome == QuestOutcome.Succeeded:
                    done_ems.add(handle)
                    self._succeeded_quests.append(quest_status)
                    self.send_finalize_quest(world, handle, quest_status)

                self._most_recent_status[handle] = quest_status

            # Don't let anyone else look at this Claim if it's all claimed
            if verb == Verbs.Claim and all(
                i.taken for i in event.args if isinstance(i, ClaimBox)
            ):
                break

        for d in sorted(done_ems):
            self._active_keys.remove(self._active[d].key())
            world.notifications.remove_for(d, NotificationReason.AnnounceQuest)
            del self._active[d]

    def send_finalize_quest(
        self, world: "World", handle: EMHandle, quest_status: "QuestStatus"
    ):
        if (
            handle in self._accepted_quests
            or quest_status.outcome == QuestOutcome.Succeeded
        ):
            # NOTE: Show successes even if the user didn't accept the quest
            world.notifications.send(
                handle, NotificationReason.FinalizeQuest, quest_status.assigner
            )
        else:
            # don't wait for the user
            self.finalize_quest(handle)

    def finalize_quest(self, em: EMHandle):
        assert isinstance(em, EMHandle)
        if em in self._accepted_quests:
            self._accepted_quests.remove(em)


@runtime_checkable
class EventMonitor(Protocol):
    def notify(self, world: "World", event: "Event") -> Optional["Done"]:
        raise NotImplementedError()

    def quest_status(self, world: "World") -> Optional["QuestStatus"]:
        raise NotImplementedError()

    def key(self):
        raise NotImplementedError()


class Done(Enum):
    Done = 0


class QuestOutcome(Enum):
    InProgress = 0
    Succeeded = 1
    Failed = 2


class QuestStatus(NamedTuple):
    name: str
    description: str
    oneliner: str
    outcome: QuestOutcome
    assigner: Optional["NPCHandle"]
    # TODO: The item the quest is about, if it has one?


# -- Typechecking --
if TYPE_CHECKING:
    from .npc import NPCHandle
    from .world import World
