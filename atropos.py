#!/usr/bin/env python3

import sys
import time
import atexit
import asyncio
import discord
import commands
from message_handlers import handle_dicelang_command
from dicelang.interpreter import Interpreter
from save_tracker import SaveTracker


# Principal objects.
client = discord.Client(max_messages=128)
last = SaveTracker()
interpreter = Interpreter()
 

def handle_saves_and_backups(dl_interpreter, s_tracker):
  s_tracker.update()
  if s_tracker.should_back_up():
    dl_interpreter.datastore.backup()
    s_tracker.backed_up()
  elif s_tracker.should_save():
    dl_interpreter.datastore.save()
    dl_interpreter.saved()

@client.event
async def on_message(msg):
  user_id = msg.author.id
  server_id = msg.channel.id
  user_name = msg.author.display_name
  
  print('{} sent: {}'.format(user_name, msg.content))
  response, command = commands.scan(msg.content)
  print('response={}; command={}'.format(response, command))
  
  if response == commands.ResponseType.NONE:
    pass
  elif response == commands.ResponseType.DICE:
    args = (interpreter, command, user_id, user_name, server_id)
    result = handle_dicelang_command(*args)
    if result:
      fmt = '{} rolled:\n```{}```'
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
    pass
  
  handle_saves_and_backups(interpreter, last)

atexit.register(interpreter.datastore.save)

if __name__ == '__main__':
  import auth
  print('atropos initialized')
  client.run(auth.bot_token)


