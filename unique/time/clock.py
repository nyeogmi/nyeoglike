from .time_of_day import TimeOfDay


class Clock(object):
    def __init__(self):
        self._started = False
        self._tick = 0
        self._time_of_day = TimeOfDay.Evening
        self._night = 0

    @property
    def started(self): return self._started

    @property
    def tick(self): return self._tick

    @property
    def time_of_day(self): return self._time_of_day

    @property
    def night(self): return self._night

    def start(self):
        self._started = True

    def advance_tick(self):
        self._tick += 1

    def advance_time(self):
        self._started = False
        self._time_of_day = self._time_of_day.next()
        if self._time_of_day == TimeOfDay.Morning:
            # TODO: Don't advance immediately, so we can do a report
            self.advance_night()

    def advance_night(self):
        self._night += 1
        self._time_of_day = TimeOfDay.Evening
