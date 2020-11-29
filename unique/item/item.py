from typing import NamedTuple, Optional, runtime_checkable, Tuple, Union
from enum import Enum


class Resource(Enum):
    Money = 0
    Blood = 1
    Spark = 2

    Snack = 3
    Furniture = 4

    def display(self) -> Tuple[int, str]:
        if self == Resource.Money: return 5, "$"
        if self == Resource.Blood: return 1, "'"
        if self == Resource.Spark: return 10, "*"

        if self == Resource.Snack: return 5, "%"
        if self == Resource.Furniture: return 5, "\xe9"
        return 12, "?"


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
    bg: Optional[int]
    fg: Optional[int]

    @classmethod
    def new(cls, name: str, icon: str, bg: Optional[int] = None, fg: Optional[int] = None):
        assert isinstance(name, str)
        assert isinstance(icon, str) and len(icon) == 1
        assert bg is None or isinstance(bg, int)
        assert fg is None or isinstance(fg, int)
        return Profile(name, icon, bg, fg)


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
