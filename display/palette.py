from typing import List, NamedTuple, Tuple


class Color(NamedTuple):
    color: int


def load(s: str):
    assert len(s) == 6
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


class Colors(object):
    """
    SWATCH = tuple(map(load, [
        "262626", "af0000", "5faf00", "dfaf5f",
        # darkening the gray (7) from d0d0d0
        "303030", "5f8787", "df875f", "b8b8b8",
        "8a8a8a", "5faf5f", "afdf00", "ff5faf",
        "444444", "ff5faf", "00afaf", "ffffff"  # TODO: ff5faf is a duplicate
        # TODO: Make 15 = 5fafdf like in the original?
    ]))
    N = len(SWATCH)
    """
    SWATCH = tuple(map(load, [
        # "1A1A13", "23262F", "3A3A4A", "5D6F6F",
        # "E0D8DB", "FFFFFF",
        "171712", "1E1F1F", "27292A", "5D6F6F",
        "DDDADB", "FFFFFF",

        "FCB97D", "FF4A59", "8C5DEA", "DCED31",
        "E03616"
    ]))
    N = len(SWATCH)

    DarkestBlack = Color(0)
    DarkBlack = Color(1)
    DarkGray = Color(2)
    DarkBlue = Color(3)

    MidWhite = Color(4)
    BrightWhite = Color(5)

    Yellow = Color(6)
    BrightPink = Color(7)
    BrightPurp = Color(8)
    BrightGreen = Color(9)

    BloodRed = Color(10)

    TermBG = DarkestBlack
    TermFG = MidWhite
    TermFGBold = BrightWhite

    FadeBG = DarkBlack
    FadeFG = DarkBlue

    WorldBG = DarkBlack
    Streak1 = DarkGray
    Streak2 = DarkGray  # DarkBlue

    WorldFG = MidWhite

    ResourceGeneric = DarkBlue

    Player = BrightWhite
    NPCNoInterest = Yellow
    NPCFriend = BrightGreen
    NPCLove = BrightPink
    MSGSystem = DarkBlue