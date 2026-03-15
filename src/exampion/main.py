from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from discord import Client, Intents

from .config import get_cfg

if TYPE_CHECKING:
    from discord.message import Message, MessageableChannel

intents = Intents.default()
intents.message_content = True

client = Client(intents=intents)


# Configuration
HABITS = ["Daily mass", "10 minutes of prayer", "Rosary", "Bedtime"]
TIMEOUT_SECONDS = 3600  # 1 hour


@dataclass
class ReviewState:
    """Track the state of an ongoing review."""

    user_id: int
    channel_id: int
    current_habit_idx: int = 0
    scores: list[int] = field(default_factory=list)


# Active reviews: {user_id: ReviewState}
active_reviews: dict[int, ReviewState] = {}


async def wait_for_response(user_id: int, channel_id: int, timeout: int) -> str | None:
    """Wait for a response from a specific user in a specific channel."""

    def check(message: Message) -> bool:
        return (
            message.author.id == user_id
            and message.channel.id == channel_id
            and not message.author.bot
        )

    try:
        msg = await client.wait_for("message", check=check, timeout=timeout)
        return msg.content.lower().strip()
    except TimeoutError:
        return None


async def start_review(user_id: int, channel: MessageableChannel) -> None:
    """Start the nightly review process."""

    # Check if user already has an active review
    if user_id in active_reviews:
        await channel.send("You already have an active review! Please finish it first.")
        return

    # Initialize review state
    review = ReviewState(user_id=user_id, channel_id=channel.id)
    active_reviews[user_id] = review

    # Step 1: Ask if ready to start
    await channel.send(f"<@{user_id}>, are you ready to start your nightly review? (yes/no)")

    timeout = get_cfg().REVIEW_TIMEOUT_SECONDS
    response = await wait_for_response(user_id, channel.id, timeout)

    if response is None:
        del active_reviews[user_id]
        try:
            partner_id = get_cfg().ACCOUNTABILITY_PARTNER_ID
            await channel.send(
                f"<@{user_id}> did not respond within the timeout. "
                f"<@{partner_id}>, please check on them!"
            )
        except ValueError:
            await channel.send(
                f"<@{user_id}> did not respond within the timeout. Notifying the server..."
            )
        return

    if "yes" not in response:
        del active_reviews[user_id]
        await channel.send("Alright, maybe later then!")
        return

    await channel.send("Great! Let's begin. Rate each habit on a scale of 1-7.\n")

    # Step 2: Ask about each habit
    for habit in HABITS:
        while True:
            await channel.send(f"{habit} (1-7):")
            response = await wait_for_response(user_id, channel.id, timeout)

            if response is None:
                del active_reviews[user_id]
                try:
                    partner_id = get_cfg().ACCOUNTABILITY_PARTNER_ID
                    await channel.send(
                        f"<@{user_id}> did not respond within the timeout. "
                        f"<@{partner_id}>, please check on them!"
                    )
                except ValueError:
                    await channel.send(
                        f"<@{user_id}> did not respond within the timeout. Notifying the server..."
                    )
                return

            try:
                score = int(response)
                if 1 <= score <= 7:
                    review.scores.append(score)
                    await channel.send(f"Got it! {habit}: {score}/7")
                    break  # Move to next habit
                else:
                    await channel.send("Please enter a number between 1 and 7.")
            except ValueError:
                await channel.send("Please enter a valid number.")

    # Step 3: Summary
    if review.scores:
        overall_score = sum(review.scores) / len(review.scores)
        await channel.send(
            f"\n📊 **Review Complete!**\n"
            f"Overall score: **{overall_score:.1f}/7**\n"
            f"Great job on your nightly review, <@{user_id}>!"
        )
    del active_reviews[user_id]


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return

    if message.content.startswith("$review"):
        # Start the review for the user who sent the command
        await start_review(message.author.id, message.channel)


if __name__ == "__main__":
    client.run(get_cfg().BOT_TOKEN)
