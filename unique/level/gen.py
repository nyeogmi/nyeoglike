from .tools import InteriorDesigner, RoomType
from .unloaded_level import UnloadedLevel


def apartment() -> UnloadedLevel:
    from .floorplans.apartment import apartment as apt_floorplan
    from .interiors.apartment import apartment as apt_interior

    plan = apt_floorplan()
    interior = plan.to_interior()
    apt_interior(interior)
    for ez in interior.ident_rooms(RoomType.EntryZone):
        ez.fill_with_exits()
    return interior.to_level()
