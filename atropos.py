#!/usr/bin/env python3
import os
import sys
import time
import atexit
import asyncio
import discord
import auth
import commands
import reply
import result_file

from dicelang.interpreter import Interpreter
from save_tracker import SaveTracker

# Principal objects.
client = discord.Client(max_messages=128)
last = SaveTracker()
interpreter = Interpreter()
command_parser = commands.CmdParser() 

def handle_saves(dl_interpreter, s_tracker):
  s_tracker.update()
  if s_tracker.should_save():
    dl_interpreter.save()
    s_tracker.saved()

@client.event
async def on_message(msg):
  user_id = msg.author.id
  server_id = msg.channel.id
  user_name = msg.author.display_name
  
  # Skip scanning Atropos' own messages, since not doing so can
  # allow for code injection.
  if msg.author.id == auth.bot_id:
    return
  
  print('{} sent: {}'.format(user_name, msg.content))
  result = command_parser.response_to(msg)
  print(f'type={result.rtype}, value={result.value!r}')
  if isinstance(msg.channel, (discord.DMChannel, discord.GroupChannel)):
    server = msg.channel
  else:
    server = msg.channel.guild
    reply_text, raw_reply_text = reply.build(
      interpreter,
      msg.author,
      server,
      result)
  
  if reply_text:
    try:
      await msg.channel.send(reply_text)
    except discord.errors.HTTPException as e:
      if e.code == 50035: # Message too long to send
        note1 = f"{user_name} got a result that was too large, so I've "
        note2 = "turned it into a file:"
        note = note1 + note2
        path = result_file.get(raw_reply_text, msg.author.name)
        await msg.channel.send(
          content=note,
          file=discord.File(path))
        os.remove(path)
  
  handle_saves(interpreter, last)

atexit.register(interpreter.save)

if __name__ == '__main__':
  print('atropos initialized')
  client.run(auth.bot_token)


