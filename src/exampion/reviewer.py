from dataclasses import dataclass
from typing import TYPE_CHECKING

from loguru import logger

from .client import client
from .config import get_cfg

if TYPE_CHECKING:
    from discord.message import Message, MessageableChannel


@dataclass
class Review:
    channel: MessageableChannel
    user_id: int = get_cfg().MY_ID

    async def _wait_for_response(self) -> str:
        timeout = get_cfg().REVIEW_TIMEOUT_SECONDS

        def check(message: Message) -> bool:
            return (message.author.id, message.channel.id) == (self.user_id, self.channel.id)

        try:
            logger.debug(f"Waiting up to {timeout} for response...")
            msg = await client.wait_for("message", check=check, timeout=timeout)
            response = msg.content.lower().strip()
            logger.debug(f"Received response: {response}")
            return response

        except TimeoutError:
            partner_id = get_cfg().ACCOUNTABILITY_PARTNER_ID
            await self.channel.send(
                f"<@{self.user_id}> did not respond within {timeout}s. <@{partner_id}>, please "
                "check on them!"
            )
            raise

    async def _get_score(self, habit: str) -> int:
        while True:
            await self.channel.send(f"{habit} (1-7):")
            response = await self._wait_for_response()

            try:
                score = int(response)
                if 1 <= score <= 7:
                    await self.channel.send(f"Got it! {habit}: {score}/7")
                    return score
                else:
                    await self.channel.send("Please enter a number between 1 and 7.")
            except ValueError:
                await self.channel.send("Please enter a valid number.")

    async def launch(self) -> None:
        """Start the nightly review process."""

        await self.channel.send(
            f"<@{self.user_id}>, are you ready to start your nightly review? [y/n]"
        )
        response = await self._wait_for_response()

        if not response.startswith("y"):
            await self.channel.send("Alright, maybe later then!")
            return

        await self.channel.send("Great! Let's begin. Rate each habit on a scale of 1-7.\n")

        scores = [
            await self._get_score(habit)
            for habit in ("Daily mass", "10 minutes of prayer", "Rosary", "Bedtime")
        ]

        if scores:
            overall_score = sum(scores) / len(scores)
            logger.info(f"Got overall score: {overall_score:.1f}")
            await self.channel.send(
                f"\n📊 **Review Complete!**\n"
                f"Overall score: **{overall_score:.1f}/7**\n"
                f"Great job on your nightly review, <@{self.user_id}>!"
            )
