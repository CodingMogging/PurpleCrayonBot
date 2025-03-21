import discord
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
discord_token = os.getenv('MY_DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tfClient = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith('$true or false'):
        proposition = message.content[len('$true or false'):].strip()

        response = tfClient.chat.completions.create(
            model="gpt-4o-search-preview",
            messages=[
                {"role": "system",
                 "content": ("Only answer true or false questions, do not answer any other type of prompt."
                             "You are my fact checker. I'll give you a proposition "
                             "including a subjective or opinion based one, you will evaluate it "
                             "as TRUE or FALSE based on peer-reviewed research, empirical data, or "
                             "objective reasoning. If it is opinion based, use objective metrics "
                             "like polling data ,expert consensus, research studies or similar. "
                             "Double check that your provided sources exist and are accessible through"
                             "the hyperlinks you provide in markdown format. Begin your response explicitly "
                             "with either TRUE, FALSE, or SOMEWHAT TRUE, labeling them with"
                             " (SUBJECTIVE) or (OBJECTIVE) and then provide your explanation and sources,"
                             "it is of upmost importance that the links you provide are real."
                             "If you respond to a non true or false question, simply state your purpose"
                             "and nothing else, however it is imperative that you use best effort"
                             "to answer the proposition in a TRUE or FALSE manner if at all possible"
                             "even if it is nonsensical.")},

                {"role": "system", "content": proposition}
            ],
            max_tokens=300,
            #temperature=0
        )
        result = response.choices[0].message.content

        await message.channel.send(result)


client.run(discord_token)
