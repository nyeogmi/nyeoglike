import display.outputs.pygame
from display import IO, DoubleWide, Key, Screen, transact
from ds.vecs import V2
from unique.tools.item_editor import main


if __name__ == "__main__":
    size = V2.new(80, 30)  # with double-tall characters, this is 4:3
    screen = Screen(size)

    transact(screen, main, lambda interactor: display.outputs.pygame.start(interactor))
