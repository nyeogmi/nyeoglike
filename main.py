import display.outputs.pygame

from display import DoubleWide, Key, Screen, transact, IO
from ds.vecs import V2
from unique.level import UnloadedLevel, SpawnNPC
from unique.time import ScheduleItem
from unique.sitemode import sitemode
from unique.world import World
from unique.worldmap import Demand, ZoneType


def main(io: IO):
    w = World.generate()
    print([w.npcs.get(i).name for i in w.npcs._all.keys()])  # TODO: Better way to do this for non-debugging in the future

    house1 = w.households.generate(w, 3)
    w.friendships.mingle(w, 5)  # every NPC gets 5 friends

    # level = w.households.get_home(w, house1)
    w.start_time_period()

    level = w.levels.zone(ZoneType.Restaurant, Demand())
    w.activate_level(level)

    sitemode(io, w)


if __name__ == "__main__":
    size = V2.new(80, 30)  # with double-tall characters, this is 4:3
    screen = Screen(size)

    transact(screen, main, lambda interactor: display.outputs.pygame.start(interactor))
