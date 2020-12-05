import random
import unicodedata


def strip_accents(s):
    nkfd = unicodedata.normalize("NFKD", s)
    return "".join([c for c in nkfd if not unicodedata.combining(c)])


def load(fname):
    with open("ascii/names/%s.ascii" % fname, "rt", encoding="utf-8") as f:
        lines = f.read().strip().split("\n")
        return sorted([i for i in set(strip_accents(l) for l in lines) if i])


AMERICAN_FEMININE_FIRST = load("american/feminine_first")
AMERICAN_FEMININE_FIRST_CLASSWEIRD = load("american/feminine_first_classweird")
AMERICAN_FEMININE_FIRST_ENBY = load("american/feminine_first_enby")
AMERICAN_FEMININE_FIRST_FUN = load("american/feminine_first_fun")
AMERICAN_FEMININE_FIRST_LITERARY = load("american/feminine_first_literary")
AMERICAN_FEMININE_FIRST_NOBJECT = load("american/feminine_first_nobject")

AMERICAN_MASCULINE_FIRST = load("american/masculine_first")
AMERICAN_MASCULINE_FIRST_ENBY = load("american/masculine_first_enby")
AMERICAN_MASCULINE_FIRST_LITERARY = load("american/masculine_first_literary")
AMERICAN_MASCULINE_FIRST_NONWHITE = load("american/masculine_first_nonwhite")

AMERICAN_LAST_COMMON = load("american/last_common")
AMERICAN_LAST_WEIRD = load("american/last_weird")

EUSKARA_FEMININE_FIRST = load("euskara/feminine_first")
EUSKARA_MASCULINE_FIRST = load("euskara/masculine_first")

MANDARIN_FIRST = load("mandarin/first")
MANDARIN_LAST = load("mandarin/last")

OBJECTS_NONSILLY = load("objects/nonsilly")
OBJECTS_SILLY = load("objects/silly")

SPANISH_FEMININE_FIRST = load("spanish/feminine_first")
SPANISH_MASCULINE_FIRST = load("spanish/masculine_first")
SPANISH_LAST = load("spanish/last")

VIETNAMESE_FEMININE_FIRST = load("vietnamese/feminine_first")
VIETNAMESE_MASCULINE_FIRST = load("vietnamese/masculine_first")
VIETNAMESE_LAST = load("vietnamese/last")


def multi_pick(*lists):
    n = sum(len(i) for i in lists)

    choice = random.randrange(n)
    for l in lists:
        if choice < len(l):
            return l[choice]
        choice -= len(l)

    raise AssertionError("should be unreachable")


def american_masculine_first():
    if random.randrange(3) == 0:
        return multi_pick(AMERICAN_MASCULINE_FIRST)

    return multi_pick(
        AMERICAN_MASCULINE_FIRST_ENBY,
        AMERICAN_MASCULINE_FIRST_LITERARY,
        AMERICAN_MASCULINE_FIRST_NONWHITE,
    )


def american_feminine_first():
    if random.randrange(3) == 0:
        return multi_pick(AMERICAN_FEMININE_FIRST)

    return multi_pick(
        AMERICAN_FEMININE_FIRST_CLASSWEIRD,
        AMERICAN_FEMININE_FIRST_ENBY,
        AMERICAN_FEMININE_FIRST_FUN,
        AMERICAN_FEMININE_FIRST_LITERARY,
        AMERICAN_FEMININE_FIRST_NOBJECT,
    )


def american_last():
    if random.randrange(2) == 0:
        return multi_pick(AMERICAN_LAST_COMMON)

    return multi_pick(AMERICAN_LAST_WEIRD)


def mandarin_first():
    return multi_pick(MANDARIN_FIRST)


def mandarin_last():
    return multi_pick(MANDARIN_LAST)


def objects_first():
    return multi_pick(OBJECTS_NONSILLY, OBJECTS_SILLY)


def spanish_masculine_first():
    if random.randrange(10) == 0:
        return multi_pick(EUSKARA_MASCULINE_FIRST)

    return multi_pick(SPANISH_MASCULINE_FIRST)


def spanish_feminine_first():
    if random.randrange(10) == 0:
        return multi_pick(EUSKARA_FEMININE_FIRST)

    return multi_pick(SPANISH_FEMININE_FIRST)


def spanish_last(): return multi_pick(SPANISH_LAST)


def vietnamese_masculine_first(): return multi_pick(VIETNAMESE_MASCULINE_FIRST)
def vietnamese_feminine_first(): return multi_pick(VIETNAMESE_FEMININE_FIRST)
def vietnamese_last(): return multi_pick(VIETNAMESE_LAST)


def generate() -> str:
    if random.choice([False, True]):
        american_first = american_masculine_first
        spanish_first = spanish_masculine_first
        vietnamese_first = vietnamese_masculine_first
    else:
        american_first = american_feminine_first
        spanish_first = spanish_feminine_first
        vietnamese_first = vietnamese_feminine_first

    pct = random.randrange(100)
    if pct in range(0, 50):
        first = american_first()
        last = american_last()

        pct = random.randrange(100)
        if pct in range(0, 15):
            # gratuitous use of other languages
            pct = random.randrange(100)
            if pct in range(0, 40):
                first = spanish_first()
            elif pct in range(40, 100):
                first = mandarin_first()

    elif pct in range(50, 100):
        pct = random.randrange(100)

        if pct in range(0, 40):
            first = spanish_first()
            last = spanish_last()
            chance_american_firstname = 25
        elif pct in range(30, 70):
            first = mandarin_first()
            last = mandarin_last()
            chance_american_firstname = 75
        elif pct in range(70, 100):
            first = vietnamese_first()
            last = vietnamese_last()
            chance_american_firstname = 55
        else:
            raise AssertionError("not reachable")

        pct = random.randrange(100)  # chances of getting an american first name
        if pct in range(0, chance_american_firstname):
            first = american_first()
        elif pct in range(chance_american_firstname, 100):
            pass
        else:
            raise AssertionError("not reachable")

    else:
        raise AssertionError("not reachable")

    pct = random.randrange(100)
    if pct in range(0, 10):
        first = objects_first()

    return "{} {}".format(first, last)


FOREIGN_FIRST = load("foreign_first")
FOREIGN_LAST = load("foreign_last")
