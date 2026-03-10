from datetime import datetime, time, timedelta
from core.config import config

class SheduleManager:
    day = datetime.combine(datetime.today(), time(0, 0))
    start_counting = datetime.fromisoformat(config.parse.count_from) # обязательно понедельник - числитель!

    def __init__(self, shedule: dict[str, dict[str, str]]):
        self.shedule = shedule

    def _is_numerator(self):
        return (self.day - self.start_counting).days % 14 > 6

    def get_shedule(self, date: datetime = None, add_week_type: bool = True) -> str:
        day = date if date else self.day
        week_day = date.weekday() if date else self.day.weekday()
        week_day = config.parse.numbers_to_days.get(week_day)
        week_type = "Числитель" if self._is_numerator() else "Знаменатель"

        output = f"📆 {day.strftime("%d.%m.%Y")}\n"
        output += f"⏳ {week_day} | {week_type}\n" if add_week_type else f"⏳ {week_day}\n"

        output += self.shedule[week_type][week_day]
        return output
    
    def get_week_shedule(self, date: datetime = None) -> str:
        week_type = "Числитель" if self._is_numerator() else "Знаменатель"
        monday = date - timedelta(
            date.weekday()
        ) if date else self.day - timedelta(
            self.day.weekday()
        )
        
        output = f"Расписание на {monday.strftime("%d.%m.%Y")} - {(monday + timedelta(6)).strftime("%d.%m.%Y")} | {week_type}\n\n"
        for day in range(6):
            output += self.get_shedule(monday + timedelta(day), False) + "\n\n"

        return output
    