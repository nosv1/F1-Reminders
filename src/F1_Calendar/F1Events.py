import datetime
from dataclasses import dataclass
import discord
from pymongo import collection


@dataclass
class EventKeys:
    summary: str = "summary"
    location: str = "location"
    description: str = "description"
    start: str = "start"
    end: str = "end"


@dataclass
class SessionNames:
    practice_1: str = "Practice 1"
    practice_2: str = "Practice 2"
    practice_3: str = "Practice 3"
    qualifying: str = "Qualifying"
    sprint_race: str = "Sprint Race"
    race: str = "Race"

    # def __iter__(self):
    #     return iter(self.__dict__.values())


class F1Event:
    # {
    #     "_id": {"$oid": "6402bc89d8d6bc2739001359"},
    #     "summary": "🏎 FORMULA 1 QATAR AIRWAYS GRAN PREMIO DEL MADE IN ITALY E DELL'EMILIA-ROMAGNA 2023 - Practice 2",
    #     "location": "Italy",
    #     "description": "Follow all the action on F1 TV and F1.com. \n\nYou can also get the latest F1 news and content, direct to your inbox, via our newsletter by registering with F1.\n\nF1 TV\nhttps://cal.f1.com/f/k95rf/W9Nt\n\nVisit the Race Hub\nhttps://cal.f1.com/f/k95rl/W9Nt\n\nSign up to F1 Newsletter\nhttps://cal.f1.com/f/k95rr/W9Nt\n\nF1 Store\nhttps://cal.f1.com/f/k95rx/W9Nt\n\nF1 Tickets\nhttps://cal.f1.com/f/k95rC/W9Nt\n\nFacebook\nhttps://cal.f1.com/f/k95rG/W9Nt\n\nTwitter\nhttps://cal.f1.com/f/k95rK/W9Nt\n\nInstagram\nhttps://cal.f1.com/f/k95rP/W9Nt\n\nTikTok\nhttps://cal.f1.com/f/k95rS/W9Nt\n\nManage my ECAL\nhttps://support.ecal.com",
    #     "start": {"$date": {"$numberLong": "1684508400000"}},
    #     "end": {"$date": {"$numberLong": "1684512000000"}},
    # }

    def __init__(self, event: dict[str, str or datetime.datetime]):
        self.summary: str = event[EventKeys.summary]
        self.location: str = event[EventKeys.location]
        self.description: str = event[EventKeys.description]
        self.start: datetime.datetime = event[EventKeys.start]
        self.end: datetime.datetime = event[EventKeys.end]

        self.start = self.start.replace(tzinfo=datetime.timezone.utc)
        self.end = self.end.replace(tzinfo=datetime.timezone.utc)

        self.event_name, self.session_name = self.summary.split(" - ")
        self.emoji = self.event_name.split(" ")[0]
        self.event_name = self.event_name.split("FORMULA 1 ")[1]

    @property
    def event_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title=f"**{self.emoji} {self.session_name} <t:{int(self.start.timestamp())}:R>**",
            color=discord.Color.from_rgb(155, 29, 29),
        )
        embed.description = (
            f"**Event:** {self.event_name}\n"
            f"**Location:** {self.location}\n"
            f"**Start:** <t:{int(self.start.timestamp())}:F>"
        )
        return embed

    async def send_event(self, channel: discord.TextChannel) -> None:
        await channel.send(embed=self.event_embed)

    async def send_reminder(
        self, channel: discord.TextChannel, mention_roles: list[discord.Role] = []
    ) -> None:
        print(
            f"Sending reminder about {self.summary} "
            f"to {channel.name} ({channel.id}) "
            f"in {channel.guild.name} ({channel.guild.id}) - "
            f"mentioning {[role.name for role in mention_roles]}"
        )

        role_mentions_str = " ".join([role.mention for role in mention_roles])
        await channel.send(embed=self.event_embed, content=role_mentions_str)


def get_sorted_future_events(
    collection: collection.Collection,
    timedelta: datetime.timedelta = datetime.timedelta(minutes=0),
) -> list[F1Event]:
    """
    Get a list of future F1_Event objects sorted by start time

    Parameters
    ----------
    collection : pymongo.collection.Collection
        The collection to get the events from

    Returns
    -------
    list[F1_Event]
        A list of F1_Event objects sorted by start time
    """
    events: list[F1Event] = []

    documents = collection.find(
        {EventKeys.start: {"$gt": datetime.datetime.utcnow() + timedelta}}
    ).sort(EventKeys.start)

    for event in documents:
        event: dict[str, str or datetime.datetime]
        events.append(F1Event(event))

    print(f"Found {len(events)} future events in {collection.name}")
    return events
