from typing import TYPE_CHECKING

from .client import client
from .config import get_cfg
from .reviewer import launch_review

if TYPE_CHECKING:
    from discord.message import Message


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return

    if message.content.startswith("$review"):
        try:
            await launch_review(message.channel)
        except TimeoutError:
            pass


if __name__ == "__main__":
    client.run(get_cfg().BOT_TOKEN)
