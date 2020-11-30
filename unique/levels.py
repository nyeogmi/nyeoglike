from ds.gensym import Gensym, Sym


class Levels(object):
    def __init__(self):
        self._all = {}
        self._sym = Gensym("NPC")
