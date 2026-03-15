from discord import Client, Intents

intents = Intents.default()
intents.message_content = True

client = Client(intents=intents)
