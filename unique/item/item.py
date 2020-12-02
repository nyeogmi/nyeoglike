from display import Color, Colors
from typing import NamedTuple, Optional, runtime_checkable, Tuple, Union
from enum import Enum


class Resource(Enum):
    Money = 0
    Blood = 1
    Spark = 2

    Snack = 3
    Furniture = 4

    def display(self) -> Tuple[Color, str]:
        if self == Resource.Money: return Colors.ResourceGeneric, "$"
        if self == Resource.Blood: return Colors.BloodRed, "'"
        if self == Resource.Spark: return Colors.BrightGreen, "*"

        if self == Resource.Snack: return Colors.ResourceGeneric, "%"
        if self == Resource.Furniture: return Colors.ResourceGeneric, "\xe9"
        return Colors.DarkGray, "?"


class Resources(object):
    ESSENTIAL = (Resource.Money, Resource.Blood, Resource.Spark)


class Contribution(NamedTuple):
    resource: Resource
    n: int

    @classmethod
    def new(cls, resource: Resource, n: int) -> "Contribution":
        assert isinstance(resource, Resource)
        assert isinstance(n, int) and n > 0
        return Contribution(resource, n)


class Profile(NamedTuple):
    name: str
    icon: str  # a string or a double-wide
    ascii_icon: str
    bg: Optional[Color]
    fg: Optional[Color]

    @classmethod
    def new(cls, name: str, icon: str, ascii_icon: str, bg: Optional[int] = None, fg: Optional[int] = None):
        assert isinstance(name, str)
        assert isinstance(icon, str) and len(icon) == 1
        assert isinstance(ascii_icon, str) and len(ascii_icon) == 1
        assert bg is None or isinstance(bg, Color)
        assert fg is None or isinstance(fg, Color)
        return Profile(name, icon, ascii_icon, bg, fg)


class Item(NamedTuple):
    profile: Profile
    contributions: Tuple[Contribution, ...]

    @classmethod
    def new(cls, profile: Profile, res0: Resource, n0: int, res1: Optional[Resource] = None, n1: Optional[int] = None):
        assert isinstance(profile, Profile)
        tup = (Contribution.new(res0, n0),)
        if res1 is not None:
            tup += (Contribution.new(res1, n1))

        return Item(profile, tup)
