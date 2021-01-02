class Player(object):
    def __init__(self):
        self._name = "Nyeogmi"

    @property
    def name(self):
        return self._name
