#!/usr/bin/env python3

import sys
import time
import atexit
import asyncio
import discord
import auth
import commands

from message_handlers import handle_dicelang_command
from message_handlers import handle_view_command
from dicelang.interpreter import Interpreter
from save_tracker import SaveTracker

# Principal objects.
client = discord.Client(max_messages=128)
last = SaveTracker()
interpreter = Interpreter()
 

def handle_saves(dl_interpreter, s_tracker):
  s_tracker.update()
  if s_tracker.should_save():
    dl_interpreter.datastore.save()
    s_tracker.saved()

@client.event
async def on_message(msg):
  user_id = msg.author.id
  server_id = msg.channel.id
  user_name = msg.author.display_name
  
  # Skip scanning Atropos' own messages, since not doing so can
  # allow for code injection.
  if user_id == auth.bot_id:
    return
  
  print('{} sent: {}'.format(user_name, msg.content))
  response, command = commands.scan(msg.content)
  print('response={}; command={}'.format(response, command))
  
  if response == commands.ResponseType.NONE:
    pass
  elif response == commands.ResponseType.DICE:
    args = (interpreter, command, user_id, user_name, server_id)
    result = handle_dicelang_command(*args)
    if result:
      fmt = '{} rolled:\n```diff\n{}```'
      reply = fmt.format(user_name, repr(result.value))
    else:
      fmt = '{} received error:\n```{}```'
      reply = fmt.format(user_name, result.value)
    await msg.channel.send(reply)
  elif response in (
      commands.ResponseType.VIEW_GLOBALS,
      commands.ResponseType.VIEW_SHAREDS,
      commands.ResponseType.VIEW_PRIVATES,
      commands.ResponseType.VIEW_ALL):
    result = handle_view_command(interpreter, response, user_id, server_id)
    reply = '{} requested to view:\n```{}```'.format(user_name, result)
    await msg.channel.send(reply)
  elif response == commands.ResponseType.HELP:
    await msg.channel.send('{} requested general help. README:\n {}'.format(
      user_name,
      'https://github.com/Grumblesaur/atropos/blob/master/README.md'))
  
  handle_saves(interpreter, last)

atexit.register(interpreter.datastore.save)

if __name__ == '__main__':
  print('atropos initialized')
  client.run(auth.bot_token)


