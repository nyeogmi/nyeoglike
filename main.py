import display.outputs.pygame

from display import DoubleWide, Key, Screen, transact, IO
from ds.vecs import V2
from unique.level import UnloadedLevel, SpawnNPC
from unique.scheduling import ScheduleItem
from unique.sitemode import sitemode
from unique.world import World


def main(io: IO):
    w = World()
    from unique.level.gen import apartment
    level = apartment()

    npc1 = w.npcs.generate()
    npc2 = w.npcs.generate()
    npc3 = w.npcs.generate()

    w.activate_level(level, [SpawnNPC(npc1, ScheduleItem.HomeSleep), SpawnNPC(npc2, ScheduleItem.HomeSleep)])
    sitemode(io, w)


if __name__ == "__main__":
    size = V2.new(80, 30)  # with double-tall characters, this is 4:3
    screen = Screen(size)

    interactor = transact(screen, main)
    display.outputs.pygame.start(interactor)
