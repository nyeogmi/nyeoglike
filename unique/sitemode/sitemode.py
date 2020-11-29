from display import Colors, DoubleWide, Key, Keycodes, IO

from ds.vecs import V2
from ..event import Event, Verbs
from ..eventmonitor import EMHandle, QuestStatus
from ..interest import Interest
from ..item import Resource, common
from ..npc import NPCs, NPC, NPCHandle
from ..world import World

from . import inventory_screen
from .targeter import Targeter, Target
from .window import draw_window, Window


def sitemode(io: IO, world: World):
    Sitemode(io, world).run()


VIEW = V2(80, 30)

# use a class to provide shared scope for the important stuff, and to share it when delegating to other fns


class Sitemode(object):
    def __init__(self, io: IO, world: World):
        assert isinstance(io, IO)
        assert isinstance(world, World)

        self.io = io
        self.world = world
        self.targets = Targeter()

    @property
    def camera_world_rect(self):
        c0 = self.world.camera_xy - V2.new(19, 14)
        c1 = self.world.camera_xy + V2.new(20 + 1, 15 + 1)  # exclusive bound
        return c0.to(c1)

    def run(self):
        # TODO: Reorder loop to draw last? On first iteration, skip player action
        self.world.notifications.send("I LOVE BATS")
        self.world.notifications.send("BATS ARE SO COOL")
        self.world.notifications.send("BATS RULE")
        self.world.notifications.send("BATS ARE THE BEST")
        self.world.inventory.add(common.cash_loot())

        while True:
            self.recalculate_visibility()

            with self.io.lock():
                self.draw()

            self.do_input()

    def do_input(self):
        input = self.io.getch()
        # update player target
        if input.match(Key.new(Keycodes.Tab)):
            self.targets.tab(self.world.player_xy)
        elif input.match(Key.new(Keycodes.Tab, shift=True)):
            self.targets.untab(self.world.player_xy)
        elif input.match(Key.new("z")):
            notif = self.world.notifications.last_notification()
            if notif:
                self.world.notifications.acknowledge(self.world, notif.ident, True)
        elif input.match(Key.new("x")):
            notif = self.world.notifications.last_notification()
            if notif:
                self.world.notifications.acknowledge(self.world, notif.ident, False)
        elif input.match(Key.new("a")):
            if self.targets.target: self.world.interest.tab(self.targets.target)

        elif input.match(Key.new("i")):
            inventory_screen.show(self.io, self.world)

        # move the player
        moves = [
            (Key.new(Keycodes.Up), V2.new(0, -1)),
            (Key.new(Keycodes.Down), V2.new(0, 1)),
            (Key.new(Keycodes.Left), V2.new(-1, 0)),
            (Key.new(Keycodes.Right), V2.new(1, 0)),
        ]
        for k, m in moves:
            if input.match(k):
                move = m
                break
        else:
            move = None

        if move:
            # Camera follows player
            if self.world.player_xy + move in self.world.level.blocks:
                # don't move
                pass
            else:
                self.world.player_xy += move
                if move.x != 0:
                    if abs(self.world.camera_xy.x - self.world.player_xy.x) > 4:
                        self.world.camera_xy += move
                if move.y != 0:
                    if abs(self.world.camera_xy.y - self.world.player_xy.y) > 4:
                        self.world.camera_xy += move

                # actually moving is worth a tick
                self.world.notify(Event.new(Verbs.Tick, ()))

    def recalculate_visibility(self):
        possible_targets = [
            Target(npc, world_xy)
            for world_xy in self.camera_world_rect
            for npc in self.world.level.npc_sites.get_bs(world_xy)
        ]
        self.targets.update_possible(
            player_xy=self.world.player_xy,
            possible_targets=possible_targets
        )

    def draw(self):
        self.draw_grid()
        self.draw_targeted_user()
        self.draw_notifications()
        self.draw_quests()
        self.draw_my_hud()

    def draw_grid(self):
        # draw grid
        draw_world = self.io.draw().goto(0, 0).box(VIEW.x, VIEW.y).zeroed()

        draw_world.bg(Colors.TermBG).fg(Colors.TermFG).fillc(" ")  # base color

        viewport_xys = (V2.new(x, y) for y in range(VIEW.y) for x in range(0, VIEW.x, 2))

        tooltip_xy = None
        tooltip_lst = []
        for world_xy, viewport_xy in zip(self.camera_world_rect, viewport_xys):
            bg = Colors.WorldBG

            draw_tile = draw_world.goto(viewport_xy).bg(bg).fg(Colors.WorldFG)
            draw_tile.copy().putdw(DoubleWide.Blank)

            if world_xy in self.world.level.blocks:
                # full block
                draw_tile.copy().bg(Colors.WorldBG).fg(Colors.WorldFG).puts("\xdb\xdb", wrap=False)

            for item in self.world.level.items.get(world_xy, []):
                profile = item.profile
                dt = draw_tile.copy()
                if profile.bg is not None: dt.bg(profile.bg)
                if profile.fg is not None: dt.fg(profile.fg)

                dt.goto(viewport_xy + V2(1, 0)).puts(profile.icon)
                (resource_fg, resource_icon) = item.contributions[0].resource.display()
                dt.goto(viewport_xy).fg(resource_fg).puts(resource_icon)

                if world_xy == self.world.player_xy:
                    tooltip_xy = viewport_xy + V2(0, 1)
                    tooltip_lst.append(profile.name)

            npc: NPCHandle
            for npc in self.world.level.npc_sites.get_bs(world_xy):
                interest = self.world.interest[npc]
                # npc_sites
                if npc == self.targets.target:
                    draw_tile.copy().bg(interest.color()).fg(Colors.WorldBG).putdw(DoubleWide.At)
                else:
                    draw_tile.copy().bg(Colors.WorldBG).fg(interest.color()).putdw(DoubleWide.At)

            if world_xy == self.world.player_xy:
                draw_tile.copy().fg(Colors.Player).putdw(DoubleWide.Bat)

            # TODO: Draw bushes in a knight's move pattern

        # Draw tooltips
        if tooltip_xy is not None and tooltip_lst:
            draw_tooltips = self.io.draw().goto(tooltip_xy)
            for i, tip in enumerate(tooltip_lst):
                draw_tooltips.goto(tooltip_xy + V2.new(0, i)).fg(Colors.TermFGBold).puts(tip)

    def draw_targeted_user(self):
        target_handle = self.targets.target
        if target_handle is not None:
            target = self.world.npcs.get(target_handle)
            interest = self.world.interest[target_handle]

            window = draw_window(self.io.draw().goto(30, 2).box(76, 6), fg=interest.color())
            window.title_bar.copy().fg(Colors.TermFGBold).puts(target.name)
            if interest != Interest.No:
                b2 = window.title_bar.copy().goto(len(target.name) + 1, 0).fg(Colors.TermFG)
                b2.puts("({})".format(interest.name))

            window.title_bar.copy().goto(window.title_bar.bounds.size.x - len("A - Mark"), 0).fg(Colors.TermFGBold).puts("A - Mark")

    def draw_notifications(self):
        notifications = self.world.notifications.active_notifications()[-6:]
        if notifications:
            for y, (i, n) in enumerate(enumerate(notifications), 7):
                last = (i == len(notifications) - 1)
                if last:
                    height = 4  # TODO: Real height
                else:
                    height = 2

                if n.source:
                    color = self.world.interest[n.source].color()
                else:
                    color = Colors.MSGSystem

                window = draw_window(self.io.draw().goto(4, y).box(26, y + height), fg=color)

                if isinstance(n.message, EMHandle):
                    quest_status: QuestStatus = self.world.eventmonitors.most_recent_status(n.message)
                    assert isinstance(quest_status, QuestStatus)  # A canceled quest should remove its notifications

                    window.title_bar.copy().fg(Colors.TermFGBold).puts(quest_status.name)
                    window.content.copy().puts(quest_status.description, wrap=True)
                    yes = "Z - OK"
                    window.button_bar.copy().fg(Colors.TermFGBold).puts(yes)
                    no = "X - Ignore"
                    window.button_bar.copy().fg(Colors.TermFGBold).goto(window.button_bar.bounds.size.x - len(no), 0).puts(no)
                else:
                    window.content.copy().puts(n.message, wrap=True)
                    help = "Z - OK"
                    # not bold because this choice is unimportant
                    window.button_bar.copy().fg(Colors.TermFG).puts(help)

    def draw_quests(self):
        draw_quests_ui = self.io.draw()
        quest_emhs = self.world.eventmonitors.accepted_quests()
        if quest_emhs:
            marked_quests = [(emh, self.world.eventmonitors.most_recent_status(emh)) for emh in quest_emhs]
            marked_quests.sort(key=lambda q: (self.world.interest[q[1].assigner], q[0]))
            marked_quests.reverse()

            y = 7
            draw_quests_ui.copy().goto(60, y).bg(Colors.TermBG).fg(Colors.TermFGBold).puts("Q - Quests");
            y += 1
            for y, (_, quest) in enumerate(marked_quests, y):
                if y >= 29:  # screen height
                    break  # don't draw too many quests

                if quest.assigner is None:
                    color = Colors.MSGSystem
                else:
                    color = self.world.interest[quest.assigner].color()

                draw_quests_ui.copy().goto(62, y).bg(Colors.TermBG).fg(color).puts("\xf9 ").fg(Colors.TermFG).puts(
                    quest.oneliner)

    def draw_my_hud(self):
        window = draw_window(self.io.draw().goto(4, 2).box(26, 5), double=True, fg=Colors.MSGSystem)

        window.title_bar.copy().fg(Colors.TermFGBold).puts("Nyeogmi Choi")

        window.content.copy().goto(0, 0).puts("$").fg(Colors.TermFGBold).puts(
            "{:,.2f}".format(self.world.inventory.get(Resource.Money) / 100)
        )
        window.content.copy().goto(0, 1).puts("[").bg(Colors.BloodRed).puts(" " * 20).bg(Colors.TermBG).fg(Colors.TermFG).puts("]")
        window.content.copy().goto(0, 2).puts("[").bg(Colors.BrightGreen).puts(
            " " * 20
        ).bg(Colors.TermBG).fg(Colors.TermFG).puts("]")
