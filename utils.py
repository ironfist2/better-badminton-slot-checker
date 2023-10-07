import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urlparse
import logging
import pandas as pd

log = logging.getLogger(__name__)
DATE_FORMAT = '%Y-%m-%d'


def get_dates_from_today():
    # Get today's date
    today = datetime.today()

    # Generate dates for the next 7 days
    for i in range(8):
        date = today + timedelta(days=i)
        formatted_date = date.strftime(DATE_FORMAT)
        yield formatted_date


def get_locations(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    divs = soup.find_all('div', class_='result-card')
    for div in divs:
        link = div.find('a')
        link = link.get("href")
        parsed_link = urlparse(link)
        location_name = parsed_link.path.strip().split('/')[-1]
        yield location_name


def get_availabilities(location_name):
    for date in get_dates_from_today():
        for dur in [60, 40]:
            try:
                log.debug(f"Fetching availabilities for {location_name} on {date} for duration {dur} mins")
                url = f'https://better-admin.org.uk/api/activities/venue/{location_name}/activity/badminton-{dur}min/times?date={date}'
                response = requests.request("GET", url, headers={'Origin': 'https://bookings.better.org.uk'})
                data = json.loads(response.text)
                if (not "data" in data or len(data["data"]) == 0):
                    log.debug(f"No spaces left at {location_name} on {date}")
                    continue
                
                yield (date, data["data"])

            except Exception as exc:
                continue


def process_availability(location_name, availability):
    date, times = availability
    data = []
    myDate = datetime.strptime(date, DATE_FORMAT)
    weekno = myDate.weekday()

    for time in times:
        try:
            # log.info([weekno, time["starts_at"]["format_24_hour"], time["ends_at"]["format_24_hour"]])
            if weekno < 5 and time["starts_at"]["format_24_hour"] >= "18:00" and time["spaces"] > 0:
                data.append([location_name, date, time["starts_at"]["format_24_hour"], time["ends_at"]["format_24_hour"]])
            elif weekno >= 5 and time["starts_at"]["format_24_hour"] >= "10:00" and time["spaces"] > 0:
                data.append([location_name, date, time["starts_at"]["format_24_hour"], time["ends_at"]["format_24_hour"]])
        except Exception as e:
            continue
    return data

def pretty_print(slots):
    headers = ["Location", "Date", "Start Time", "End Time"]
    df = pd.DataFrame(data=slots, columns=headers)
    print(df)