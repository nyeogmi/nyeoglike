from display import IO, Colors, DoubleWide, Key, Keycodes
from ds.vecs import V2

from ..event import Event, Verbs
from ..eventmonitor import EMHandle, QuestOutcome, QuestStatus
from ..interest import Interest
from ..item import Resource
from ..level import Block
from ..notifications import NotificationReason
from ..npc import NPC, NPCHandle, NPCs
from ..world import World
from . import fly_screen, fov, inventory_screen, shop_screen
from .npcview import NPCView
from .targeter import Target, Targeter
from .window import Window, draw_window


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
        self.lightmap: fov.Lightmap = fov.Lightmap({})
        self.npc_view = NPCView(self.world)

    @property
    def camera_world_rect(self):
        c0 = self.world.camera_xy - V2.new(19, 14)
        c1 = self.world.camera_xy + V2.new(20 + 1, 15 + 1)  # exclusive bound
        return c0.to(c1)

    def run(self):
        """
        self.world.notifications.send("I LOVE BATS")
        self.world.notifications.send("BATS ARE SO COOL")
        self.world.notifications.send("BATS RULE")
        self.world.notifications.send("BATS ARE THE BEST")
        """

        self.world.start_time_period()

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
            if notif and notif.reason == NotificationReason.AnnounceQuest:
                self.world.notifications.acknowledge(self.world, notif.ident, False)
        elif input.match(Key.new("a")):
            if self.targets.target:
                self.world.interest.tab(self.targets.target)

        elif input.match(Key.new("i")):
            inventory_screen.show(self.io, self.world)

        elif input.match(Key.new("e")):
            shop_screen.show(self, self.io, self.world)

        elif input.match(Key.new("f")):
            fly_screen.show(self.io, self.world)

        elif input.match(Key.new("g")):
            spawns = self.world.level.items.view(self.world.player_xy)
            if len(spawns) == 0:
                pass  # nothing to grab
            else:
                if (
                    len(spawns) == 1
                ):  # TODO: Only autopick the item if it would not be stealing
                    ix = -1
                else:
                    # TODO: Let the player pick their item
                    ix = -1  # item = self.pick_item(items)

                item = self.world.level.items.take(spawns.pop(ix).handle)
                self.world.inventory.add(self.world, item)

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
            new_xy = self.world.player_xy + move
            block = self.world.level.blocks.get(new_xy)
            if block == Block.Normal:
                # don't move
                pass
            elif block == Block.Exit:
                fly_screen.show(self.io, self.world)
            else:
                self.world.player_xy = new_xy
                if move.x != 0:
                    if abs(self.world.camera_xy.x - self.world.player_xy.x) > 4:
                        self.world.camera_xy += move
                if move.y != 0:
                    if abs(self.world.camera_xy.y - self.world.player_xy.y) > 4:
                        self.world.camera_xy += move

                # actually moving is worth a tick
                self.world.notify(Event.new(Verbs.Tick, ()))

    def recalculate_visibility(self):
        self.lightmap = fov.fov(
            lambda world_xy: world_xy in self.world.level.blocks,
            self.camera_world_rect,
            self.world.player_xy,
            80.0,  # see indefinitely in all directions
        )
        self.world.level.seen.update(
            world_xy
            for world_xy in self.camera_world_rect
            if self.lightmap[world_xy] > 0
        )
        # TODO: Player always sees NPCs who they are Friend/Love with
        possible_targets = [
            Target(npc, world_xy)
            for world_xy in self.camera_world_rect
            if self.lightmap[world_xy] > 0
            for npc in self.world.level.npc_sites.get_bs(world_xy)
        ]

        for tar in possible_targets:
            self.world.npcs.get(tar.npc).seen = True

        self.targets.update_possible(
            player_xy=self.world.player_xy, possible_targets=possible_targets
        )

        # update npc view
        self.npc_view.select(self.targets.target)

    def draw(self):
        self.draw_grid()
        self.draw_targeted_user()
        self.draw_notifications()
        self.draw_quests()
        self.draw_my_hud()
        self.draw_timeinfo()

    def draw_grid(self):
        # draw grid
        draw_world = self.io.draw().goto(0, 0).box(VIEW.x, VIEW.y).zeroed()

        draw_world.bg(Colors.TermBG).fg(Colors.TermFG).fillc(" ")  # base color

        viewport_xys = (
            V2.new(x, y) for y in range(VIEW.y) for x in range(0, VIEW.x, 2)
        )

        tooltip_xy = None
        tooltip_lst = []
        for world_xy_bot, viewport_xy in zip(self.camera_world_rect, viewport_xys):
            world_xy_back = world_xy_bot + V2.new(0, -1)

            # Draw order:
            # (1) Back of block behind
            # (2) Items, NPCs, player
            # (3) Top of this block
            # (4) Tooltips

            draw_tile = (
                draw_world.goto(viewport_xy).bg(Colors.WorldBG).fg(Colors.WorldFG)
            )
            draw_tile.copy().putdw(DoubleWide.Blank)

            if self.lightmap[world_xy_bot] == 0:
                draw_tile.copy().bg(Colors.WorldUnseenBG).fg(
                    Colors.WorldUnseenFG
                ).putdw(DoubleWide.Blank)

            # == Back of block behind ==
            if world_xy_back in self.world.level.seen:
                back = self.world.level.blocks.get(world_xy_back)
            else:
                back = None

            if world_xy_bot in self.world.level.seen:
                top = self.world.level.blocks.get(world_xy_bot)
            else:
                top = None

            if back == Block.Normal:
                self.draw_wallpaper(
                    draw_tile.copy(),
                    self.world.level.wallpaper.get(world_xy_back),
                    cutaway=False,
                    illum=self.lightmap[world_xy_back] > 0
                    and self.world.player_xy.y > world_xy_back.y,
                )

            if self.lightmap[world_xy_bot] > 0:
                things_drawn = 0
                for spawn in self.world.level.items.view(world_xy_bot):
                    dt = draw_tile.copy()
                    profile = spawn.item.profile

                    if things_drawn > 0:
                        dt.bg(Colors.Grey0)
                    if profile.bg is not None:
                        dt.bg(profile.bg)
                    if profile.fg is not None:
                        dt.fg(profile.fg)

                    if profile.double_icon is not None:
                        if isinstance(profile.double_icon, str):
                            dt.goto(viewport_xy).puts(profile.double_icon, wrap=False)
                        else:
                            dt.goto(viewport_xy).putdw(profile.double_icon)
                    else:
                        dt.goto(viewport_xy + V2(1, 0)).puts(profile.icon)
                        (resource_fg, resource_icon) = spawn.item.contributions[
                            0
                        ].resource.display()
                        dt.goto(viewport_xy).fg(resource_fg).puts(resource_icon)

                    things_drawn += 1

                    if world_xy_bot == self.world.player_xy:
                        tooltip_xy = viewport_xy + V2(0, 1)
                        tooltip_lst.append(profile.name)

                npc: NPCHandle
                for npc in self.world.level.npc_sites.get_bs(world_xy_bot):
                    interest = self.world.interest[npc]
                    # npc_sites
                    if npc == self.targets.target:
                        draw_tile.copy().bg(interest.color()).fg(Colors.WorldBG).putdw(
                            DoubleWide.At
                        )
                    else:
                        draw_tile.copy().bg(
                            Colors.WorldBG if things_drawn == 0 else Colors.Grey0
                        ).fg(interest.color()).putdw(DoubleWide.At)
                    things_drawn += 1

                if world_xy_bot == self.world.player_xy:
                    draw_tile.copy().bg(
                        Colors.WorldBG if things_drawn == 0 else Colors.Grey0
                    ).fg(Colors.Player).putdw(DoubleWide.Bat)

            # if this is right above a wall, draw a (seen) ceiling
            if top == Block.Normal:
                self.draw_ceiling(
                    draw_tile.copy(),
                    self.world.level.wallpaper.default,
                    # self.world.level.wallpaper.get(world_xy + V2.new(0, 1)),
                    cutaway=False,
                    illum=self.lightmap[world_xy_bot] > 0,
                )

            elif top == Block.Exit:
                if self.lightmap[world_xy_bot] > 0:
                    draw_tile.copy().putdw(DoubleWide.Exit)
                else:
                    draw_tile.copy().bg(Colors.WorldUnseenBG).fg(
                        Colors.WorldUnseenFG
                    ).putdw(DoubleWide.Exit)

        # Draw tooltips
        if tooltip_xy is not None and tooltip_lst:
            draw_tooltips = self.io.draw().goto(tooltip_xy)
            for i, tip in enumerate(tooltip_lst):
                draw_tooltips.goto(tooltip_xy + V2.new(0, i)).fg(
                    Colors.TermFGBold
                ).puts(tip)

    def draw_targeted_user(self):
        self.npc_view.draw(self.io.draw())

    def draw_notifications(self):
        notifications = self.world.notifications.active_notifications()[-12:]
        if notifications:
            for y, (i, n) in enumerate(enumerate(notifications), 7):
                last = i == len(notifications) - 1
                if last:
                    height = 4  # TODO: Real height
                else:
                    height = 2

                if n.source:
                    color = self.world.interest[n.source].color()
                else:
                    color = Colors.MSGSystem

                window = draw_window(
                    self.io.draw().goto(4, y).box(26, y + height), fg=color
                )

                if isinstance(n.message, EMHandle):
                    if n.reason == NotificationReason.AnnounceQuest:
                        quest_status: QuestStatus = (
                            self.world.eventmonitors.most_recent_status(n.message)
                        )
                        assert quest_status is not None

                        window.title_bar.copy().fg(Colors.TermFGBold).puts(
                            quest_status.name
                        )
                        window.content.copy().puts(quest_status.description, wrap=True)
                        yes = "Z - OK"
                        window.button_bar.copy().fg(Colors.TermFGBold).puts(yes)
                        no = "X - Ignore"
                        window.button_bar.copy().fg(Colors.TermFGBold).goto(
                            window.button_bar.bounds.size.x - len(no), 0
                        ).puts(no)
                    elif n.reason == NotificationReason.FinalizeQuest:
                        quest_status: QuestStatus = (
                            self.world.eventmonitors.most_recent_status(n.message)
                        )
                        assert quest_status is not None

                        if quest_status.outcome == QuestOutcome.Failed:
                            window.border.copy().fg(Colors.QuestFailed).etch(
                                double=True
                            )
                            window.title_bar.copy().fg(Colors.TermFGBold).puts(
                                "Failed: " + quest_status.name
                            )
                        else:
                            window.border.copy().fg(Colors.QuestSucceeded).etch(
                                double=True
                            )
                            window.title_bar.copy().fg(Colors.TermFGBold).puts(
                                "Succeeded: " + quest_status.name
                            )

                        window.content.copy().puts(quest_status.description, wrap=True)
                        yes = "Z - OK"
                        window.button_bar.copy().fg(Colors.TermFGBold).puts(yes)
                    else:
                        raise AssertionError("bad reason: {}".format(n.reason))
                else:
                    window.content.copy().puts(n.message, wrap=True)
                    help = "Z - OK"
                    # not bold because this choice is unimportant
                    window.button_bar.copy().fg(Colors.TermFG).puts(help)

    def draw_quests(self):
        draw_quests_ui = self.io.draw()
        quest_emhs = self.world.eventmonitors.accepted_quests()
        if quest_emhs:
            marked_quests = [
                (emh, self.world.eventmonitors.most_recent_status(emh))
                for emh in quest_emhs
            ]
            marked_quests.sort(
                key=lambda q: (
                    q[1].outcome != QuestOutcome.InProgress,
                    self.world.interest[q[1].assigner],
                    q[0],
                )
            )
            marked_quests.reverse()

            y = 7
            draw_quests_ui.copy().goto(50, y).bg(Colors.TermBG).fg(
                Colors.TermFGBold
            ).puts("Q - Quests")
            y += 1
            for (_, quest) in marked_quests:
                if y >= 29:  # screen height
                    break  # don't draw too many quests

                if quest.outcome == QuestOutcome.Succeeded:
                    color = Colors.QuestSucceeded
                elif quest.outcome == QuestOutcome.Failed:
                    color = Colors.QuestFailed
                elif quest.assigner is None:
                    color = Colors.MSGSystem
                else:
                    color = self.world.interest[quest.assigner].color()

                dq2 = (
                    draw_quests_ui.copy()
                    .goto(52, y)
                    .bg(Colors.TermBG)
                    .fg(color)
                    .puts("\xf9 ")
                    .fg(Colors.TermFG)
                )
                start_x = dq2.xy.x
                dq2.puts(quest.oneliner, wrap=True)
                y = dq2.xy.y + (
                    1 if dq2.xy.x != start_x else 0
                )  # drop once if we didn't wrap

    def draw_my_hud(self):
        window = draw_window(
            self.io.draw().goto(4, 2).box(26, 5), double=True, fg=Colors.MSGSystem
        )

        window.title_bar.copy().fg(Colors.TermFGBold).puts(self.world.player.name)

        window.content.copy().goto(0, 0).puts("$").fg(Colors.TermFGBold).puts(
            "{:,.2f}".format(self.world.inventory.get(Resource.Money) / 100)
        )
        window.content.copy().goto(0, 1).puts("[").bg(Colors.Red1).puts(" " * 20).bg(
            Colors.TermBG
        ).fg(Colors.TermFG).puts("]")
        window.content.copy().goto(0, 2).puts("[").bg(Colors.YellowGreen1).puts(
            " " * 20
        ).bg(Colors.TermBG).fg(Colors.TermFG).puts("]")

    def draw_timeinfo(self):
        txt = (
            self.world.clock.time_of_day.display()
            + ", "
            + str(self.world.clock.weekday)
        )
        window = draw_window(
            self.io.draw().goto(4, 27).box(4 + len(txt), 28),
            double=True,
            fg=Colors.MSGSystem,
        )

        window.content.copy().goto(0, 0).puts(txt)

    def draw_wallpaper(self, drawer, walltile, cutaway: bool, illum: bool):
        if cutaway:
            return

        d = drawer.copy()

        if not illum:  # TODO: Reinstate detailed rendering for unseen walls?
            d.fg(Colors.WorldUnseenFG).puts("\xb0\xb0", wrap=False)
            return

        if walltile.flip:
            d = d.bg(walltile.fg if illum else Colors.WorldUnseenFG).fg(
                Colors.WorldBG if illum else Colors.WorldUnseenBG
            )
        else:
            d = d.fg(walltile.fg if illum else Colors.WorldUnseenFG)

        d.puts(
            walltile.display
            if illum
            else "\xb0\xb0"
            if walltile.display == "\xdb\xdb"
            else walltile.display,
            wrap=False,
        )

    def draw_ceiling(self, drawer, walltile, cutaway: bool, illum: bool):
        if cutaway:
            return

        d = drawer.copy()
        d.fg(walltile.cap if illum else Colors.WorldUnseenFG)
        d.puts("\xdb\xdb", wrap=False)
