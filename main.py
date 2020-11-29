import discord
import os
from discord.ext import commands, tasks


def read_token():
  with open ("token.txt", 'r') as f:
    lines = f.readlines()
    return lines[0].strip()
  

client = commands.Bot(command_prefix = '.')

for filename in os.listdir('./cogs'): 
  if filename.endswith('.py'):
    client.load_extension(f'cogs.{filename[:-3]}')


@client.event
async def on_message(message):
  if message.content.startswith('..') or message.content.startswith('.gw') is False or message.author.bot:
    return

  await client.process_commands(message)


client.run(read_token())
