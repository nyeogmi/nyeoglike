from enum import Enum
from typing import NamedTuple, Optional, Tuple, Union, runtime_checkable, Iterable

from display import Color, Colors


class Resource(Enum):
    Money = 0
    Blood = 1
    Spark = 2

    Snack = 3
    Furniture = 4

    def display(self) -> Tuple[Color, str]:
        if self == Resource.Money:
            return Colors.ResourceGeneric, "$"
        if self == Resource.Blood:
            return Colors.Red1, "'"
        if self == Resource.Spark:
            return Colors.YellowGreen1, "*"

        if self == Resource.Snack:
            return Colors.ResourceGeneric, "%"
        if self == Resource.Furniture:
            return Colors.ResourceGeneric, "\xe9"
        return Colors.Grey0, "?"


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
    double_icon: Optional[Union[str, int]]
    bg: Optional[Color]
    fg: Optional[Color]

    @classmethod
    def new(
        cls,
        name: str,
        icon: str,
        bg: Optional[int] = None,
        fg: Optional[int] = None,
    ):
        assert isinstance(name, str)
        assert isinstance(icon, str) and len(icon) == 1

        assert bg is None or isinstance(bg, Color)
        assert fg is None or isinstance(fg, Color)
        return Profile(name, icon, None, bg, fg)

    def with_double_icon(self, s) -> "Profile":
        assert isinstance(s, str) or isinstance(s, int)
        if isinstance(s, str):
            assert len(s) == 2

        return self._replace(double_icon=s)


class Item(NamedTuple):
    profile: Profile
    buy_price: int
    keywords: Tuple[str, ...]
    contributions: Tuple[Contribution, ...]

    @classmethod
    def new(
        cls,
        profile: Profile,
        buy_price: int,
        keywords: Tuple[str, ...] = (),
        res0: Resource = None,
        n0: int = None,
        res1: Optional[Resource] = None,
        n1: Optional[int] = None,
    ):
        assert isinstance(profile, Profile)
        assert isinstance(buy_price, int)
        assert isinstance(keywords, tuple)
        assert all(isinstance(i, str) for i in keywords)
        assert isinstance(res0, Resource)
        assert isinstance(n0, int)

        tup = (Contribution.new(res0, n0),)
        if res1 is not None:
            tup += Contribution.new(res1, n1)

        return Item(profile, buy_price, tuple(sorted({*keywords})), tup)

    def plus_keywords(self, keywords: Iterable[str]) -> "Item":
        i2 = Item(
            profile=self.profile,
            buy_price=self.buy_price,
            keywords=tuple(sorted({*self.keywords, *keywords})),
            contributions=self.contributions,
        )
        assert all(isinstance(kw, str) for kw in i2.keywords)
        return i2
