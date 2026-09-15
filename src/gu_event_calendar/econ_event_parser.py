import re
import requests
from bs4 import BeautifulSoup, NavigableString, Tag


MONTHS = {
    "january": "Jan",
    "february": "Feb",
    "march": "Mar",
    "april": "Apr",
    "may": "May",
    "june": "Jun",
    "july": "Jul",
    "august": "Aug",
    "september": "Sep",
    "october": "Oct",
    "november": "Nov",
    "december": "Dec",
}

WEEKDAYS = (
    r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)"
)

MONTH_PATTERN = "|".join(MONTHS)

STANDARD_EVENT = re.compile(
    rf"""
    ^
    (?P<event_type>.+?)
    :\s*
    (?:{WEEKDAYS},\s*)?
    (?P<month>{MONTH_PATTERN})
    \s+
    (?P<day>\d{{1,2}})
    (?:
        \s+at\s+
        (?P<start>\d{{1,2}}:\d{{2}})
        (?:
            \s*[-–]\s*
            (?P<end>\d{{1,2}}:\d{{2}})
        )?
        (?:
            \s+(?:in\s+|,\s*)
            (?P<location>.+?)
        )?
    )?
    \.?
    $
    """,
    re.IGNORECASE | re.VERBOSE,
)

DATE_RANGE_EVENT = re.compile(
    rf"""
    ^
    (?P<event_type>.+?)
    ,\s*
    (?P<month>{MONTH_PATTERN})
    \s+
    (?P<start_day>\d{{1,2}})
    \s*[-–]\s*
    (?P<end_day>\d{{1,2}})
    \.?
    $
    """,
    re.IGNORECASE | re.VERBOSE,
)

def parse_events_from_url(
    url: str,
    year: int,
) -> list[dict[str, str]]:
    response = requests.get(
        url,
        headers={
            "User-Agent": "gu-event-calendar/1.0",
            "Accept": "text/html",
        },
        timeout=30,
    )

    response.raise_for_status()

    return parse_events(
        html=response.text,
        year=year,
    )


def clean_text(value: str) -> str:
    """Normalize whitespace, non-breaking spaces, and punctuation spacing."""
    value = value.replace("\xa0", " ")
    value = " ".join(value.split())
    value = re.sub(r"\s+([.,;:])", r"\1", value)
    return value.strip()


def split_paragraph(paragraph: Tag) -> tuple[str, str]:
    """Split a paragraph into the text before and after its first <br>."""
    before = []
    after = []
    found_break = False

    for node in paragraph.descendants:
        if isinstance(node, Tag) and node.name == "br":
            found_break = True
        elif isinstance(node, NavigableString):
            target = after if found_break else before
            target.append(str(node))

    return clean_text("".join(before)), clean_text("".join(after))


def format_date(day: int, month: str, year: int) -> str:
    month_abbreviation = MONTHS[month.lower()]
    return f"{day} {month_abbreviation} {year}"


def parse_events(html: str, year: int) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    container = soup.select_one("div.formatted-content")

    if container is None:
        raise ValueError("Could not find div.formatted-content")

    events = []

    for paragraph in container.find_all("p", recursive=False):
        heading, description = split_paragraph(paragraph)

        if not heading:
            continue

        match = STANDARD_EVENT.fullmatch(heading)

        if match:
            values = match.groupdict()

            event = {
                "title": clean_text(values["event_type"]),
                "description": description,
                "event_type": clean_text(values["event_type"]),
                "date": format_date(
                    int(values["day"]),
                    values["month"],
                    year,
                ),
            }

            if values["start"]:
                if values["end"]:
                    event["time"] = (
                        f"{values['start']} - {values['end']}"
                    )
                else:
                    event["time"] = values["start"]

            if values["location"]:
                event["location"] = (
                    clean_text(values["location"]).rstrip(".")
                )

            events.append(event)
            continue

        # Handle entries such as:
        # "CHG Workshop on Economics, Inequality, and Health,
        #  October 22–23."
        match = DATE_RANGE_EVENT.fullmatch(heading)

        if match:
            values = match.groupdict()

            events.append({
                "title": clean_text(values["event_type"]),
                "description": description,
                "event_type": clean_text(values["event_type"]),
                "date": format_date(
                    int(values["start_day"]),
                    values["month"],
                    year,
                ),
                "end_date": format_date(
                    int(values["end_day"]),
                    values["month"],
                    year,
                ),
            })
            continue

        # Retain unrecognized entries instead of silently losing them.
        events.append({
            "title": heading,
            "description": description,
            "parse_error": "Unrecognized event heading",
        })

    return events