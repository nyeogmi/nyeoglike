from typing import List, NamedTuple, Tuple


class Color(NamedTuple):
    color: int


def load(s: str):
    assert len(s) == 6
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


class Colors(object):
    SWATCH = tuple(
        map(
            load,
            [
                "171712",
                "1E1F1F",
                "27292A",
                "5D6F6F",
                "DDDADB",
                "FFFFFF",
                "FCB97D",
                "FF4A59",
                "8C5DEA",
                "DCED31",
                "E03616",
            ],
        )
    )
    N = len(SWATCH)

    DarkestBlack = Color(0)
    DarkBlack = Color(1)
    DarkGray = Color(2)
    DarkBlue = Color(3)

    MidWhite = Color(4)
    BrightWhite = Color(5)
    CreamWhite = BrightWhite  # TODO: Different?

    Yellow = Color(6)
    BrightPink = Color(7)
    BrightPurp = Color(8)
    BrightGreen = Color(9)

    BrightOrange = Yellow  # TODO: Different

    BloodRed = Color(10)

    TermBG = DarkestBlack
    TermFG = MidWhite
    TermFGBold = BrightWhite

    TermHighlightBG = BrightPurp
    TermHighlightBGInactive = DarkBlue

    FadeBG = DarkBlack
    FadeFG = DarkBlue

    WorldBG = DarkestBlack  # was DarkBlack
    WorldFG = MidWhite

    WorldUnseenBG = DarkBlack
    WorldUnseenFG = DarkBlue

    ResourceGeneric = DarkBlue

    Player = BrightWhite
    NPCNoInterest = Yellow
    NPCFriend = BrightGreen
    NPCLove = BrightPink
    MSGSystem = DarkBlue

    QuestSucceeded = BrightPurp
    QuestFailed = BloodRed
