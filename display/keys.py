from typing import NamedTuple, Optional

# maps uncaps to caps
_LETTERS = dict(zip(
    "abcdefghijklmnopqrstuvwxyz",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
))

# maps uncaps to caps
_UNLETTERS = {v: k for k, v in _LETTERS.items()}

# maps uncaps to caps
_SYMS = dict(zip(
    "`1234567890-=[]\\;',./",
    "~!@#$%^&*()_+{}|:\"<>?",
))

# maps uncaps to caps
_UNSYMS = {v: k for k, v in _SYMS.items()}


class Key(NamedTuple):
    keycode: str

    control: bool
    shift: bool
    alt: bool
    caps_lock: bool

    @classmethod
    def new(
        cls,
        keycode,
        control=False, shift=False, alt=False, caps_lock=False
    ) -> "Key":
        assert keycode in Keycodes.ALL

        assert isinstance(control, bool)
        assert isinstance(shift, bool)
        assert isinstance(alt, bool)
        assert isinstance(caps_lock, bool)

        return Key(keycode, control, shift, alt, caps_lock)

    def __str__(self) -> str:
        return "<{}>".format("".join([
            "C-" if self.control else "",
            "S-" if self.shift else "",
            "A-" if self.alt else "",
            self.keycode,
            "!" if self.caps_lock else ""
        ]))

    def text(self) -> Optional[str]:
        # for UI forms -- this is what's being _typed_ by a character
        if self.control or self.alt:
            return None

        alpha_upper = self.caps_lock != self.shift
        sym_upper = self.shift

        if self.keycode in _LETTERS:
            if alpha_upper:
                return _LETTERS[self.keycode]
            else:
                return self.keycode

        if self.keycode in _SYMS:
            if sym_upper:
                return _SYMS[self.keycode]
            else:
                return self.keycode

        if self.keycode == Keycodes.Space:
            return " "

        return None

    def match(self, pattern: "Key"):
        return (
            pattern.keycode == self.keycode and
            pattern.control == self.control and
            pattern.shift == self.shift and
            pattern.alt == self.alt
        )



class Keycodes(object):
    Nothing = "NOTHING"  # Used to force a redraw
    Space = "SPACE"

    Escape = "ESC"
    Tab = "TAB"
    Enter = "ENTER"

    Backspace = "BACKSPACE"
    Delete = "DELETE"

    Up = "UP"
    Down = "DOWN"
    Left = "LEFT"
    Right = "RIGHT"

    ALL = list(_SYMS.keys()) + list(_LETTERS.keys()) + [
        Nothing, Space,
        Escape, Tab, Enter,
        Backspace, Delete,
        Up, Down, Left, Right,
    ]
