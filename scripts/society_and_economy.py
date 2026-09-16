import sys
import requests
from gu_event_calendar.event_parser import fetch_event, create_ical_event
from gu_event_calendar.path import DOCS_DIR
from ics import Calendar
from gu_event_calendar.get_events import get_event_urls


get_event_urls("2026-09-01",event_area = "Society and economy", hits = 200,  event_type = "Seminar",)  

def main() -> int:
    calendar = Calendar()
    calendar_event_urllist = get_event_urls("2026-09-01",event_area = "society and economy", hits = 200)  # Fetch events starting from this date

    for url in calendar_event_urllist:
        try:
            event_data = fetch_event(url)
            calendar.events.add(create_ical_event(event_data))
        except (requests.RequestException, KeyError, TypeError, ValueError) as error:
            print(f"Could not add event from {url}: {error}", file=sys.stderr)

    if not calendar.events:
        print("No events were fetched; the calendar was not updated.", file=sys.stderr)
        return 1

    output_path = DOCS_DIR / "society_and_economy.ics"
    try:
        with output_path.open("w", encoding="utf-8") as file:
            file.writelines(calendar.serialize_iter())
    except (OSError, ValueError) as error:
        print(f"Could not write {output_path}: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
