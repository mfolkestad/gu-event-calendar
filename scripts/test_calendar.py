from gu_event_calendar.path import DOCS_DIR
from ics import Calendar, Event

calendar = Calendar()

event = Event(
    name="General Research Seminar in Political Science (AFS) with Alexandra Cirone",
    begin="2026-09-15 13:15:00+02:00",
    duration={"hours": 1, "minutes": 15},
    location="Lilla Skansen (B340)"
)

event = Event(
    name="Comparative Politics Seminar with Luis Sattelmayer",
    begin="2026-09-15 13:15:00+02:00",
    duration={"hours": 1, "minutes": 15},
    location="Lilla Skansen (B340)"
)

calendar.events.add(event)

with open(DOCS_DIR / "calendar.ics", "w") as file:
    file.writelines(calendar.serialize_iter())