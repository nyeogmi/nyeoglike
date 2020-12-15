from display import Colors, Drawer
from typing import Optional
from ..interest import Interest
from ..npc import NPCHandle
from ..world import World
from .window import draw_window, Window


class NPCView(object):
    def __init__(self, world: World):
        self._world = world
        self._npc = None
        self._view = None

    def select(self, npc: Optional[NPCHandle]):
        assert npc is None or isinstance(npc, NPCHandle)
        if self._npc == npc:
            return

        if npc:
            self._npc = npc
            self._view = _NPCView(self._world, npc)
        else:
            self._npc = None
            self._view = None

    def draw(self, drawer: Drawer):
        if self._view is None:
            return

        self._view.draw(drawer)


class _NPCView(object):
    def __init__(self, world: World, npc: NPCHandle):
        self._world = world
        self._npc = npc

    def draw(self, drawer: Drawer):
        target = self._world.npcs.get(self._npc)
        interest = self._world.interest[self._npc]

        # == draw border ==
        window = draw_window(drawer.copy().goto(30, 2).box(76, 6), fg=interest.color())
        window.title_bar.copy().fg(Colors.TermFGBold).puts(target.name)
        if interest != Interest.No:
            b2 = window.title_bar.copy().goto(len(target.name) + 1, 0).fg(Colors.TermFG)
            b2.puts("({})".format(interest.name))

        window.title_bar.copy().goto(
            window.title_bar.bounds.size.x - len("A - Mark"), 0
        ).fg(Colors.TermFGBold).puts("A - Mark")

        # == draw content ==
        sleepiness_s = "Sleepiness: {}".format(
            self._world.rhythms.get_sleepiness(self._npc)
        )  # TODO: Include count
        window.content.copy().goto(0, 0).puts(sleepiness_s)

        sceneflags_s = "Scene flags: {}".format(
            sorted(self._world.scene_flags.get_scene_flags(self._npc))
        )
        window.content.copy().goto(0, 1).puts(sceneflags_s)
