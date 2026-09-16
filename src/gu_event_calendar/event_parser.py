import requests
from bs4 import BeautifulSoup

import re
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from ics import Event

STOCKHOLM = ZoneInfo("Europe/Stockholm")


def fetch_event(event_url: str) -> dict[str, str]:
    response = requests.get(event_url, timeout=30)
    response.raise_for_status()

    return parse_event(response.text)

def parse_event(html: str) -> dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")

    event = {}

    # Main fields
    title = soup.select_one("h1.heading-main")
    description = soup.select_one("p.preamble")
    event_type = soup.select_one(".label--framed")
    
    if title:
        event["title"] = title.get_text(" ", strip=True)

    if description:
        event["description"] = description.get_text(" ", strip=True)

    if event_type:
        event["event_type"] = event_type.get_text(" ", strip=True)

    # Fields consisting of a label followed by data
    for meta in soup.select("div.meta"):
        label = meta.select_one(".label")
        value = meta.select_one(".meta__data")

        if label and value:
            key = label.get_text(" ", strip=True).lower()
            event[key] = value.get_text(" ", strip=True)
    event["url"] = soup.select_one("link[rel='canonical']")["href"]
    return event



def clean_url(value: str) -> str:
    """Convert a Markdown URL such as [https://...](https://...) to a plain URL."""
    if value is None:
        return ""
    match = re.fullmatch(r"\[.*?]\((https?://.*?)\)", value.strip())
    return match.group(1) if match else value.strip()
    

def create_ical_event(data: dict[str, str]) -> Event:
    date = datetime.strptime(data["date"], "%d %b %Y").date()

    start_text, end_text = (
        value.strip()
        for value in data["time"].split("-", maxsplit=1)
    )

    start_time = datetime.strptime(start_text, "%H:%M").time()
    end_time = datetime.strptime(end_text, "%H:%M").time()

    start = datetime.combine(date, start_time, tzinfo=STOCKHOLM)
    end = datetime.combine(date, end_time, tzinfo=STOCKHOLM)

    url = clean_url(data.get("url"))

    event = Event()
    event.name = data["title"]
    event.description = data.get("description", "")
    event.location = data.get("location", "")
    event.begin = start
    event.end = end
    event.url = url

    if event_type := data.get("event_type"):
        event.categories = {event_type}

    # Create a stable identifier from the source URL. Regenerating the
    # calendar will therefore update this event instead of duplicating it.
    if url:
        event.uid = f"{uuid.uuid5(uuid.NAMESPACE_URL, url)}@gu-event-calendar"
    else:
        event.uid= f"{uuid.uuid4()}@gu-event-calendar"
        
    if last_modified := data.get("last modified"):
        event.last_modified = datetime.strptime(
            last_modified,
            "%d %B %Y",
        ).replace(tzinfo=STOCKHOLM)

    return event