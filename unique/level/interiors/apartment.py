from unique.item.common import pizza
from ..tools import InteriorDesigner, RoomType


def apartment(interior: InteriorDesigner):
    for br in interior.ident_rooms(RoomType.Bedroom):
        br.center(pizza)
