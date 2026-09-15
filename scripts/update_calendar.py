import sys

import requests
from gu_event_calendar.event_parser import fetch_event, create_ical_event
from gu_event_calendar.path import DOCS_DIR
from ics import Calendar

calendar_event_urllist = [
    "https://www.gu.se/en/event/comparative-politics-seminar-with-luis-sattelmayer", "https://www.gu.se/en/event/reorienting-automation-reframing-ai-with-daniela-rosner-and-cristina-zaga", "https://www.gu.se/en/event/qog-lunch-seminar-with-elin-bjarnegard"

]


def main() -> int:
    calendar = Calendar()

    for url in calendar_event_urllist:
        try:
            event_data = fetch_event(url)
            calendar.events.add(create_ical_event(event_data))
        except (requests.RequestException, KeyError, TypeError, ValueError) as error:
            print(f"Could not add event from {url}: {error}", file=sys.stderr)

    if not calendar.events:
        print("No events were fetched; the calendar was not updated.", file=sys.stderr)
        return 1

    output_path = DOCS_DIR / "calendar2.ics"
    try:
        with output_path.open("w", encoding="utf-8") as file:
            file.writelines(calendar.serialize_iter())
    except (OSError, ValueError) as error:
        print(f"Could not write {output_path}: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
