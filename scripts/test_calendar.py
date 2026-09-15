from calendar_tools.path import DATA_DIR, OUTPUT_DIR
from ics import Calendar, Event

calendar = Calendar()

event = Event(
    name="Comparative Politics Seminar with Luis Sattelmayer",
    begin="2026-09-15 13:15:00+02:00",
    duration={"hours": 1, "minutes": 15},
    location="Lilla Skansen (B340)"
)

calendar.events.add(event)

with open(OUTPUT_DIR / "calendar.ics", "w") as file:
    file.writelines(calendar.serialize_iter())