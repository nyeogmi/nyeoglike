class Challenges(object):
    def __init__(self):
        self._clean_junk_challenge = None

    def scan(self, world: "World"):
        from unique.quests.clean_junk import CleanJunkQuest

        # for now, in case it's missed, just because it's the only way to None the existing ones
        self.descan(world)

        junk_left = world.level.items.junk_left
        print("adding clean junk challenge? {}".format(junk_left))
        if junk_left > 0:
            assert self._clean_junk_challenge is None
            self._clean_junk_challenge = world.eventmonitors.add(
                world, lambda handle: CleanJunkQuest(handle, junk_left)
            )

    def descan(self, world: "World"):
        if self._clean_junk_challenge:
            # TODO: Is this an abstraction violation? See if it breaks anything.
            world.eventmonitors.finalize_quest(self._clean_junk_challenge)
            self._clean_junk_challenge = None


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .world import World
