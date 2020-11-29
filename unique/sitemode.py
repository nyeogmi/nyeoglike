from display import DoubleWide, Key, Keycodes, Screen, IO
from typing import List, NamedTuple, Optional

from ds.vecs import V2
from .event import Event, Verbs
from .eventmonitor import EMHandle, QuestStatus
from .interest import Interest
from .npc import NPCs, NPC, NPCHandle
from .world import World

# 80 x 30


def sitemode(io: IO, world: World):
    # TODO: Reorder loop to draw last? On first iteration, skip player action
    world.notifications.send("I LOVE BATS")
    world.notifications.send("BATS ARE SO COOL")
    world.notifications.send("BATS RULE")
    world.notifications.send("BATS ARE THE BEST")

    targets = Targeter()
    first = True

    while True:
        # TODO: Draw grass instead. Grid is for civilized areas.
        # Grass is in a knight's move pattern like this -- it's a quotation mark doublewide.
        # There might be bushes.
        #      "
        #   "
        #       "
        #    "
        if first:
            first = False
        else:
            input = io.getch()
            # update player target
            if input.match(Key.new(Keycodes.Tab)):
                targets.tab(world.player_xy)
            elif input.match(Key.new(Keycodes.Tab, shift=True)):
                targets.untab(world.player_xy)
            elif input.match(Key.new("z")):
                notif = world.notifications.last_notification()
                if notif:
                    world.notifications.acknowledge(world, notif.ident, True)
            elif input.match(Key.new("x")):
                notif = world.notifications.last_notification()
                if notif:
                    world.notifications.acknowledge(world, notif.ident, False)
            elif input.match(Key.new("a")):
                if targets.target: world.interest.tab(targets.target)

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
                world.player_orientation = move  # NOTE: This should happen regardless of whether the move is successful

                # TODO: Objects can block player motion
                # Camera follows player
                if world.player_xy + move in world.level.blocks:
                    # don't move
                    pass
                else:
                    world.player_xy += move
                    if move.x != 0:
                        if abs(world.camera_xy.x - world.player_xy.x) > 4:
                            world.camera_xy += move
                    if move.y != 0:
                        if abs(world.camera_xy.y - world.player_xy.y) > 4:
                            world.camera_xy += move

                    # actually moving is worth a tick
                    world.notify(Event.new(Verbs.Tick, ()))

        with io.lock():
            possible_targets = []
            # draw grid
            draw_world = io.draw().goto(0, 0).box(80, 30).zeroed()

            draw_world.bg(0).fg(7).fillc(" ")  # base color
            camera_xy0 = world.camera_xy - V2.new(19, 14)
            camera_xy1 = world.camera_xy + V2.new(20 + 1, 15 + 1)  # exclusive bound

            viewport_xys = (V2.new(x, y) for y in range(draw_world.bounds.size.y) for x in range(0, draw_world.bounds.size.x, 2))

            for world_xy in camera_xy0.to(camera_xy1):
                for npc in world.level.npc_sites.get_bs(world_xy):
                    possible_targets.append(Target(npc, world_xy))

            targets.update_possible(player_xy=world.player_xy, possible_targets=possible_targets)
            target_handle = targets.target

            for world_xy, viewport_xy in zip(camera_xy0.to(camera_xy1), viewport_xys):
                x, y = world_xy

                # draw bg. (TODO: Better pattern?)
                bg_streak_ix = ((x // 4 + y * 2 + x // 16 + y // 12) % 18)
                if bg_streak_ix < 1: bg = 5
                elif bg_streak_ix < 4: bg = 4
                else: bg = 0

                draw_tile = draw_world.goto(viewport_xy).bg(bg).fg(7)
                draw_tile.copy().putdw(DoubleWide.Blank)

                if world_xy in world.level.blocks:
                    # full block
                    draw_tile.copy().bg(0).fg(7).puts("\xdb\xdb", wrap=False)

                npc: NPCHandle
                for npc in world.level.npc_sites.get_bs(world_xy):
                    interest = world.interest[npc]
                    # npc_sites
                    if npc == target_handle:
                        draw_tile.copy().bg(interest.color()).fg(0).putdw(DoubleWide.At)
                    else:
                        draw_tile.copy().bg(0).fg(interest.color()).putdw(DoubleWide.At)

                if world_xy == world.player_xy:
                    draw_tile.copy().fg(15).putdw(DoubleWide.Bat)

                # TODO: Draw bushes in a knight's move pattern

            # Draw targeted user
            if target_handle is not None:
                target = world.npcs.get(target_handle)
                interest = world.interest[target_handle]
                draw_npc_ui = io.draw().goto(30, 2).box(76, 6).zeroed()
                draw_npc_ui.bg(0).fg(7)
                box = draw_npc_ui.copy().expand(2, 1).fillc(" ").fg(interest.color()).etch(double=False) # box
                box.zeroed().goto(2, 0).fg(15).puts(target.name)
                if interest != Interest.No:
                    box.zeroed().goto(2 + len(target.name) + 1, 0).fg(7).puts("({})".format(interest.name))

                box.zeroed().goto(48 - len("A - Mark"), 0).fg(15).puts("A - Mark")

            # Draw notifications
            notifications = world.notifications.active_notifications()[-6:]
            if notifications:
                for y, (i, n) in enumerate(enumerate(notifications), 8):
                    last = (i == len(notifications) - 1)
                    if last:
                        height = 4  # TODO: Real height
                    else:
                        height = 2

                    if n.source:
                        color = world.interest[n.source].color()
                    else:
                        color = 5
                    draw_notification_ui = io.draw().goto(4, y).box(26, y + height).zeroed()
                    draw_notification_ui.bg(0).fg(7)
                    draw_notification_ui.copy().fg(color).expand(2, 1).fillc(" ").etch(double=False)  # box

                    if isinstance(n.message, EMHandle):
                        quest_status: QuestStatus = world.eventmonitors.most_recent_status(n.message)
                        assert isinstance(quest_status, QuestStatus)  # A canceled quest should remove its notifications

                        draw_notification_ui.copy().expand(2, 1).goto(0, -1).fg(15).puts(quest_status.name)
                        draw_notification_ui.copy().goto(0, 0).puts(quest_status.description, wrap=True)
                        yes = "Z - OK"
                        draw_notification_ui.copy().fg(15).expand(2, 1).goto(0, height).puts(yes)
                        no = "X - Ignore"
                        draw_notification_ui.copy().fg(15).expand(2, 1).goto(draw_notification_ui.bounds.size.x - len(no), height).puts(no)
                    else:
                        draw_notification_ui.goto(0, 0).puts(n.message, wrap=True)
                        help = "Z - OK"
                        # fg=7 because this choice is unimportant
                        draw_notification_ui.copy().fg(7).expand(2, 1).goto(0, height).puts(help)

            # Draw quests
            draw_quests_ui = io.draw()
            quest_emhs = world.eventmonitors.accepted_quests()
            if quest_emhs:
                marked_quests = [(emh, world.eventmonitors.most_recent_status(emh)) for emh in quest_emhs]
                marked_quests.sort(key=lambda q: (world.interest[q[1].assigner], q[0]))
                marked_quests.reverse()

                y = 7
                draw_quests_ui.copy().goto(60, y).bg(0).fg(7).puts("Q - Quests"); y += 1
                for y, (_, quest) in enumerate(marked_quests, y):
                    if y >= 29:  # screen height
                        break  # don't draw too many quests
                    if quest.assigner is None: color = 5
                    else: color = world.interest[quest.assigner].color()
                    draw_quests_ui.copy().goto(62, y).bg(0).fg(color).puts("\xf9 ").fg(7).puts(quest.oneliner)

            # Draw my HUD
            draw_hud_ui = io.draw().goto(4, 2).box(26, 6).zeroed()
            draw_hud_ui.bg(0).fg(7)
            box = draw_hud_ui.copy().expand(2, 1).fillc(" ").fg(5).etch(double=True)  # box
            box.copy().fg(15).zeroed().goto(2, 0).puts("Nyeogmi Choi")


class Target(NamedTuple):
    npc: NPCHandle
    vec: V2


class Targeter(object):
    def __init__(self):
        self._targets: List[Target] = []
        self._targeting_0: bool = False

    @property
    def target(self) -> Optional[NPCHandle]:
        if self._targeting_0:
            return self._targets[0].npc

    def untargeted(self) -> List[NPCHandle]:
        if self._targeting_0:
            return [i.npc for i in self._targets[1:]]
        else:
            return [i.npc for i in self._targets]

    def tab(self, player_xy):
        if self._targeting_0:
            assert self._targets  # can't be targeting 0 unless there are targets
            if len(self._targets) == 1:
                self._targeting_0 = False  # untarget
            else:
                self._targets.append(self._targets.pop(0))
        else:
            # target 0
            if self._targets:
                self._targets.sort(key=lambda tar: player_xy.manhattan(tar.vec))
                self._targeting_0 = True

    def untab(self, player_xy):
        if self._targeting_0:
            assert self._targets  # can't be targeting 0 unless there are targets
            self._targets.insert(0, self._targets.pop(-1))
        else:
            # target 0
            if self._targets:
                if len(self._targets) == 1:
                    self._targeting_0 = False  # untarget
                else:
                    self._targets.sort(key=lambda tar: player_xy.manhattan(tar.vec))
                    self._targeting_0 = True
                    self.untab(player_xy)  # target the furthest

    def update_possible(self, player_xy: V2, possible_targets: List[Target]):
        possible_corrected = {tar.npc: tar for tar in possible_targets}

        # copy it and sort, consume from end
        old_npcs = set(i.npc for i in self._targets)
        targets_to_add = sorted(
            [i for i in possible_targets if i.npc not in old_npcs],
            key=lambda tar: player_xy.manhattan(tar.vec), reverse=True
        )

        new_targets = []
        new_targeting_0 = self._targeting_0
        for i, old_tar in enumerate(self._targets):
            if old_tar.npc not in possible_corrected:
                # remove it
                if i == 0: new_targeting_0 = False
                continue

            correct_tar = possible_corrected[old_tar.npc]

            # shuffle new targets in
            while (
                any(targets_to_add) and  # w
                not (new_targeting_0 and i == 0) and  # never displace existing target

                # only add if the next is further away
                player_xy.manhattan(targets_to_add[-1].vec) < player_xy.manhattan(correct_tar.vec)
            ):
                new_targets.append(targets_to_add.pop())

            new_targets.append(correct_tar)

        while any(targets_to_add):
            new_targets.append(targets_to_add.pop())

        if len(new_targets) == 0:
            assert new_targeting_0 == False  # should be guaranteed by the loop

        self._targets = new_targets
        self._targeting_0 = new_targeting_0