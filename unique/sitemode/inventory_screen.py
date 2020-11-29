from display import Colors, DoubleWide, Key, Keycodes, IO
from .window import draw_window
from ..item import Resource, Resources
from ..world import World


def show(io: IO, world: World):
    InventoryScreen(io, world).run()


class InventoryScreen(object):
    def __init__(self, io: IO, world: World):
        assert isinstance(io, IO)
        assert isinstance(world, World)

        self.io = io
        self.world = world
        self.done = False

    def run(self):
        with self.io.lock():
            self.io.draw().fade()
            self.draw()

        while True:
            self.do_input()

            if self.done:
                return

            with self.io.lock():
                self.draw()

    def do_input(self):
        input = self.io.getch()

        if input.match(Key.new(Keycodes.Escape)):
            self.done = True
            return

    def draw(self):
        window = draw_window(self.io.draw().goto(4, 7).box(26, 28), fg=Colors.MSGSystem, double=True)
        window.title_bar.copy().fg(Colors.TermFGBold).puts("Inventory")

        window.content.copy().goto(0, 0).fg(Colors.TermFGBold).puts("Resources")
        window.button_bar.copy().fg(Colors.TermFGBold).puts("ESC - Return")

        y = 1
        for resource in Resource:
            amt = self.world.inventory.get(resource)
            if resource in Resources.ESSENTIAL or True or self.world.inventory.get(resource) > 0:
                window.content.copy().goto_xy(0, y).fg(Colors.MSGSystem).puts("\xf9 ").fg(Colors.TermFG).puts(resource.name)

                if resource == Resource.Money:
                    window.content.copy().goto_xy(11, y).fg(Colors.TermFG).puts("$").fg(Colors.TermFGBold).puts("{:,.2f}".format(amt / 100))
                else:
                    window.content.copy().goto_xy(12, y).fg(Colors.TermFGBold).puts(str(amt))
                y += 1
