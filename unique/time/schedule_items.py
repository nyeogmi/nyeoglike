from ..npc import NPCHandle
from .schedule_item import ScheduleItem, _Verb, ALL

HomeFun: ScheduleItem = ALL.verb("HomeFun", type(None), "home, not sleepy")(None)
HomeSleep: ScheduleItem = ALL.verb("HomeSleep", type(None), "home to sleep")(None)
SleepOver: _Verb = ALL.verb("SleepOver", NPCHandle, "sleepover with {arg}")
