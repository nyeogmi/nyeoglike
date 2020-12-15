from ..world import World
from .dump import Dump, ObjDump


def dump_world(w: World):
    dump = Dump()

    def if_(c, x):
        return [x] if c else []

    obj = dump.obj("Schedule")
    for npch in sorted(w.npcs.all(), key=lambda n: w.npcs.get(n).name):
        schedule_s = "{} -> {}".format(
            w.schedules.next_schedule(npch).name,
            w.schedules.next_location(w, npch),
        )
        obj.add(w.npcs.get(npch).name, schedule_s)

    for npch in sorted(w.npcs.all(), key=lambda n: w.npcs.get(n).name):
        npc = w.npcs.get(npch)

        obj = dump.obj(npc.name)

        schedule_s = "{} -> {}".format(
            w.schedules.next_schedule(npch).name,
            w.schedules.next_location(w, npch),
        )
        obj.add("plan", schedule_s)

        obj.add(
            "flags",
            ", ".join(
                [
                    *if_(npc.asleep, "asleep"),
                    *if_(npc.seen, "seen"),
                    *(
                        ["very sleepy"]
                        if w.rhythms.is_very_sleepy(npch)
                        else ["sleepy"]
                        if w.rhythms.is_sleepy(npch)
                        else ["can sleep"]
                        if w.rhythms.can_sleep(npch)
                        else []
                    ),
                    *(
                        ["very hungry"]
                        if w.rhythms.is_very_hungry(npch)
                        else ["hungry"]
                        if w.rhythms.is_hungry(npch)
                        else ["can eat"]
                        if w.rhythms.can_eat(npch)
                        else []
                    ),
                ]
            ),
        )

        with obj.prefix("household"):
            household = w.households.household_of(npch)
            for i, fellow in enumerate(
                sorted(
                    w.households.members(household), key=lambda n: w.npcs.get(n).name
                )
            ):
                obj.add(i, w.npcs.get(fellow).name)

        with obj.prefix("shifts"):
            for i, shift in enumerate(w.enterprises.get_shifts_worked_by(npch)):
                shift_s = "{} ({})".format(
                    w.enterprises.get_name(shift.enterprise),
                    w.enterprises.get_shift(shift),
                )
                obj.add(i, shift_s)

    for household in w.households.all():
        obj = dump.obj(household)
        for i, fellow in enumerate(
            sorted(w.households.members(household), key=lambda n: w.npcs.get(n).name)
        ):
            obj.add(i, w.npcs.get(fellow).name)

    for enterprise in sorted(
        w.enterprises.all(), key=lambda e: w.enterprises.get_name(e)
    ):
        obj = dump.obj(w.enterprises.get_name(enterprise))
        for i, shift in enumerate(w.enterprises.all_shifts_of(enterprise)):
            worker = w.enterprises.get_employee(shift)
            worker_s = "?" if worker is None else w.npcs.get(worker).name
            shift_s = "({}) -> {}".format(w.enterprises.get_shift(shift), worker_s)
            obj.add(i, shift_s)

    return dump.render()
