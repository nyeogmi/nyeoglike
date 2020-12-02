from ds.vecs import V2, R2

import random

from ..tools import Cardinal, Carve, DoorSpread, LinkType, RoomType, Rule, Snake


def apartment() -> Carve:
    cell_sz_x = random.randint(3, 4)

    carve = Carve(DoorSpread(x=cell_sz_x + 1, y=cell_sz_x + 1, cx=random.randrange(cell_sz_x + 1), cy=random.randrange(cell_sz_x + 1)))

    living_room_width = random.randint(cell_sz_x + 3, cell_sz_x * 2 + 1)
    living_room_height = random.randrange(6, 8)
    living_room = carve.carve(V2.new(0, 0).sized(V2.new(living_room_width, living_room_height)), RoomType.LivingRoom)
    carve.freeze(living_room)

    def build_kitchen(snake: Snake):
        kitchen_width = random.randint(living_room_width - 1, living_room_width)
        kitchen_height = random.randint(living_room_height - 4, living_room_height - 2)
        kitchen_height = max(kitchen_height, 2)
        carve.freeze(snake.tunnel(V2.new(kitchen_width, kitchen_height), RoomType.Kitchen, LinkType.Complete, min_contact=kitchen_width))

    build_kitchen(carve.snake(living_room, Cardinal.North))

    def build_antechamber_once(snake: Snake):
        choice = random.choice([0, 0, 0, 1, 1])
        if choice == 0:
            # tiny room -- _just_ an entry zone
            carve.freeze(snake.tunnel(V2.new(3, 3), RoomType.EntryZone, LinkType.Door, min_contact=3))
        else:
            # yard-like
            carve.freeze(snake.tunnel(V2.new(living_room_height, 3), RoomType.Antechamber, LinkType.Door, min_contact=living_room_height))
            if random.choice([False, True]):
                snake.turn_right()
                carve.freeze(snake.tunnel(V2.new(3, 3), RoomType.Antechamber, LinkType.Door))

            random.choice([lambda: None, snake.turn_left])()
            carve.freeze(snake.tunnel(V2.new(3, 3), RoomType.EntryZone, LinkType.Door, min_contact=3))

    def build_antechamber(snake: Snake):
        for try_ in range(5):
            with snake.veto_point() as vetoed:
                return build_antechamber_once(snake)
        snake.veto()

    build_antechamber(carve.snake(living_room, Cardinal.West))

    bedroom_depth_l = random.randint(living_room_height // 2, living_room_height)
    bedroom_depth_r = random.randint(living_room_height // 2, living_room_height)

    def build_hall_room(snake: Snake, master: bool, depth: int) -> bool:
        for sz_x in range(cell_sz_x, 2, -1):
            room_type = (
                RoomType.Bedroom if master else
                RoomType.Bathroom if len(carve.ident_rooms(RoomType.Bathroom)) == 0 else
                RoomType.Bedroom
            )
            size = V2.new(sz_x + (random.randint(2, 4) if master else 0), depth + (random.randint(0, 1) if master else 0))
            size = V2.new(size.x, min(size.y, int(size.x * 1.5)))

            with snake.veto_point() as vetoed:
                # TODO: Bathroom
                snake.tunnel(
                    size,
                    room_type,
                    LinkType.Door,
                    min_contact=min(cell_sz_x, sz_x),
                    rule=Rule.Dense
                )

            if not vetoed:
                return True

        return False

    def build_bathroom(snake: Snake) -> bool:
        for sz_x in range(4, 2, -1):
            room_type = RoomType.Bathroom
            size = V2.new(sz_x, 3)

            with snake.veto_point() as vetoed:
                carve.freeze(snake.tunnel(size, room_type, LinkType.Door, min_contact=min(cell_sz_x, sz_x - 1), rule=Rule.Dense))

            if not vetoed:
                return True

        return False

    def build_closet(snake: Snake) -> bool:
        for sz_x in range(5, 1, -1):
            room_type = RoomType.Closet
            size = V2.new(sz_x, 1)

            with snake.veto_point() as vetoed:
                # TODO: Complete sometimes?
                r = snake.tunnel(size, room_type, LinkType.Door, min_contact=sz_x, rule=Rule.Dense)
                carve.freeze(r)  # should be frozen, closets are easy to wipe out

            if not vetoed:
                return True

        return False

    def build_hallway(snake: Snake, n_hall_nodes: int):
        if n_hall_nodes == 0:
            build_hall_room(snake, master=True, depth=living_room_width)
            return

        # bend
        for i in range(n_hall_nodes):
            carve.freeze(snake.tunnel(V2.new(3, cell_sz_x), RoomType.Hallway, LinkType.Complete, min_contact=3))

            def build_l():
                room1 = snake.branch()
                room1.turn_left()
                build_hall_room(room1, False, bedroom_depth_l)

            def build_r():
                room2 = snake.branch()
                room2.turn_right()
                build_hall_room(room2, False, bedroom_depth_r)

            # we assign bathroom first, so assign it to the smaller side
            if bedroom_depth_l < bedroom_depth_r:
                build_l()
                build_r()
            else:
                build_r()
                build_l()

        build_hall_room(snake, True, cell_sz_x)  # master bedroom

    has_junction = random.choice([False, True])

    if has_junction:
        n_hall_nodes = random.choice([0, 0, 1, 2])
        junc = carve.snake(living_room, Cardinal.East)
        junc.tunnel(V2.new(3, 3), RoomType.Hallway, LinkType.Complete, min_contact=3)

        h1 = junc.branch()
        h1.turn_right()
        build_hallway(h1, n_hall_nodes=n_hall_nodes)

        if random.choice([False, True, True]):
            n_hall_nodes = random.choice([0, 0, 1])
            h1 = junc.branch()
            if random.choice([False, False, True]):
                h1.turn_left()
            build_hallway(h1, n_hall_nodes=n_hall_nodes)
    else:
        n_hall_nodes = random.choice([0, 0, 0, 1, 1, 2, 3])
        h1 = carve.snake(living_room, Cardinal.East)
        build_hallway(h1, n_hall_nodes=n_hall_nodes)

    # TODO: Veto if the number of rooms is wrong

    bedrooms = carve.ident_rooms(room_type=RoomType.Bedroom)
    bathrooms = carve.ident_rooms(room_type=RoomType.Bathroom)
    hallways = carve.ident_rooms(room_type=RoomType.Hallway)
    # Freeze rooms
    for br in bedrooms: carve.freeze(br)
    for br in bathrooms: carve.freeze(br)
    for hw in hallways: carve.freeze(hw)

    # give every bedroom a closet if possible
    for br in bedrooms:
        for card in Cardinal.all_shuffled():
            if build_closet(carve.snake(br, card)):
                break
        else:
            # try really hard to have a closet
            carve.veto()

    bathroom_bedrooms = list(bedrooms)
    # if there aren't enough bathrooms, try to add some
    for try_ in range(10):
        bathrooms = carve.ident_rooms(room_type=RoomType.Bathroom)
        if len(bathrooms) >= len(bedrooms):
            break

        random_bedroom = random.choice(bathroom_bedrooms)
        for card in Cardinal.all_shuffled():
            if build_bathroom(carve.snake(random_bedroom, card)):
                bathroom_bedrooms.remove(random_bedroom)
                break

        if hallways:
            random_hallway = random.choice(hallways)
            for card in Cardinal.all_shuffled():
                if build_bathroom(carve.snake(random_hallway, card)):
                    break

    # now improve various room types
    for room_type in [RoomType.Bedroom, RoomType.Kitchen, RoomType.LivingRoom]:
        for r in carve.ident_rooms(room_type):
            carve.expand_densely(r)

    for room_type in [RoomType.Bedroom, RoomType.Kitchen, RoomType.LivingRoom]:
        for r in carve.ident_rooms(room_type):
            carve.erode_1tile_wonk(r)

    # erode room types that are often pointlessly large
    if random.choice([False, False, True]):
        for room_type in [RoomType.LivingRoom, RoomType.Kitchen]:
            for r in carve.ident_rooms(room_type):
                carve.erode(r, 1)

    # build links
    carve.build_links()

    # randomize rotation/flip
    carve.permute_at_random()

    # TODO: Generate a spanning tree to make sure the level is possible
    return carve

