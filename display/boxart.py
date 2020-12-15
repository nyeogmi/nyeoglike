from ds.vecs import R2, V2

from .screen import Drawer


class Single(object):
    VERT = chr(0xB3)
    HORZ = chr(0xC4)
    TL = chr(0xDA)
    BL = chr(0xC0)
    TR = chr(0xBF)
    BR = chr(0xD9)


class Double(object):
    VERT = chr(0xBA)
    HORZ = chr(0xCD)
    TL = chr(0xC9)
    BL = chr(0xC8)
    TR = chr(0xBB)
    BR = chr(0xBC)


def draw(d: Drawer, rect: R2, double=False):
    mold = Double if double else Single

    assert rect.size.x > 1 and rect.size.y > 1

    for x in range(1, rect.size.x - 1):
        d.goto(rect.top.x + x, rect.top.y).puts(mold.HORZ)
        d.goto(rect.top.x + x, rect.top.y + rect.size.y - 1).puts(mold.HORZ)

    for y in range(1, rect.size.y - 1):
        d.goto(rect.top.x, rect.top.y + y).puts(mold.VERT)
        d.goto(rect.top.x + rect.size.x - 1, rect.top.y + y).puts(mold.VERT)

    d.goto(rect.top.x, rect.top.y).puts(mold.TL)
    d.goto(rect.top.x + rect.size.x - 1, rect.top.y).puts(mold.TR)
    d.goto(rect.top.x, rect.top.y + rect.size.y - 1).puts(mold.BL)
    d.goto(rect.top.x + rect.size.x - 1, rect.top.y + rect.size.y - 1).puts(mold.BR)
