from typing import TYPE_CHECKING

from loguru import logger

from exampion.client import client
from exampion.config import get_cfg
from exampion.reviewer import Review

if TYPE_CHECKING:
    from discord.message import Message


@client.event
async def on_ready():
    logger.info(f"We have logged in as {client.user}")


@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return

    if message.content.startswith("$review"):
        try:
            await Review(message.channel).launch()
        except TimeoutError:
            pass


if __name__ == "__main__":
    logger.info("Started Exampion.")
    client.run(get_cfg().BOT_TOKEN.get_secret_value())
    logger.info("Exampion finished.")
