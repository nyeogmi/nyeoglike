from display import Colors, Drawer, DoubleWide, Key, Keycodes, IO, measure_wrap
from ds.vecs import V2, R2
from .scrollbar import Scrollbar, ScrollbarData
from .window import draw_window

from ..item import Resource, Resources
from ..npc import NPCHandle
from ..world import World

from typing import Set, Optional, Protocol, runtime_checkable
from enum import Enum


def show(io: IO, world: World):
    FlyScreen(io, world).run()


class FlyScreen(object):
    def __init__(self, io: IO, world: World):
        assert isinstance(io, IO)
        assert isinstance(world, World)

        self.io = io
        self.world = world
        self.done = False

        self._state = FlyScreenState.Follow

        self.follow_npcs = Scrollbar([], Follow(self))

    def calculate_lists(self):
        all_npcs: Set[NPCHandle] = set()

        # npcs you like
        for handle in self.world.interest.friends_list():
            all_npcs.add(handle)

        # npcs that were in the room when you left it
        for handle in self.world.level.npc_sites.all_bs():
            all_npcs.add(handle)

        follow_npcs = list(all_npcs)
        follow_npcs.sort(key=lambda n: self.world.npcs.get(n).name)
        follow_npcs.sort(key=lambda n: self.world.interest[n], reverse=True)
        self.follow_npcs = Scrollbar(follow_npcs, Follow(self))

    def run(self):
        self.calculate_lists()

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

        if input.match(Key.new("f")):
            self._state = FlyScreenState.Follow

        if self._state == FlyScreenState.Follow:
            if input.match(Key.new(Keycodes.Up)):
                self.follow_npcs.up()
            if input.match(Key.new(Keycodes.Down)):
                self.follow_npcs.down()

    def draw(self):
        window = draw_window(self.io.draw().goto(4, 7).box(26, 28), fg=Colors.MSGSystem, double=True)
        window.title_bar.copy().fg(Colors.TermFGBold).puts("Fly")

        window.content.copy().goto(0, 0).fg(Colors.TermFGBold).puts("F - Follow")
        self.follow_npcs.draw(window.content.copy().goto(0, 1).box(window.content.bounds.size.x, 11))

        window.content.copy().goto(0, 12).fg(Colors.TermFGBold).puts("R - Recent")


class Follow(ScrollbarData):
    def __init__(self, fly: FlyScreen):
        self.fly = fly

    def measure_item(self, npch, width: int) -> V2:
        # TODO: Measure NPC name
        npc = self.fly.world.npcs.get(npch)
        y = measure_wrap(npc.name, width - 2)  # bullet point
        return V2.new(width, y)

    def draw_item(self, npch, draw: Drawer, selected: bool):
        npc = self.fly.world.npcs.get(npch)
        color = self.fly.world.interest[npch].color()
        if selected:
            draw.bg(Colors.TermHighlightBG if self.fly._state == FlyScreenState.Follow else Colors.TermHighlightBGInactive)
        draw.goto(0, 0).fg(color).puts("\xf9 ").fg(Colors.TermFG).puts(npc.name, wrap=True)


class FlyScreenState(Enum):
    Follow = 0
    Recent = 1