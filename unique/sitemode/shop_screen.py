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


def show(sitemode, io: IO, world: World):
    ShopScreen(sitemode, io, world).run()


class ItemToBuy(object):
    def __init__(self, item: Item, count: int, who_wants: Optional[NPCHandle]):
        assert isinstance(item, Item)
        assert isinstance(count, int)

        self.item = item
        self.count = count
        self.who_wants = who_wants

    @property
    def buy_price(self):
        return self.item.buy_price


class ShopScreen(object):
    def __init__(self, sitemode, io: IO, world: World):
        assert isinstance(io, IO)
        assert isinstance(world, World)

        self.sitemode = sitemode
        self.io = io
        self.world = world
        self.done = False

        self.verb = "Shop"
        self.shop_items = Scrollbar([], Shop(self))

    def calculate_lists(self):
        all_items: List[ItemToBuy] = []

        level: LevelHandle = self.world.level.ident
        verbs = []

        # if this is a restaurant, include the menu
        enterprise = self.world.enterprises.located_at(level)
        if enterprise:
            restaurant = self.world.enterprises.get_restaurant(self.world, enterprise)
            if restaurant:
                all_items.extend(
                    ItemToBuy(
                        item, 0, self.world.eventmonitors.who_wants(self.world, item)
                    )
                    for item in restaurant.menu.items
                )
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

        sel = self.shop_items.get_selected()
        if sel:
            if input.match(Key.new(Keycodes.Left)):
                sel.count -= 1
                if sel.count < 0:
                    sel.count = 0
            if input.match(Key.new(Keycodes.Right)):
                sel.count += 1
                if sel.count > 9:
                    sel.count = 9
            if input.match(Key.new(Keycodes.Left, shift=True)):
                sel.count = 0
            if input.match(Key.new(Keycodes.Right, shift=True)):
                sel.count = 9

        if input.match(Key.new(Keycodes.Enter)):
            count, price, budget = self.total_count_price_budget()

            selected = self.shop_items.get_selected()
            if selected:
                if price <= budget:
                    self.world.inventory.take(Resource.Money, price)
                    for i2b in self.shop_items.all_items():
                        i2b: ItemToBuy
                        for i in range(i2b.count):
                            self.world.inventory.add(self.world, i2b.item)
                    self.done = True

    def total_count_price_budget(self):
        total_count = sum([i.count for i in self.shop_items.all_items()])
        total_price = sum([i.count * i.buy_price for i in self.shop_items.all_items()])
        budget = self.world.inventory.get(Resource.Money)
        return total_count, total_price, budget

    def draw(self):
        total_count, total_price, budget = self.total_count_price_budget()

        self.sitemode.draw_my_hud()

        main_window = draw_window(
            self.io.draw().goto(4, 7).box(26, 25), fg=Colors.MSGSystem, double=True
        )
        main_window.title_bar.copy().fg(Colors.TermFGBold).puts(self.verb)

        # TODO: Make space/use space at the bottom?
        main_window.content.copy().goto(0, 0).fg(Colors.TermFGBold).puts("Items")
        self.shop_items.draw(
            main_window.content.copy()
            .goto(0, 1)
            .box(main_window.content.bounds.size.x, 18 if total_count == 0 else 15)
        )

        if total_count > 0:
            main_window.content.copy().goto(0, 15).fg(Colors.TermFGBold).puts("Total")
            draw = main_window.content.copy().goto(0, 16)
            draw.fg(Colors.TermFGBold).puts("{:>3d}".format(total_count))
            draw.fg(Colors.TermFG).puts(" items")

            draw.goto(draw.bounds.size.x - 10, draw.xy.y).fg(
                Colors.Red0 if total_price > budget else Colors.TermFG
            ).puts("{:10,.2f}".format(total_price / 100))

        if total_count == 0:
            main_window.button_bar.fg(Colors.TermFGBold).puts("\x1d - Add")
        else:
            main_window.button_bar.fg(
                Colors.Red0 if total_price > budget else Colors.TermFGBold
            ).puts("Enter - {}".format("Buy" if self.verb == "Shop" else self.verb))


class Shop(ScrollbarData):
    def __init__(self, shop: ShopScreen):
        self.shop = shop

    def text(self, i2b: ItemToBuy):
        # TODO: Info about the price and whether the item will complete a quest
        return (
            i2b.item.profile.name,
            ("for {}" + self.shop.world.npcs.get(i2b.who_wants).name)
            if i2b.who_wants
            else None,
        )  # we don't use the second line here so it doesn't matter

    def measure_item(self, i2b: ItemToBuy, width: int) -> V2:
        # TODO: Measure NPC name
        line_1, line_2 = self.text(i2b)
        y1 = measure_wrap(line_1, width - 2)  # bullet point
        y2 = (
            0 if i2b.who_wants is None else measure_wrap(line_2, width - 2)
        )  # who wants it
        y3 = 1  # price line
        return V2.new(width, y1 + y2 + y3)

    def draw_item(self, i2b: ItemToBuy, draw: Drawer, selected: bool):
        #  color = self.fly.world.interest[npch].color()
        if selected:
            draw.bg(Colors.TermHighlightBG)

        line_1, _ = self.text(i2b)
        "${:,.2f}".format(i2b.buy_price / 100)
        draw.goto(0, 0)
        if i2b.count == 0:
            draw.fg(Colors.MSGSystem).puts("\xf9 ")
        else:
            draw.fg(Colors.TermFGBold).puts("{:<2d}".format(i2b.count))

        draw.fg(Colors.TermFG).puts(line_1, wrap=True)

        if i2b.who_wants:
            draw.goto(2, draw.xy.y + 1)  # who wants it
            draw.fg(Colors.TermFG).puts("for ")
            draw.fg(self.shop.world.interest[i2b.who_wants].color()).puts(
                self.shop.world.npcs.get(i2b.who_wants).name
            )

        draw.goto(2, draw.xy.y + 1)
        draw.bg(Colors.TermBG)
        # draw.fg(Colors.TermFG).puts("1")
        # draw.fg(Colors.MSGSystem).puts(" x")
        # draw.fg(Colors.TermFGBold).puts("$")
        draw.fg(Colors.TermFG).puts("{:,.2f}".format(i2b.buy_price / 100))

        if i2b.count > 0:
            draw.goto(draw.bounds.size.x - 10, draw.xy.y).fg(Colors.TermFG).puts(
                "{:10,.2f}".format(i2b.count * i2b.buy_price / 100)
            )
