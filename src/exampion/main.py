# This example requires the 'message_content' intent.
import os
from typing import TYPE_CHECKING

from discord import Client, Intents

if TYPE_CHECKING:
    from discord.message import Message

intents = Intents.default()
intents.message_content = True

client = Client(intents=intents)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")


def get_token() -> str:
    if not (token := os.getenv("BOT_TOKEN")):
        raise RuntimeError("'BOT_TOKEN' env var not set!")
    return token


if __name__ == "__main__":
    client.run(get_token())
