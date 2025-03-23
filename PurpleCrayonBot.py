import discord
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

discord_token = os.getenv('MY_DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tfClient = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def triage(proposition: str) -> str:
    response = tfClient.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",
             "content": ("You are a classifier bot."
                         "Given a proposition, you must exclusively perform one of two actions, you will not deviate from these actions:"
                         "A) WEB_SEARCH_REQUIRED: Requires external verification or searching (current events, niche facts, uncertain statements). In this case, output ONLY WEB_SEARCH_REQUIRED."
                         "B) NO_SEARCH_REQUIRED: Can be confidently answered without external search (logical, mathematical, common knowledge, in this case"
                         "Only answer true or false questions, do not answer any other type of prompt."
                         "You are my fact checker. I'll give you a proposition "
                         "including a subjective or opinion based one, you will evaluate it "
                         "as TRUE or FALSE based on peer-reviewed research, empirical data, or "
                         "objective reasoning. If it is opinion based, use objective metrics "
                         "like polling data ,expert consensus, research studies or similar. "
                         "begin your response with either TRUE, FALSE, or SOMEWHAT TRUE, labeling them with"
                         " (SUBJECTIVE) or (OBJECTIVE) and then provide your explanation and sources,"
                         "If you respond to a non true or false question, simply state your purpose"
                         "and nothing else, however it is imperative that you use best effort"
                         "to answer the proposition in a TRUE or FALSE manner if at all possible"
                         "even if it is nonsensical."
                         )},

            {"role": "system", "content": proposition}
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content


def true_or_false(proposition: str) -> str:
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
    )
    result = response.choices[0].message.content
    return result


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith('$true or false'):
        proposition = message.content[len('$true or false'):].strip()
        if triage(proposition) == 'WEB_SEARCH_REQUIRED':
            proposition = true_or_false(proposition)
            print("Used 4o-search-preview")
        else:
            proposition = triage(proposition)
            print("Used 4o")
        await message.channel.send(proposition)
        print(proposition)


client.run(discord_token)
