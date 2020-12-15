from enum import Enum
from typing import Dict, Iterator

from display import Color, Colors
from .npc import NPCHandle


class Interest(Enum):
    No = 0
    Friend = 1
    Love = 2

    def color(self) -> Color:
        if self == Interest.No:
            return Colors.NPCNoInterest
        elif self == Interest.Friend:
            return Colors.NPCFriend
        else:
            return Colors.NPCLove

    def __lt__(self, other: "Interest"):
        return self.value < other.value


class InterestTracker(object):
    def __init__(self):
        self._interest_level: Dict[NPCHandle, Interest] = {}

    def tab(self, handle: NPCHandle) -> Interest:
        existing = self[handle]
        new = (
            Interest.Friend
            if existing == Interest.No
            else Interest.Love
            if existing == Interest.Friend
            else Interest.No
        )
        self[handle] = new
        return new

    def friends_list(self) -> Iterator[NPCHandle]:
        for npch in self._interest_level:
            yield npch

    def __delitem__(self, handle: NPCHandle):
        assert isinstance(handle, NPCHandle)
        self[handle] = Interest.No

    def __getitem__(self, handle: NPCHandle) -> Interest:
        assert isinstance(handle, NPCHandle)
        return self._interest_level.get(handle, Interest.No)

    def __setitem__(self, handle: NPCHandle, interest: Interest):
        assert isinstance(handle, NPCHandle)
        assert isinstance(interest, Interest)

        old_interest = self._interest_level.get(handle, Interest.No)
        if interest is Interest.No:
            if handle in self._interest_level:
                del self._interest_level[handle]
        else:
            self._interest_level[handle] = interest
