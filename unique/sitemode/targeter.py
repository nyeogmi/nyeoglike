from typing import List, NamedTuple, Optional

from ds.vecs import V2

from ..npc import NPCHandle


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
            key=lambda tar: player_xy.manhattan(tar.vec),
            reverse=True,
        )

        new_targets = []
        new_targeting_0 = self._targeting_0
        for i, old_tar in enumerate(self._targets):
            if old_tar.npc not in possible_corrected:
                # remove it
                if i == 0:
                    new_targeting_0 = False
                continue

            correct_tar = possible_corrected[old_tar.npc]

            # shuffle new targets in
            while (
                any(targets_to_add)
                and not (new_targeting_0 and i == 0)  # w
                and  # never displace existing target
                # only add if the next is further away
                player_xy.manhattan(targets_to_add[-1].vec)
                < player_xy.manhattan(correct_tar.vec)
            ):
                new_targets.append(targets_to_add.pop())

            new_targets.append(correct_tar)

        while any(targets_to_add):
            new_targets.append(targets_to_add.pop())

        if len(new_targets) == 0:
            assert new_targeting_0 == False  # should be guaranteed by the loop

        self._targets = new_targets
        self._targeting_0 = new_targeting_0
