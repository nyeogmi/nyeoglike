from enum import Enum
from typing import List, Optional, Protocol, Set, runtime_checkable

from display import IO, Colors, DoubleWide, Drawer, Key, Keycodes, measure_wrap
from ds.vecs import R2, V2

from ..item import Item, Resource, Resources
from ..npc import NPCHandle
from ..world import World
from ..worldmap import LevelHandle
from .scrollbar import Scrollbar, ScrollbarData
from .window import draw_window


def show(io: IO, world: World):
    ShopScreen(io, world).run()


class ShopScreen(object):
    def __init__(self, io: IO, world: World):
        assert isinstance(io, IO)
        assert isinstance(world, World)

        self.io = io
        self.world = world
        self.done = False

        self.verb = "Shop"
        self.shop_items = Scrollbar([], Shop(self))

    def calculate_lists(self):
        all_items: List[Item] = []

        level: LevelHandle = self.world.level.ident
        verbs = []

        # if this is a restaurant, include the menu
        enterprise = self.world.enterprises.located_at(level)
        if enterprise:
            restaurant = self.world.enterprises.get_restaurant(self.world, enterprise)
            if restaurant:
                all_items.extend(restaurant.menu.items)
                verbs.append("Order")

        self.shop_items = Scrollbar(all_items, Shop(self))
        if len(verbs) == 1:
            self.verb = verbs[0]

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

        if input.match(Key.new(Keycodes.Up)):
            self.shop_items.up()
        if input.match(Key.new(Keycodes.Down)):
            self.shop_items.down()

        if input.match(Key.new(Keycodes.Enter)):
            selected = self.shop_items.get_selected()
            if selected:
                pass  # TODO, Actually buy it
                # self.world.follow_npc(selected)
                # self.world.advance_time()
                # self.done = True

    def draw(self):
        window = draw_window(
            self.io.draw().goto(4, 7).box(26, 25), fg=Colors.MSGSystem, double=True
        )
        # TODO: Have the text depend on whether we're in a restaurant or what
        window.title_bar.copy().fg(Colors.TermFGBold).puts(self.verb)

        # TODO: Make space/use space at the bottom?
        window.content.copy().goto(0, 0).fg(Colors.TermFGBold).puts("Items")
        self.shop_items.draw(
            window.content.copy()
            .goto(0, 1)
            .box(window.content.bounds.size.x, window.content.bounds.size.y)
        )
        window.button_bar.fg(Colors.TermFGBold).puts(
            "Enter - {}".format("Buy" if self.verb == "Shop" else self.verb)
        )


class Shop(ScrollbarData):
    def __init__(self, shop: ShopScreen):
        self.shop = shop

    def text(self, item):
        # TODO: Info about the price and whether the item will complete a quest
        return item.profile.name, "${:,.2f}".format(item.buy_price / 100)

    def measure_item(self, item, width: int) -> V2:
        # TODO: Measure NPC name
        line_1, line_2 = self.text(item)
        y1 = measure_wrap(line_1, width - 2)  # bullet point
        y2 = measure_wrap(line_2, width - 3)
        return V2.new(width, y1 + y2)

    def draw_item(self, item, draw: Drawer, selected: bool):
        #  color = self.fly.world.interest[npch].color()
        color = Colors.TermFG
        if selected:
            draw.bg(Colors.TermHighlightBG)

        line_1, line_2 = self.text(item)
        draw.goto(0, 0).fg(color).puts("\xf9 ").fg(Colors.TermFG).puts(
            line_1, wrap=True
        )
        draw.goto(3, draw.xy.y + 1).fg(Colors.TermFG).puts(line_2, wrap=True)
