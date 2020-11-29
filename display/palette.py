from typing import List, Tuple


def _load(s: str) -> Tuple[int, int, int]:
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)

SOLARIZED: List[Tuple[int, int, int]] = [
    (0x00, 0x2b, 0x36),
    (0x07, 0x36, 0x42),
    (0x58, 0x6e, 0x75),
    (0x65, 0x7b, 0x83),
    (0x83, 0x94, 0x96),
    (0x93, 0xa1, 0xa1),
    (0xee, 0xe8, 0xd5),
    (0xfd, 0xf6, 0xe3),
    (0xb5, 0x89, 0x00),
    (0xcb, 0x4b, 0x16),
    (0xdc, 0x32, 0x2f),
    (0xd3, 0x36, 0x82),
    (0x6c, 0x71, 0xc4),
    (0x26, 0x8b, 0xd2),
    (0x2a, 0xa1, 0x98),
    (0x85, 0x99, 0x00),
]

PAPER_COLOR: List[Tuple[int, int, int]] = list(map(
    _load, [
        "262626", "af0000", "5faf00", "dfaf5f",
        # darkening the gray (7) from d0d0d0
        "303030", "5f8787", "df875f", "b8b8b8",
        "8a8a8a", "5faf5f", "afdf00", "ff5faf",
        "444444", "ff5faf", "00afaf", "ffffff"  # TODO: ff5faf is a duplicate
        # TODO: Make 15 = 5fafdf like in the original?
    ]
))


PALETTE: List[Tuple[int, int, int]] = PAPER_COLOR
N_COLORS = len(PALETTE)

