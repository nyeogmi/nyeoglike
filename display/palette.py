from typing import List, NamedTuple, Tuple


class Color(NamedTuple):
    color: int


def load(s: str):
    assert len(s) == 6
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def load_swatch(swatch_name):
    # TODO: Better code to do this, don't use pygame, handle alternate FS paths.
    import pygame

    pygame.init()
    swatch_image = pygame.image.load("images/{}.png".format(swatch_name))
    assert swatch_image.get_width() * swatch_image.get_height() == 16  # for now

    swatch = []
    for y in range(swatch_image.get_height()):
        for x in range(swatch_image.get_width()):
            (r, g, b, _) = swatch_image.get_at((x, y))
            swatch.append((r, g, b))
    return swatch


class Colors(object):
    SWATCH = load_swatch("palette")
    N = len(SWATCH)

    assert N == 16  # for now

    Black0 = Color(0)
    Black1 = Color(1)

    Grey0 = Color(2)
    Grey1 = Color(3)  # this is also deep green, coincidentally

    White0 = Color(4)
    White1 = Color(5)

    YellowGreen0 = Color(6)
    YellowGreen1 = Color(7)

    GreenNeg = Color(3)
    Green0 = Color(8)
    Green1 = Color(9)

    Red0 = Color(10)
    Red1 = Color(11)

    # it's too purplish at low values to be blue
    Sky0 = Color(12)
    Sky1 = Color(13)

    Fuchsia0 = Color(14)
    Fuchsia1 = Color(15)

    TermBG = Black0
    TermFG = White0
    TermFGBold = White1

    TermHighlightBG = Fuchsia1
    TermHighlightBGInactive = Grey1

    FadeBG = Black1
    FadeFG = Grey1

    WorldBG = Black0
    WorldFG = White0

    WorldUnseenBG = Black1
    WorldUnseenFG = Grey1

    ResourceGeneric = Grey1  # TODO: Bad choice?

    Player = White1
    NPCNoInterest = YellowGreen0
    NPCFriend = YellowGreen1
    NPCLove = Fuchsia1
    MSGSystem = Grey1

    QuestSucceeded = Fuchsia1
    QuestFailed = Red1


# Re-export certain colors
# If items have a color not in this list, that's suspicious
class ItemColors(object):
    Mundane = Colors.GreenNeg

    Green0 = Colors.Green0
    Green1 = Colors.Green1

    Red0 = Colors.Red0
    Red1 = Colors.Red1

    # it's too purplish at low values to be blue
    Sky0 = Colors.Sky0
    Sky1 = Colors.Sky1

    Fuchsia0 = Colors.Fuchsia0
    Fuchsia1 = Colors.Fuchsia1

    ALL = [Green0, Green1, Red0, Sky1, Mundane, Red1, Sky0, Fuchsia1, Fuchsia0]

    @classmethod
    def name(cls, value):
        if value == cls.Mundane:
            return "Mundane"
        elif value == cls.Green0:
            return "Green0"
        elif value == cls.Green1:
            return "Green1"
        elif value == cls.Red0:
            return "Red0"
        elif value == cls.Red1:
            return "Red1"
        elif value == cls.Sky0:
            return "Sky0"
        elif value == cls.Sky1:
            return "Sky1"
        elif value == cls.Fuchsia0:
            return "Fuchsia0"
        elif value == cls.Fuchsia1:
            return "Fuchsia1"

        raise NotImplementedError("don't know how to name: {}".format(value))


class WallColors(object):
    Base = Colors.WorldFG
    Yellow0 = Colors.YellowGreen0
    Green0 = Colors.Green0
    Red0 = Colors.Red0
    Sky0 = Colors.Sky0
    Fuchsia0 = Colors.Fuchsia0

    ALL = [Base, Yellow0, Green0, Red0, Sky0, Fuchsia0]
    COLORFUL = [Yellow0, Green0, Red0, Sky0, Fuchsia0]
    BANAL = [Base]
