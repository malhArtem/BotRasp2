from datetime import datetime, time, timedelta
from core.config import config

class SheduleManager:
    day = datetime.combine(datetime.today(), time(0, 0))
    start_counting = datetime.fromisoformat(config.count_from) # обязательно понедельник - числитель!

    def __init__(self, shedule: dict[str, dict[str, str]]):
        self.shedule = shedule

    def _is_numerator(self):
        return (self.day - self.start_counting).days % 14 > 6
    
    def _increment_day(self):
        if self.day.weekday != 5:
            self.day += timedelta(1)
        else:
            self.day += timedelta(2)

    def _decrement_day(self):
        if self.day.weekday:
            self.day -= timedelta(1)
        else:
            self.day -= timedelta(2)

    def get_shedule(self, date: datetime = None):
        week_day = date.weekday() if date else self.day.weekday()
        week_day = config.numbers_to_days.get(week_day)
        week_type = "Числитель" if self._is_numerator() else "Знаменатель"

        output = f"📆 {self.day.strftime("%d.%m.%Y")}\n"
        output += f"⏳ {week_day} | {week_type}\n"

        output += self.shedule[week_type][week_day]
        return output
    
    def next_shedule(self):
        self._increment_day()
        return self.get_shedule()
    
    def prev_shedule(self):
        self._decrement_day()
        return self.get_shedule()
    