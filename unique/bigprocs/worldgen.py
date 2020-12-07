from ..world import World
from ..worldmap import ZoneType

from . import jobs_and_houses


N_NPCS = 50
N_ENTERPRISES = 1


def main(w: World):
    for i in range(N_NPCS):
        w.npcs.generate()

    for i in range(N_ENTERPRISES):
        w.enterprises.generate(w, ZoneType.Restaurant)  # TODO: Generate other enterprises

    print([w.npcs.get(i).name for i in w.npcs._all.keys()])  # TODO: Better way to do this for non-debugging in the future

    w.friendships.mingle(w, 5)  # every NPC gets 5 friends
    jobs_and_houses.run(w)