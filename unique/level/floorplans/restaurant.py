from ds.vecs import V2, R2

import random

from ..tools import Cardinal, Carve, Grid, LinkType, RoomType, Rule, Snake


def restaurant() -> Carve:
    cell_sz_x = random.randint(3, 4)

    carve = Carve(
        Grid(
            x=cell_sz_x + 1,
            y=cell_sz_x + 1,
            cx=random.randrange(cell_sz_x + 1),
            cy=random.randrange(cell_sz_x + 1),
        )
    )

    # TODO: RNG from a few of these
    build_basic_layout(carve)

    def build_bathroom(snake: Snake) -> bool:
        for sz_x in range(4, 2, -1):
            room_type = RoomType.Bathroom
            size = V2.new(sz_x, 3)

            with snake.veto_point() as vetoed:
                carve.freeze(
                    snake.tunnel(
                        size,
                        room_type,
                        LinkType.Door,
                        min_contact=min(cell_sz_x, sz_x - 1),
                        rule=Rule.Dense,
                    )
                )

            if not vetoed:
                return True

        return False

    # == build bathrooms ==
    # try twice in antechambers
    consumer_bathroom_rooms = [
        *carve.ident_rooms(RoomType.Gallery),
        *carve.ident_rooms(RoomType.Antechamber),
        *carve.ident_rooms(RoomType.Antechamber),
    ]
    for try_ in range(10):
        if len(carve.ident_rooms(RoomType.Bathroom)) >= 2:
            break

        random_room = random.choice(consumer_bathroom_rooms)
        for card in Cardinal.all_shuffled():
            if build_bathroom(carve.snake(random_room, card)):
                consumer_bathroom_rooms.remove(random_room)
                break
    prev_bathrooms = len(carve.ident_rooms(RoomType.Bathroom))

    # and for the kitchen
    employee_bathroom_rooms = [
        *carve.ident_rooms(RoomType.Kitchen),
    ]
    for try_ in range(10):
        if len(carve.ident_rooms(RoomType.Bathroom)) - prev_bathrooms >= 1:
            break

        random_room = random.choice(employee_bathroom_rooms)
        for card in Cardinal.all_shuffled():
            if build_bathroom(carve.snake(random_room, card)):
                employee_bathroom_rooms.remove(random_room)
                break

    # == improve various room types ==
    for room_type in [RoomType.Gallery, RoomType.Antechamber]:
        for r in carve.ident_rooms(room_type):
            carve.expand_densely(r)

    for room_type in [RoomType.Gallery, RoomType.Antechamber]:
        for r in carve.ident_rooms(room_type):
            carve.erode_1tile_wonk(r)

    # build links
    carve.build_links()

    # randomize rotation/flip
    carve.permute_at_random()

    return carve


def build_basic_layout(carve: Carve):
    gallery_width = random.randint(9, 12)
    gallery_height, gallery_corner_width = random.choice(
        [
            ((gallery_width * 2) // 3, (gallery_width * 1) // 3),
            ((gallery_width * 1) // 3, (gallery_width * 2) // 3),
        ]
    )
    gallery_corner_depthback = random.randint(2, 5)

    galleries = []
    gallery = carve.carve(
        V2.new(0, 0).sized(V2.new(gallery_width, gallery_height)), RoomType.Gallery
    )

    snake_2 = carve.snake(gallery, Cardinal.East)
    galleries.append(
        snake_2.tunnel(
            V2.new(gallery_height, gallery_corner_width),
            RoomType.Gallery,
            LinkType.Complete,
            min_contact=gallery_height,
        )
    )

    snakes = [snake_2]

    pct = random.randrange(100)
    if pct in range(0, 50):
        snake_1 = carve.snake(gallery, Cardinal.West)
        galleries.append(
            snake_1.tunnel(
                V2.new(gallery_height, gallery_corner_width),
                RoomType.Gallery,
                LinkType.Complete,
                min_contact=gallery_height,
            )
        )
        snake_1.turn_right()
        snakes.append(snake_1)

    pct = random.randrange(100)
    if pct in range(0, 50):
        snake_2.turn_left()
    elif pct in range(50, 70):
        snake_2.turn_right()
    else:
        pass

    for snake in snakes:
        galleries.append(
            snake.tunnel(
                V2.new(gallery_corner_width, gallery_corner_depthback),
                RoomType.Gallery,
                LinkType.Complete,
                min_contact=gallery_corner_width,
            )
        )

    kitchen_snake = carve.snake(gallery, Cardinal.North)
    kitchen_snake.tunnel(
        V2.new(gallery_width, max(2, gallery_corner_depthback + random.randint(-2, 2))),
        RoomType.Kitchen,
        LinkType.Counter,  # TODO: A link type for counters
        min_contact=gallery_width,
    )

    pct = random.randrange(100)
    if pct in range(0, 50):
        # leave it as is
        pass
    elif pct in range(50, 100):  # TODO: find ways to generate this split up
        width = max(min(4, gallery_width), gallery_width - random.randint(1, 4))
        kitchen_snake.tunnel(
            V2.new(width, random.randint(4, 7)),
            RoomType.Kitchen,
            LinkType.Complete,
            min_contact=width,
            rule=Rule.Dense,
        )
    else:
        raise AssertionError("impossible")

    for rm in carve.ident_rooms(RoomType.Gallery):
        carve.freeze(rm)
    for rm in carve.ident_rooms(RoomType.Kitchen):
        carve.freeze(rm)

    snake_2.turn_right()
    pct = random.randrange(100)
    if pct in range(0, 100):
        entry_zone_depth = random.randrange(3, 7)
        entry_zone = snake_2.tunnel(
            V2.new(gallery_corner_depthback, entry_zone_depth),
            RoomType.Antechamber,
            LinkType.Complete,
            min_contact=gallery_corner_depthback,
        )
        carve.freeze(entry_zone)
        pct = random.randrange(100)
        if pct in range(0, 33):
            snake_2.turn_right()
        elif pct in range(33, 66):
            snake_2.turn_left()

        entry = snake_2.tunnel(
            V2.new(3, 3),
            RoomType.EntryZone,
            LinkType.Door,
            min_contact=3,
        )
        carve.freeze(entry)
    else:
        raise AssertionError("impossible condition")
