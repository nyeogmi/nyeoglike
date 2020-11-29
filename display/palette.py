from typing import List, NamedTuple, Tuple


class Color(NamedTuple):
    color: int


def load(s: str):
    assert len(s) == 6
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


class Colors(object):
    SWATCH = tuple(map(load, [
        "262626", "af0000", "5faf00", "dfaf5f",
        # darkening the gray (7) from d0d0d0
        "303030", "5f8787", "df875f", "b8b8b8",
        "8a8a8a", "5faf5f", "afdf00", "ff5faf",
        "444444", "ff5faf", "00afaf", "ffffff"  # TODO: ff5faf is a duplicate
        # TODO: Make 15 = 5fafdf like in the original?
    ]))
    N = len(SWATCH)

    DarkBlack = Color(0)
    BloodRed = Color(1)
    Yellow = Color(3)
    DarkGray = Color(4)
    DarkBlue = Color(5)
    MidWhite = Color(7)
    BrightGreen = Color(10)
    BrightPink = Color(13)
    Azure = Color(14)
    BrightWhite = Color(15)

    TermBG = DarkBlack
    TermFG = MidWhite
    TermFGBold = BrightWhite

    WorldBG = DarkBlack
    Streak1 = DarkGray
    Streak2 = DarkBlue

    WorldFG = MidWhite

    ResourceGeneric = DarkBlue

    Player = BrightWhite
    NPCNoInterest = Yellow
    NPCFriend = BrightGreen
    NPCLove = BrightPink
    MSGSystem = DarkBlue