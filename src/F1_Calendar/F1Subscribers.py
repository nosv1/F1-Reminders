from dataclasses import dataclass

import discord
from discord.ext import commands

from .F1Events import SessionNames

from pymongo import collection


@dataclass
class SubscriberKeys:
    channel_id: str = "channel_id"
    roles_ids: str = "roles_ids"
    notes: str = "notes"
    practice_1: str = "practice_1"
    practice_2: str = "practice_2"
    practice_3: str = "practice_3"
    qualifying: str = "qualifying"
    sprint_race: str = "sprint_race"
    race: str = "race"


class F1Subscriber:
    # {
    #     "_id": {"$oid": "640361c320b526daeb8e88b9"},
    #     "channel_id": {"$numberLong": "1069742935299592202"},
    #     "roles_ids": [{"$numberLong": "452726925803388953"}],
    #     "notes": "limitless, f1 lounge, f1 reminders role",
    #     "practice_1": false,
    #     "practice_2": false,
    #     "practice_3": false,
    #     "qualifying": true,
    #     "sprint_race": true,
    #     "race": true,
    # }
    def __init__(self, subscriber: dict[str, str or int or list[int]]):
        self.channel_id: int = subscriber[SubscriberKeys.channel_id]
        self.roles_ids: list[int] = subscriber[SubscriberKeys.roles_ids]
        self.notes: str = subscriber[SubscriberKeys.notes]
        self.ping_practice_1: bool = subscriber[SubscriberKeys.practice_1]
        self.ping_practice_2: bool = subscriber[SubscriberKeys.practice_2]
        self.ping_practice_3: bool = subscriber[SubscriberKeys.practice_3]
        self.ping_qualifying: bool = subscriber[SubscriberKeys.qualifying]
        self.ping_sprint_race: bool = subscriber[SubscriberKeys.sprint_race]
        self.ping_race: bool = subscriber[SubscriberKeys.race]

        self._channel: discord.TextChannel = None
        self._roles: list[discord.Role] = None

    def channel(self, bot: commands.Bot) -> discord.TextChannel:
        if self._channel is None:
            self._channel = bot.get_channel(self.channel_id)

        return self._channel

    def guild(self, bot: commands.Bot) -> discord.Guild:
        return self.channel(bot).guild

    def roles(self, bot: commands.Bot) -> list[discord.Role]:
        if self._roles is None:
            self._roles = [
                self.guild(bot).get_role(role_id) for role_id in self.roles_ids
            ]

        return self._roles

    def ping_for_session(self, session_name: str):
        return (
            (self.ping_practice_1 and session_name == SessionNames.practice_1)
            or (self.ping_practice_2 and session_name == SessionNames.practice_2)
            or (self.ping_practice_3 and session_name == SessionNames.practice_3)
            or (self.ping_qualifying and session_name == SessionNames.qualifying)
            or (self.ping_sprint_race and session_name == SessionNames.sprint_race)
            or (self.ping_race and session_name == SessionNames.race)
        )


def get_event_subscribers(collection: collection.Collection) -> list[F1Subscriber]:
    """
    Get a list of F1_Subscriber objects from the database

    Parameters
    ----------
    collection : pymongo.collection.Collection
        The collection to get the subscribers from

    Returns
    -------
    list[F1_Subscriber]
        A list of F1_Subscriber objects
    """
    subscribers: list[F1Subscriber] = []

    documents = collection.find()
    for document in documents:
        subscribers.append(
            F1Subscriber(
                document[SubscriberKeys.channel_id], document[SubscriberKeys.roles_ids]
            )
        )

    print(f"Found {len(subscribers)} event subscribers in {collection.database.name}")
    return subscribers
