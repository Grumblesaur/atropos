#!/usr/bin/env python3
import os
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

  async def on_ready(self):
    activity_type = discord.ActivityType.listening
    name = "+help quickstart"
    activity = discord.Activity(type=activity_type, name=name)
    await self.change_presence(activity=activity)

  async def on_message(self, msg):
    # Skip scanning Atropos' own messages, since not doing so can
    # allow for code injection.
    if msg.author.id == self.user.id:
      return
    
    # Determine if user message was a command.
    result = await self.result_of_command(msg)
    if not result:
      return
    
    # Channel name is for debug purposes only.
    if isinstance(msg.channel, discord.GroupChannel):
      server_or_dm = msg.channel
      channel_name = server_or_dm.name
    elif isinstance(msg.channel, discord.DMChannel):
      server_or_dm = msg.channel
      channel_name = f'Atropos-{msg.author.name}'
    else:
      server_or_dm = msg.channel.guild
      channel_name = f'{server_or_dm.name}:{msg.channel.name}'
    
    # debug prints
    print(f'[usr:{msg.author.display_name}] in [chn:{channel_name}] sent:')
    print(f'{msg.content}')
    print(f'type={result.rtype}, value={result.value!r}')
    

    # Construct reply data based on the contents of the message, and
    # our copy of the dicelang interpreter.
    async with msg.channel.typing():
      reply_data = await self.reply_for_result(
        self.interpreter,
        msg.author,
        server_or_dm,
        result)
    
    text, raw, out = reply_data
    
    await self.send(text, raw, out, msg)
    
  async def result_of_command(self, msg):
    return self.command_parser.response_to(msg)
  
  async def reply_for_result(self, dicelang, author, channel, result):
    return reply.build(dicelang, author, channel, result)
  
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


