import random
from display import Colors, WallColors
from raw.furniture import BED

from ..tools import InteriorDesigner, RoomType, SpawnType
from ..wallpaper import WallTile


def residence(interior: InteriorDesigner):
    interior.wallpaper.set_default(WallTile.generate_wallpaper())

    for cl in interior.ident_rooms(RoomType.Closet):
        interior.wallpaper.add(
            cl.all_tiles_and_interior_wall(), WallTile.generate_paneling()
        )

    for cl in interior.ident_rooms(RoomType.Bathroom):
        interior.wallpaper.add(
            cl.all_tiles_and_interior_wall(), WallTile.generate_bathroom_tile()
        )

    for br in interior.ident_rooms(RoomType.Bedroom):
        br.boundary(BED)
        br.mark_spawn(SpawnType.Sleep)
        br.mark_spawn_neighbors(SpawnType.Bedside)

    # TODO: Any other room or furniture
