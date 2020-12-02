import display.outputs.pygame

from display import DoubleWide, Key, Screen, transact, IO
from ds.vecs import V2
from unique.level import Level
from unique.world import World
from unique.sitemode import sitemode


def main(io: IO):
    w = World()
    from unique.level.gen import apartment
    level = apartment()
    w.activate_level(level)
    sitemode(io, w)


if __name__ == "__main__":
    size = V2.new(80, 30)  # with double-tall characters, this is 4:3
    screen = Screen(size)

    interactor = transact(screen, main)
    display.outputs.pygame.start(interactor)
