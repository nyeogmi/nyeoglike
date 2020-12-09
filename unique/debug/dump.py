from contextlib import contextmanager
from io import StringIO


class Dump(object):
    def __init__(self):
        self._objs = []

    def obj(self, name) -> "ObjDump":
        od = ObjDump(name)
        self._objs.append(od)
        return od

    def render(self) -> str:
        return "\n\n".join(o.render() for o in self._objs)


class ObjDump(object):
    def __init__(self, name):
        self._name = name
        self._prefix = []
        self._kv = []

    def add(self, name, value):
        self._kv.append(((*self._prefix, str(name)), value))

    @contextmanager
    def prefix(self, pfx):
        self._prefix.append(str(pfx))
        yield
        self._prefix.pop()

    def render(self) -> str:
        out = StringIO()
        out.write("== {} ==".format(self._name))
        for k, v in self._kv:  # TODO: Format better?
            out.write("\n{}: {}".format(".".join(k), v))
        return out.getvalue()