import sys
import time
import asyncio
import discord
import commands

def make_client():
  client = discord.Client(max_messages=128)
  
  @client.event
  async def on_message(msg):
    name = msg.author.name
    try:
      nick = msg.author.nick
    except AttributeError:
      nick = name
    response, command = commands.scan(msg.content)
    
    if response == commands.ResponseType.NONE:
      pass
    elif response == commands.ResponseType.DICE:
      pass # TODO: call interpreter
    else:
      pass

