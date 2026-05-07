from loguru import logger

from exampion.client import client
from exampion.config import get_cfg
from exampion.reviewer import Review


@client.event
async def on_ready():
    logger.info(f"We have logged in as {client.user}")

    # Assuming the bot is in one guild with one text channel
    guild = client.guilds[0]
    channel = guild.text_channels[0]
    logger.debug(f"Initiating review ({guild=}, {channel=})...")

    try:
        await Review(channel).launch()
    except TimeoutError:
        logger.warning("Review timeout out!")

    logger.info("Review finished! Closing client...")
    await client.close()


def setup_logging() -> None:
    logger.add("logs/exampion.log", rotation="1 day", retention="30 days", level="DEBUG")


def main():
    setup_logging()
    logger.info("Started Exampion.")

    token = get_cfg().BOT_TOKEN.get_secret_value()
    logger.debug(f"Using bot token: {token[:4]}...{token[-4:]}")
    client.run(token)

    logger.info("Exampion finished.")


if __name__ == "__main__":
    main()
