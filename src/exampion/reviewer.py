from dataclasses import dataclass
from typing import TYPE_CHECKING

from loguru import logger

from exampion.client import client
from exampion.config import get_cfg

if TYPE_CHECKING:
    from discord.message import Message, MessageableChannel

HABITS = (
    "Waking up fast",
    "Angelus",
    "Daily mass",
    "10 minutes of prayer + reflection + text intention",
    "Getting ready for bed by 10:30, 10:45 latest",
    "Night prayer",
    "[Optional] Rosary",
    "[Virtue] Prayer intentionality",
    "[Virtue] Humility",
    "[Virtue] Intentionality with time (<2 hours vegging)",
    "[Virtue] Chastity",
    "[Wednesday] Michael check-in",
    "[Thursday] Holy hour",
    "[Friday] Lunch fast",
)


@dataclass
class Review:
    channel: MessageableChannel
    user_id: int = get_cfg().MY_ID

    async def _wait_for_response(self) -> str:
        timeout = get_cfg().REVIEW_TIMEOUT_SECONDS

        def check(message: Message) -> bool:
            return (message.author.id, message.channel.id) == (self.user_id, self.channel.id)

        try:
            logger.debug(f"Waiting up to {timeout}s for response...")
            msg = await client.wait_for("message", check=check, timeout=timeout)
            response = msg.content.lower().strip()
            logger.debug(f"Received response: {response}")
            return response

        except TimeoutError:
            partner_id = get_cfg().ACCOUNTABILITY_PARTNER_ID
            logger.warning(
                f"Response took longer than {timeout}s: Pinging accountability partner "
                f"{partner_id}..."
            )
            await self.channel.send(
                f"<@{self.user_id}> did not respond within {timeout}s. <@{partner_id}>, please "
                "check on them!"
            )
            raise

    async def _get_score(self, habit: str) -> int | None:
        logger.debug(f"Getting score for habit: {habit}")
        while True:
            await self.channel.send(f"{habit} (1-7, or s to skip):")
            response = await self._wait_for_response()

            first = (response[0] if response else "").lower()
            if first == "s":
                await self.channel.send(f"Skipping {habit}...")
                return

            try:
                score = int(first)
            except ValueError:
                await self.channel.send("Please enter a valid number.")
                return

            if 1 <= score <= 7:
                await self.channel.send(f"Got it! {habit}: {score}/7")
                return score
            else:
                await self.channel.send("Please enter a number between 1 and 7.")

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

        scores = [score for habit in HABITS if (score := await self._get_score(habit)) is not None]

        if scores:
            overall_score = sum(scores) / len(scores)
            logger.info(f"Got overall score: {overall_score:.1f}")
            await self.channel.send(
                f"\n📊 **Review Complete!**\n"
                f"Overall score: **{overall_score:.1f}/7**\n"
                f"Great job on your nightly review, <@{self.user_id}>!"
            )
