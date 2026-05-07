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
        logger.info("Message starts with '$review': initiating review...")
        try:
            await Review(message.channel).launch()
        except TimeoutError:
            logger.warning("Review timeout out!")

        logger.info("Review finished! Closing client...")
        await client.close()


def main():
    logger.add("logs/exampion.log", rotation="1 day", retention="30 days", level="DEBUG")
    logger.info("Started Exampion.")
    token = get_cfg().BOT_TOKEN.get_secret_value()
    logger.debug(f"Using bot token: {token[:8]}...")
    client.run(token)
    logger.info("Exampion finished.")


if __name__ == "__main__":
    main()
