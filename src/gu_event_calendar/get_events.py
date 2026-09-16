import requests
import json
from gu_event_calendar.path import EVENT_API


def fetch_event_list(date_from: str, event_type = "Seminar", event_area = "Society and economy", hits = 200) -> str:
    """Return the URL of the GU event list page."""
    params = {
        "date_from": date_from,
        "event_area_facet": event_area,
        "event_type_facet": event_type,
        "hits": hits,
        "q": "*",
        "sort": "date_asc",
    }

    response = requests.get(
        EVENT_API,
        params=params,
        headers={
            "Accept": "application/json",
            "User-Agent": "gu-event-calendar/1.0",
        },
        timeout=30,
    )
    response.raise_for_status()
    print(response.url)
    return json.loads(response.text)

def get_event_urls(date_from: str, **kwargs) -> list:
    """Return event URLs from the GU event list.

    Args:
        date_from: Earliest event date to include.

    Keyword Args:
        event_type: Event type to request. Defaults to ``"Seminar"``.
        event_area: Event area to request. Defaults to
            ``"Society and economy"``.
        hits: Maximum number of events to request. Defaults to ``200``.

    Returns:
        A list of absolute URLs for the matching events.
    """
    event_list = fetch_event_list(date_from, **kwargs)
    return [f"https://www.gu.se{event['url']}" for event in event_list["documentList"]["documents"]]    
