from enum import Enum
from typing import Optional, Protocol, Set, runtime_checkable

from display import IO, Colors, DoubleWide, Drawer, Key, Keycodes, measure_wrap
from ds.vecs import R2, V2

from ..item import Resource, Resources
from ..npc import NPCHandle
from ..world import World
from .scrollbar import Scrollbar, ScrollbarData
from .window import draw_window


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

            if input.match(Key.new(Keycodes.Enter)):
                selected = self.follow_npcs.get_selected()
                if selected:
                    self.world.follow_npc(selected)
                    self.world.advance_time()
                    self.done = True

    def draw(self):
        window = draw_window(
            self.io.draw().goto(4, 7).box(26, 25), fg=Colors.MSGSystem, double=True
        )
        window.title_bar.copy().fg(Colors.TermFGBold).puts("Fly")

        window.content.copy().goto(0, 0).fg(Colors.TermFGBold).puts("F - Follow")
        self.follow_npcs.draw(
            window.content.copy().goto(0, 1).box(window.content.bounds.size.x, 11)
        )

        window.content.copy().goto(0, 12).fg(Colors.TermFGBold).puts("R - Recent")


class Follow(ScrollbarData):
    def __init__(self, fly: FlyScreen):
        self.fly = fly

    def text(self, npch):
        npc = self.fly.world.npcs.get(npch)
        return (
            npc.name
            + "\n"
            + "("
            + self.fly.world.schedules.next_schedule(npch).to_text(self.fly.world)
            + ")"
        )

    def measure_item(self, npch, width: int) -> V2:
        # TODO: Measure NPC name
        y = measure_wrap(self.text(npch), width - 2)  # bullet point
        return V2.new(width, y)

    def draw_item(self, npch, draw: Drawer, selected: bool):
        color = self.fly.world.interest[npch].color()
        if selected:
            draw.bg(
                Colors.TermHighlightBG
                if self.fly._state == FlyScreenState.Follow
                else Colors.TermHighlightBGInactive
            )
        draw.goto(0, 0).fg(color).puts("\xf9 ").fg(Colors.TermFG).puts(
            self.text(npch), wrap=True
        )


class FlyScreenState(Enum):
    Follow = 0
    Recent = 1
