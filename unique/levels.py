from ds.gensym import Gensym, Sym
from typing import Dict, NamedTuple
from .level import Level


class LevelHandle(NamedTuple):
    ident: Sym


class Levels(object):
    def __init__(self):
        self._all: Dict[LevelHandle, Level] = {}
        self._sym = Gensym("LVL")

    def generate_home(self, npc: "NPCHandle"):



from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .npc import NPCHandle
