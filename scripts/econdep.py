import sys
import requests

from gu_event_calendar.econ_event_parser import parse_events_from_url
from gu_event_calendar.event_parser import create_ical_event
from gu_event_calendar.path import ECON_EVENTS_URL, DOCS_DIR
from ics import Calendar


def main() -> int:
    calendar = Calendar()

    try:
        events = parse_events_from_url(ECON_EVENTS_URL, year=2026)
    except requests.RequestException as error:
        print(
            f"Could not fetch events from {ECON_EVENTS_URL}: {error}",
            file=sys.stderr,
        )
        return 1
    except (TypeError, ValueError) as error:
        print(
            f"Could not parse events from {ECON_EVENTS_URL}: {error}",
            file=sys.stderr,
        )
        return 1

    for event in events:
        event_name = (
            event.get("title", "<untitled event>")
            if isinstance(event, dict)
            else "<invalid event>"
        )
        try:
            calendar.events.add(create_ical_event(event))
        except (requests.RequestException, KeyError, TypeError, ValueError) as error:
            print(
                f"Could not add event {event_name!r}: {error}",
                file=sys.stderr,
            )

    if not calendar.events:
        print("No events were fetched; the calendar was not updated.", file=sys.stderr)
        return 1

    output_path = DOCS_DIR / "econdep.ics"
    try:
        with output_path.open("w", encoding="utf-8") as file:
            file.writelines(calendar.serialize_iter())
    except (OSError, TypeError, ValueError) as error:
        print(f"Could not write {output_path}: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
