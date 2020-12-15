from ..npc import NPCHandle
from ..social import EnterpriseHandle
from .schedule_item import ALL, DestinationRule, ScheduleItem, _Verb

HomeFun: ScheduleItem = ALL.verb(
    "HomeFun", type(None), "home, not sleepy", DestinationRule.MyHousehold
)(None)
HomeSleep: ScheduleItem = ALL.verb(
    "HomeSleep", type(None), "home to sleep", DestinationRule.MyHousehold
)(None)
HostSleepOver: ScheduleItem = ALL.verb(
    "HostSleepOver", type(None), "host a sleepover", DestinationRule.MyHousehold
)(None)
SleepOver: _Verb = ALL.verb(
    "SleepOver", NPCHandle, "sleepover with {arg}", DestinationRule.Follow
)
GoToWork: _Verb = ALL.verb(
    "GoToWork", EnterpriseHandle, "work at {arg}", DestinationRule.Follow
)
