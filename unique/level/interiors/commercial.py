from unique.item.common.furniture import BED, CHAIR, COUNTER, TABLE
from ..tools import InteriorDesigner, RoomType, SpawnType, Hint
import random
from ds.vecs import V2, R2


def commercial(interior: InteriorDesigner):
    galleries = list(interior.ident_rooms(RoomType.Gallery))
    first_gallery = galleries[0]
    for gallery in galleries[1:]:
        interior.merge_rooms(first_gallery, gallery)

    # invalid now
    del first_gallery
    del gallery

    for rm in interior.ident_rooms(RoomType.Kitchen) + interior.ident_rooms(
        RoomType.Gallery
    ):
        for i in rm.hinted(Hint.Counter):
            rm.at(i, COUNTER)

    for rm in interior.ident_rooms(RoomType.Gallery):
        for i in rm.hinted(Hint.Counterside):
            rm.at(i, CHAIR)

    for rm in interior.ident_rooms(RoomType.Kitchen):
        for i in rm.hinted(Hint.Counterside):
            rm.at(i)
            rm.mark_spawn(SpawnType.Employee)

    # place tables in pods
    spacing_dist = 4
    spacing_constant_x = random.randrange(spacing_dist)
    spacing_constant_y = random.randrange(spacing_dist)

    for rm in interior.ident_rooms(RoomType.Gallery):
        counterside_expanded = set()
        for i in rm.hinted(Hint.Counterside):
            for n in i.neighbors():
                counterside_expanded.add(n)

        for i in rm.hinted(Hint.Counter):
            for n in i.neighbors():
                counterside_expanded.add(n)

        all_safe_tiles = set(rm.all_tiles())
        all_safe_shuf = list(all_safe_tiles)
        random.shuffle(all_safe_shuf)

        table_sz_x, table_sz_y = 1, 1
        pct = random.randrange(0, 100)
        if pct in range(0, 20):
            table_sz_x = random.randint(1, 3)
        else:
            table_sz_y = random.randint(1, 3)

        for tsx, tsy in [(table_sz_x, table_sz_y), (table_sz_y, table_sz_x)]:
            for v in all_safe_shuf:
                # TODO: Do a second pass and try to place rotated tables
                bounds_inside = v.sized(V2(tsx, tsy))
                bounds = bounds_inside.expand(V2.new(1, 1))
                corners = set(bounds.inclusive_corners())
                if any(
                    t not in all_safe_tiles or t in counterside_expanded for t in bounds
                ):
                    continue

                for b in bounds_inside:
                    rm.at(b, TABLE)

                for b in bounds:
                    if b in bounds_inside:
                        continue
                    if b in corners:
                        continue
                    rm.at(b, CHAIR)

                for b in bounds:
                    all_safe_tiles.discard(b)
