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

with open('Triage_Prompt.txt', 'r') as file:
    prompt = file.read()

with open('Search_Prompt.txt', 'r') as file:
    search_prompt = file.read()


def triage(proposition: str) -> str:
    response = tfClient.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",
             "content": prompt},

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
             "content": search_prompt},

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

  #reply functionality
    if message.content.lower().startswith('factcheck') and message.reference: #checks if it starts with factcheck and if it is a reply to a message
        try:
            ref_message = message.reference.resolved #this is the message that we replied to
            if ref_message is None:
                ref_message = await message.channel.fetch_message(message.reference.message_id)

            if ref_message and ref_message.content:                
                proposition = ref_message.content
                if triage(proposition) == 'WEB_SEARCH_REQUIRED':
                    proposition = true_or_false(proposition)
                    print("Used 4o-search-preview")
                else:
                    proposition = triage(proposition)
                    print("Used 4o")
                await message.channel.send(proposition)
                print(proposition)
            else:
                await message.channel.send("no text context")
        except Exception as e:
            print("Error fetching the referenced message:", e)
            await message.channel.send("error trying to read reply")
  


client.run(discord_token)
