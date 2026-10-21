#!/usr/bin/env python3

from collections import defaultdict
import csv
import sys
from datetime import date, datetime
from zoneinfo import ZoneInfo
from icalendar import Calendar


def parse_and_sort_ics(file_path):
    berlin_tz = ZoneInfo("Europe/Berlin")

    with open(file_path, "rb") as f:
        cal = Calendar.from_ical(f.read())

    raw_events = []
    for component in cal.walk():
        if component.name == "VEVENT":
            name = str(component.get("summary", "No Title"))
            dtstart = component.get("dtstart")

            if not dtstart:
                continue

            dt = dtstart.dt

            if isinstance(dt, datetime):
                if dt.tzinfo is None:
                    dt_berlin = dt.replace(tzinfo=berlin_tz)
                else:
                    dt_berlin = dt.astimezone(berlin_tz)

                sort_key = dt_berlin
                date_str = dt_berlin.strftime("%Y-%m-%d")
                time_str = dt_berlin.strftime("%H:%M:%S")
            elif isinstance(dt, date):
                sort_key = datetime.combine(dt, datetime.min.time(), tzinfo=berlin_tz)
                date_str = dt.strftime("%Y-%m-%d")
                time_str = "All Day"

            raw_events.append(
                (
                    sort_key,
                    {
                        "name": name,
                        "date": date_str,
                        "starttime": time_str,
                    },
                )
            )

    raw_events.sort(key=lambda x: x[0])
    return [event[1] for event in raw_events]


def filter_events_2026(events):
    return [
        event for event in events if "2026-01-01" <= event.get("date", "") <= "2026-12-31"
    ]


def classify_event(eventname: str) -> str:
    weekday = datetime.strptime(ev["date"], "%Y-%m-%d").strftime("%A")
    if 'abholen' in eventname.lower() or 'crashkurs' in eventname.lower() or 'crash-kurs' in eventname.lower() or 'belegt' in eventname.lower() or 'bibliothek geschlossen' in eventname.lower() or ('tutorial' in eventname and weekday == 'Wednesday'):
        return 'not a workshop'
    elif 'ber-it' in eventname.lower():
        return 'BER-IT'
    elif 'remili' in eventname.lower():
        return 'ReMili'
    elif 'Freies Coden' in eventname:
        return 'Freies Coden'
    elif 'makerspace' in eventname.lower() or weekday == 'Friday':
        return 'Makerspace'
    elif 'gertrud' in eventname.lower():
        return 'Gertrud-Junge'
    elif 'fest für demokratie' in eventname.lower():
        return 'extra'
    elif weekday == 'Saturday':
        return 'Workshop'
    else:
        return 'unclassified'


def format_ev(ev, min_name_len: int = 0):
    weekday = datetime.strptime(ev["date"], "%Y-%m-%d").strftime("%A").ljust(10)
    name = ev["name"].ljust(min_name_len)
    return f'{name}\t{ev["date"]}\t{weekday}\t{ev["starttime"]}'


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_ics_file>")
        sys.exit(1)

    ics_path = sys.argv[1]
    parsed_events = parse_and_sort_ics(ics_path)
    parsed_events = filter_events_2026(parsed_events)

    classes = defaultdict(list)
    for ev in parsed_events:
        c = classify_event(ev['name'])
        classes[c].append(ev)

    num_chars = max(len(ev['name']) for ev in parsed_events)

    for c, evs in classes.items():
        print(f'{c} [{len(evs)}]')
        for ev in evs:
            print('    ', format_ev(ev, num_chars))

    
