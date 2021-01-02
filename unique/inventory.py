from typing import Dict, NamedTuple

from ds.gensym import Gensym, Sym
from ds.relational import OneToMany

from .event import Event, Verbs
from .eventmonitor import EMHandle
from .item import Item, Resource


class Inventory(object):
    def __init__(self):
        self.resources: Dict[Resource, int] = {}
        self.claims = Claims()

    def add(self, world: "World", item: Item):
        from .world import World

        assert isinstance(world, World)
        assert isinstance(item, Item)

        claim_box = ClaimBox(self.claims, item, hypothetical=False)
        world.notify(Event.new(Verbs.Claim, (claim_box,)))

        if not claim_box.taken:
            self.liquidate(item)

    def liquidate(self, item: Item):
        for c in item.contributions:
            self.resources[c.resource] = self.resources.get(c.resource, 0)
            self.resources[c.resource] += c.n

        if self.resources.get(Resource.Blood, 0) > 100:
            self.resources[Resource.Blood] = 100

        if self.resources.get(Resource.Spark, 0) > 100:
            self.resources[Resource.Spark] = 100

    def get(self, resource: Resource) -> int:
        return self.resources.get(resource, 0)

    def take(self, resource: Resource, n: int) -> bool:
        assert isinstance(n, int)
        if n == 0:
            return True

        if n > self.resources.get(resource, 0):
            return False

        self.resources[resource] -= n
        if self.resources[resource] == 0:
            del self.resources[resource]


class ClaimHandle(NamedTuple):
    ident: Sym


class Claims(object):
    def __init__(self):
        self._sym = Gensym("CLM")

        self._quest_claims: OneToMany[EMHandle, ClaimHandle] = OneToMany()
        self._claimed_items: Dict[ClaimHandle, Item] = {}

    def claim(self, quest: EMHandle, item: Item) -> ClaimHandle:
        ident = self._sym.gen()
        handle: ClaimHandle = ClaimHandle(ident)

        self._quest_claims.add(quest, handle)
        self._claimed_items[handle] = item

        return handle

    def redeem(self, handle: ClaimHandle) -> Item:
        assert handle in self._claimed_items


class ClaimBox(object):
    def __init__(self, claims, item, hypothetical):
        assert isinstance(claims, Claims)
        assert isinstance(item, Item)
        assert isinstance(hypothetical, bool)

        self._claims = claims
        self._item = item
        self._taken: bool = False
        self._hypothetical = hypothetical

    @property
    def taken(self) -> bool:
        return self._taken

    @property
    def item(self) -> Item:
        return self._item

    def claim(self, quest: EMHandle) -> ClaimHandle:
        if self._hypothetical:
            raise HypotheticalClaimException(quest)

        handle = self._claims.claim(quest, self._item)
        self._taken = True
        return handle


class HypotheticalClaimException(Exception):
    def __init__(self, quest):
        Exception.__init__(self)
        self.claimant = quest


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .world import World
