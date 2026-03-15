from typing import TYPE_CHECKING

from .client import client
from .config import get_cfg

if TYPE_CHECKING:
    from discord.message import Message, MessageableChannel


async def launch_review(channel: MessageableChannel) -> None:
    """Start the nightly review process."""

    async def wait_for_response() -> str:
        timeout = get_cfg().REVIEW_TIMEOUT_SECONDS

        def check(message: Message) -> bool:
            return (message.author.id, message.channel.id) == (user_id, channel.id)

        try:
            msg = await client.wait_for("message", check=check, timeout=timeout)
            return msg.content.lower().strip()

        except TimeoutError:
            partner_id = get_cfg().ACCOUNTABILITY_PARTNER_ID
            await channel.send(
                f"<@{user_id}> did not respond within {timeout}s. <@{partner_id}>, please check on "
                "them!"
            )
            raise

    async def get_score(habit: str) -> int:
        while True:
            await channel.send(f"{habit} (1-7):")
            response = await wait_for_response()

            try:
                score = int(response)
                if 1 <= score <= 7:
                    await channel.send(f"Got it! {habit}: {score}/7")
                    return score
                else:
                    await channel.send("Please enter a number between 1 and 7.")
            except ValueError:
                await channel.send("Please enter a valid number.")

    user_id = get_cfg().MY_ID
    await channel.send(f"<@{user_id}>, are you ready to start your nightly review? [y/n]")
    response = await wait_for_response()

    if not response.startswith("y"):
        await channel.send("Alright, maybe later then!")
        return

    await channel.send("Great! Let's begin. Rate each habit on a scale of 1-7.\n")

    scores = [
        await get_score(habit)
        for habit in ("Daily mass", "10 minutes of prayer", "Rosary", "Bedtime")
    ]

    if scores:
        overall_score = sum(scores) / len(scores)
        await channel.send(
            f"\n📊 **Review Complete!**\n"
            f"Overall score: **{overall_score:.1f}/7**\n"
            f"Great job on your nightly review, <@{user_id}>!"
        )
