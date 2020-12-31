from ds.code_registry import ref
from ..loaded_level import LoadedLevel


@ref("ephemera/residence")
def generate(world: "World", ll: LoadedLevel):
    print("generating residence ephemera for {}".format(ll))
    pass


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...world import World
