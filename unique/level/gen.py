from .tools import InteriorDesigner
from .unloaded_level import UnloadedLevel


def apartment() -> UnloadedLevel:
    from .floorplans.apartment import apartment as apt_floorplan
    from .interiors.apartment import apartment as apt_interior

    plan = apt_floorplan()
    interior = plan.to_interior()
    apt_interior(interior)
    return interior.to_level()
