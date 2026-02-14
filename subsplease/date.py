from datetime import datetime


def get_day(weekday: str) -> str | None:
    weekday = weekday.strip().lower()
    if not weekday:
        return None

    days = ["monday", "tuesday", "wednesday", "thursday",
            "friday", "saturday", "sunday"]
    abbrs = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

    if weekday[0] in ("+", "-"):
        try:
            offset = int(weekday)
            current_idx = datetime.now().weekday()
            return days[(current_idx + offset) % 7]
        except ValueError:
            return None
    if weekday.isdigit():
        day = int(weekday)-1
        return days[day % 7]
    if weekday in abbrs:
        return days[abbrs.index(weekday)]
    if weekday in days:
        return weekday
