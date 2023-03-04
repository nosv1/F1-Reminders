import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

from F1CalendarCog import F1CalendarCog


load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")
    bot.add_cog(F1CalendarCog(bot))


if __name__ == "__main__":
    token = os.getenv("DISCORD_F1_REMINDERS_TOKEN")
    bot.run(token)
