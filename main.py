import display.outputs.pygame

from display import DoubleWide, Key, Screen, transact, IO
from ds.vecs import V2
from unique.level import UnloadedLevel, SpawnNPC
from unique.scheduling import ScheduleItem
from unique.sitemode import sitemode
from unique.world import World


def main(io: IO):
    w = World.generate()
    print([w.npcs.get(i).name for i in w.npcs._all.keys()])  # TODO: Better way to do this for non-debugging in the future

    house1 = w.households.generate(w, 3)
    level = w.households.get_home(w, house1)
    w.activate_level(level)

    sitemode(io, w)


if __name__ == "__main__":
    size = V2.new(80, 30)  # with double-tall characters, this is 4:3
    screen = Screen(size)

    interactor = transact(screen, main)
    display.outputs.pygame.start(interactor)
