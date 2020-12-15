from unique.item.common.furniture import BED

from ..tools import InteriorDesigner, RoomType, SpawnType


def residence(interior: InteriorDesigner):
    for br in interior.ident_rooms(RoomType.Bedroom):
        br.boundary(BED)
        br.mark_spawn(SpawnType.Sleep)
        br.mark_spawn_neighbors(SpawnType.Bedside)

    # TODO: Any other room or furniture
