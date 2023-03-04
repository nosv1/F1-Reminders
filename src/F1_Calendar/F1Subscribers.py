from dataclasses import dataclass

import discord
from discord.ext import commands

from pymongo import collection


@dataclass
class SubscriberKeys:
    channel_id: str = "channel_id"
    roles_ids: str = "roles_ids"


class F1Subscriber:
    def __init__(self, channel_id: int, roles_ids: list[int]) -> None:
        self.channel_id: int = channel_id
        self.roles_ids: list[int] = roles_ids

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
