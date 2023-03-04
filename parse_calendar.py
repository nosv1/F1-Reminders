import icalendar
import datetime
import pymongo
import os

from dotenv import load_dotenv

load_dotenv()


def parse_calendar(ics_file: str) -> list[dict[str, str or datetime.datetime]]:
    cal = icalendar.Calendar.from_ical(open(ics_file, encoding="utf-8").read())
    events = []
    for component in cal.walk():
        if component.name == "VEVENT":
            event = {}
            event["summary"] = component.get("summary")
            event["location"] = component.get("location")
            event["description"] = component.get("description")
            event["start"] = component.get("dtstart").dt
            event["end"] = component.get("dtend").dt
            events.append(event)
    return events


if __name__ == "__main__":
    directory = os.path.dirname(os.path.abspath(__file__))
    calendar_path = os.path.join(directory, "F1 2023 Calendar.ics")

    client = pymongo.MongoClient(
        f"mongodb+srv://{os.getenv('MONGO_DB_USER')}:{os.getenv('MONGO_DB_PASSWORD')}@novo.4b3bqfk.mongodb.net/?retryWrites=true&w=majority"
    )
    db = client.F1_Calendar  # set the Database

    events = parse_calendar(calendar_path)

    for event in events:
        db.F1_2023_events.insert_one(event)  # set the collection
