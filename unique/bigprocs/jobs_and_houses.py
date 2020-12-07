import random
from ..social import EnterpriseHandle, HouseholdHandle
from ..npc import NPCHandle
from ..world import World
from typing import NamedTuple, Set
from ds.gale_shapley import GaleShapley
import itertools


class _Sets(NamedTuple):
    all_npcs: Set[NPCHandle]
    all_households: Set[HouseholdHandle]
    all_enterprises: Set[EnterpriseHandle]

    household_npcs: Set[NPCHandle]
    job_npcs: Set[NPCHandle]

    resented_npcs: Set[NPCHandle]

    no_household_npcs: Set[NPCHandle]
    no_job_npcs: Set[NPCHandle]


def _tabulate_sets(w: World) -> _Sets:
    all_npcs = set(w.npcs.all())
    all_households = set(w.households.all())
    all_enterprises = set(w.enterprises.all())

    household_npcs = set()
    for h in all_households:
        for m in w.households.members(h):
            household_npcs.add(m)

    job_npcs = set()
    for e in all_enterprises:
        for m in w.enterprises.get_employees(e):
            job_npcs.add(m)

    no_household_npcs = all_npcs - household_npcs
    no_job_npcs = all_npcs - job_npcs

    resented_npcs = set()
    for h in all_households:
        all_members = set(w.households.members(h))
        job_members = set(m for m in all_members if m in job_npcs)
        no_job_members = set(m for m in all_members if m in no_job_npcs)

        if len(job_members) >= 1 and len(no_job_members) == 1:
            for m in no_job_members:
                resented_npcs.add(m)

    return _Sets(
        all_npcs=all_npcs,
        all_households=all_households,
        all_enterprises=all_enterprises,

        household_npcs=household_npcs,
        job_npcs=job_npcs,

        resented_npcs=resented_npcs,

        no_household_npcs=no_household_npcs,
        no_job_npcs=no_job_npcs,
    )


def run(w: World):
    create_seed_households(w)

    for iteration in range(10):
        recruit_npcs_to_incomplete_households(w)
        recruit_npcs_to_jobs(w)
        evict_resented_npcs(w)
        # TODO: Drop shifts for NPCs that have too many shifts

    create_remaining_households(w)


def create_seed_households(w: World):
    sets = _tabulate_sets(w)

    no_household_npcs = shuffled(sets.no_household_npcs)
    incomplete_npcs = no_household_npcs[:len(no_household_npcs) // 3]  # limit number of seed households

    for n in incomplete_npcs:
        w.households.create(w, [n])


def create_remaining_households(w: World):
    sets = _tabulate_sets(w)

    for n in sets.no_household_npcs:
        w.households.create(w, [n])


def recruit_npcs_to_incomplete_households(w: World):
    sets = _tabulate_sets(w)

    # == Households that want to recruit NPCs ==
    incomplete_households = set()
    incomplete_npcs = set(sets.no_household_npcs)
    for h in sets.all_households:
        members = set(w.households.members(h))
        if len(members) == 1 and False:  # TODO: and "is homeless"
            for m in members:
                incomplete_npcs.add(m)
        elif len(members) == 1 and any(m in sets.no_job_npcs for m in members):
            incomplete_households.add(h)

        # TODO: There may be other cases where a plus one is needed


    # == Gale-Shapley between households and unpicked NPCs ==
    def ranked_friends(npc):
        return shuffled(w.friendships.friends(npc))

    # TODO: Homeless NPCs should be recruitable to a household, even if they are already in one
    household_npc_preference = {}
    for h in incomplete_households:
        members = shuffled(w.households.members(h))
        invitable_people = []
        for m in members:
            for f in ranked_friends(m):
                if f in invitable_people: continue
                invitable_people.append(f)
        invitable_people.reverse()
        household_npc_preference[h] = {npc: i for i, npc in enumerate(invitable_people)}

    gale_shapley = GaleShapley(
        lambda household, npc: household_npc_preference[household].get(npc), # will be 0, otherwise a higher index for more desirable npcs
        lambda npc, household:  # NPCs like households with more friends
            # TODO: Scale down by n members in household?
            sum(1 for member in w.households.members(household) if w.friendships.npc_likes(npc, member))
    )

    match_households = shuffled(incomplete_households)
    match_npcs = shuffled(incomplete_npcs)
    matches = gale_shapley.match(match_households, match_npcs)
    for ix_household, ix_npc in matches:
        w.households.add_member(match_households[ix_household], match_npcs[ix_npc])


def recruit_npcs_to_jobs(w: World):
    # TODO: Identify NPCs who need a job
    #  (ex. are homeless, are living above their means, are resented by their household for being idle)
    sets = _tabulate_sets(w)

    incomplete_shifts = set(shift for shift in w.enterprises.all_shifts() if w.enterprises.get_employee(shift) is None)
    incomplete_npcs = set()
    for npc in sets.all_npcs:
        # TODO: "Homeless," "above their means," "_wants_ a job" as reasons to seek work
        if npc in sets.resented_npcs:
            incomplete_npcs.add(npc)
        if True:  # TODO: No one wants to be idle for now
            incomplete_npcs.add(npc)

    gale_shapley = GaleShapley(
        lambda shift, npc: 1,  # TODO: Give enterprises a reason to prefer one NPC over another
        lambda npc, shift:  # NPCs like households with more friends
            # TODO: Scale down by n members in household?
            sum(1 for member in w.enterprises.get_employees(shift.enterprise) if w.friendships.npc_likes(npc, member))
    )

    match_shifts = shuffled(incomplete_shifts)
    match_npcs = shuffled(incomplete_npcs)
    matches = gale_shapley.match(match_shifts, match_npcs)

    for ix_shift, ix_npc in matches:
        w.enterprises.employ(match_shifts[ix_shift], match_npcs[ix_npc])


def evict_resented_npcs(w: World):
    sets = _tabulate_sets(w)

    for n in sets.resented_npcs:
        w.households.evict(n)


def shuffled(xs):
    lxs = list(xs)
    random.shuffle(lxs)
    return lxs
