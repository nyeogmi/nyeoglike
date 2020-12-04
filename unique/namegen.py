import random

def load(fname):
    with open("ascii/names/%s.ascii" % fname, "rt") as f:
        lines = f.read().strip().split("\n")
        return sorted(set(lines))


def generate() -> str:
    k = random.random()
    if k < 0.25:
        firsts = DOMESTIC_FIRST
        lasts = DOMESTIC_LAST
    elif k < 0.6:
        firsts = DOMESTIC_FIRST
        lasts = FOREIGN_LAST
    elif k < 0.9:
        firsts = FOREIGN_FIRST
        lasts = DOMESTIC_LAST
    else:
        firsts = FOREIGN_FIRST
        lasts = FOREIGN_LAST

    first = random.choice(firsts)
    last = random.choice(lasts)

    return "{} {}".format(first, last)


DOMESTIC_FIRST = load("domestic_first")
DOMESTIC_LAST = load("domestic_last")
FOREIGN_FIRST = load("foreign_first")
FOREIGN_LAST = load("foreign_last")
