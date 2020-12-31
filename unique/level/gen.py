from . import ephemera
from .tools import InteriorDesigner, RoomType
from .unloaded_level import UnloadedLevel


def residence() -> UnloadedLevel:
    from .floorplans.residence import residence as res_floorplan
    from .interiors.residence import residence as res_interior

    plan = res_floorplan()
    interior = plan.to_interior()
    res_interior(interior)

    for ez in interior.ident_rooms(RoomType.EntryZone):
        ez.fill_with_exits()

    return interior.to_level(ephemera.residence)


def restaurant() -> UnloadedLevel:
    from .floorplans.restaurant import restaurant as res_floorplan

    # TODO: Generalized commercial interior
    from .interiors.commercial import commercial as res_interior

    plan = res_floorplan()
    interior = plan.to_interior()
    res_interior(interior)

    for ez in interior.ident_rooms(RoomType.EntryZone):
        ez.fill_with_exits()

    return interior.to_level(ephemera.restaurant)
