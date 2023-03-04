from Database import MongoDatabase
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks

import F1_Calendar.F1Events as F1Events
from F1_Calendar.F1Events import F1Event

import F1_Calendar.F1Subscribers as F1Subscribers


class F1CalendarCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_events.start()
        self.set_next_f1_event.start()

        self._next_f1_event: F1Event = None

    @property
    async def next_f1_event(self) -> F1Event:
        if self._next_f1_event is None:
            await self.set_next_f1_event()

        return self._next_f1_event

    ### Commands ###

    @commands.command()
    async def next(self, ctx: commands.Context):
        if await self.next_f1_event is None:
            await ctx.send("No upcoming events")
            return

        if not isinstance(self._next_f1_event, F1Event):
            return

        await self._next_f1_event.send_event(ctx.channel)

    ### Tasks ###

    @tasks.loop(seconds=60)
    async def check_events(self):
        if not isinstance(self._next_f1_event, F1Event):
            return

        if self._next_f1_event.start - datetime.now() > timedelta(minutes=30):
            return

        print(f"Sending reminders about {self._next_f1_event.summary}...")

        database, _ = MongoDatabase().connect_to_F1_Calendar()
        event_subscribers = F1Subscribers.get_event_subscribers(
            database.connected_database.event_subscribers
        )
        database.close_connection()

        for subscriber in event_subscribers:
            try:
                await self._next_f1_event.send_reminder(
                    subscriber.channel(self.bot), subscriber.roles(self.bot)
                )
            except Exception as e:
                print(f"Failed to send reminder to {subscriber.channel_id}: {e}")

        self._next_f1_event = None

    @tasks.loop(hours=1)
    async def set_next_f1_event(self):
        database, _ = MongoDatabase().connect_to_F1_Calendar()
        F1_2023_events_collection = database.connected_database.get_collection(
            "F1_2023_events"
        )
        future_events: list[F1Event] = F1Events.get_sorted_future_events(
            F1_2023_events_collection
        )
        database.close_connection()

        if not future_events:
            self._next_f1_event = None
            print(f"No future events found")
            return

        self._next_f1_event = future_events[0]
        print(
            f"Next F1 event is {self._next_f1_event.summary} "
            f"at {self._next_f1_event.start.strftime('%Y-%m-%d %H:%M:%S')}"
        )
