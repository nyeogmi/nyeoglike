from enum import Enum


class TimeOfDay(Enum):
    Evening = 0
    Dusk = 1
    Midnight = 2
    Dawn = 3
    Morning = 4
    Afternoon = 5

    def display(self) -> str:
        return self.name

    def next(self):
        if self == TimeOfDay.Evening:
            return TimeOfDay.Dusk
        if self == TimeOfDay.Dusk:
            return TimeOfDay.Midnight
        if self == TimeOfDay.Midnight:
            return TimeOfDay.Dawn
        if self == TimeOfDay.Dawn:
            return TimeOfDay.Morning
        if self == TimeOfDay.Morning:
            return TimeOfDay.Afternoon
        if self == TimeOfDay.Afternoon:
            return TimeOfDay.Evening
