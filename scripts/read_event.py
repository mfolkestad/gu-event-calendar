from gu_event_calendar.event_parser import fetch_event, create_ical_event
from gu_event_calendar.path import DOCS_DIR
from ics import Calendar

calendar = Calendar()

calendar_event_urllist = [
    "https://www.gu.se/en/event/comparative-politics-seminar-with-luis-sattelmayer", "https://www.gu.se/en/event/reorienting-automation-reframing-ai-with-daniela-rosner-and-cristina-zaga"

]
events = [fetch_event(url) for url in calendar_event_urllist]

for event in events:
    calendar.events.add(create_ical_event(event))

with open(DOCS_DIR / "calendar.ics", "w") as file:
    file.writelines(calendar.serialize_iter())

