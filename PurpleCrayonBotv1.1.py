import discord
from discord import app_commands
from dotenv import load_env
import os
import asyncio
from openai import OpenAI

load_dotenv()
discord_token = os.getenv('MY_DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
tfClient = OpenAI (api_key=os.getenv('OPENAI_API_KEY'))

# Cooldown - track user request timing
cooldowns = {}
COOLDOWN_TIME = 15 # Cooldown time (s)

@tree.command(name="factcheck", description="Check if a statement is true or false.")
async def factcheck(interaction: discord.Interaction, statement: str):
    user_id = interaction.user.id
    if user_id in cooldowns and (asyncio.get_event_loop().time() - cooldowns[user_id]) < COOLDOWN_TIME:
        await interaction.response.send_message("⏳ You are sending requests too quickly. Please wait a few seconds.", ephemeral=True)
        return

    cooldowns[user_id] = asyncio.get_event_loop().time()

    prompt = ("You are a fact-checking assistant. Your task is to evaluate statements and classify them as one of the following:\n\n"
        "TRUE (OBJECTIVE) – The statement is factually correct based on empirical data, scientific research, or official records.\n\n"
        "FALSE (OBJECTIVE) – The statement is factually incorrect based on reliable sources.\n\n"
        "SOMEWHAT TRUE (SUBJECTIVE) – The statement contains some truth but is context-dependent or disputed.\n\n"
        "For subjective claims, rely on expert consensus, peer-reviewed studies, polling data, or official reports. Provide citations in markdown format with working hyperlinks.\n\n"
        "If the message is not a true-or-false question, respond: 'I only answer true-or-false questions.'\n"
        "DO NOT generate made-up sources—double-check that all links are real and accessible.\n\n"
        f"Now, analyze the following proposition: '{statement}'")

    response = tfClient.chat.completion.create(
        model="gpt-4o-search-preview",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=500  # institute a limit to responses to perserve resources
    )

    result = response.choices[0].message.content
    await interaction.response.send_message(result)

@client.event
async def on_ready():
    await tree.sync()
    print(f'Logged in as {client.user}')

client.run(discord_token)
