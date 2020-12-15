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

class Atropos(discord.Client):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.interpreter = Interpreter()
    self.command_parser = commands.CmdParser()
    
    # Initialize configuration directory if not already established.
    config_dir_path = os.environ.get('ATROPOS_CONFIG')
    if config_dir_path is None:
      raise Exception('Environment variable "ATROPOS_CONFIG" not set.')
    if not os.path.isdir(config_dir_path):
      os.mkdir(config_dir_path)

  #@client.event
  async def on_ready(self):
    activity_type = discord.ActivityType.listening
    name = "+help quickstart"
    activity = discord.Activity(type=activity_type, name=name)
    await self.change_presence(activity=activity)

  #@client.event
  async def on_message(self, msg):
    # Skip scanning Atropos' own messages, since not doing so can
    # allow for code injection.
    if msg.author.id == self.user.id:
      return
    
    # Determine if user message was a command.
    result = self.command_parser.response_to(msg)
    
    # debug prints
    print(f'{msg.author.display_name} sent: {msg.content}')
    print(f'type={result.rtype}, value={result.value!r}')
    
    if isinstance(msg.channel, (discord.DMChannel, discord.GroupChannel)):
      server_or_dm = msg.channel
    else:
      server_or_dm = msg.channel.guild
    
    # Construct reply data based on the contents of the message, and
    # our copy of the dicelang interpreter.
    reply_data = reply.build(
      self.interpreter,
      msg.author,
      server_or_dm,
      result)
    
    text, raw, out = reply_data
    
    # Send the reply.
    await self.send(text, raw, out, msg)
    
  async def send(self, reply_text, raw_reply_text, printout, msg):
    if not reply_text:
      return
    try:
      await msg.channel.send(reply_text)
    except discord.errors.HTTPException as e:
      if e.code == 50035: # Message too long.
        note = f"The response to `{msg.author.display_name}`'s request "
        note += "was too large, so I've uploaded it as a file instead:"
        path = result_file.get(raw_reply_text, msg.author.name, printout)
        await msg.channel.send(content=note, file=discord.File(path))
        os.remove(path)

if __name__ == '__main__':
  atropos = Atropos(max_messages=128)
  print('atropos initialized')
  atropos.run(auth.bot_token)


