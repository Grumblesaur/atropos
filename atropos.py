#!/usr/bin/env python3
import os
import asyncio
import discord
import auth
import commands
import reply
from result_file import ResultFile

from dicelang.interpreter import Interpreter

class Atropos(discord.Client):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.interpreter = Interpreter()
    self.command_parser = commands.CommandParser()
    
    # Initialize configuration directory if not already established.
    config_dir_path = os.environ.get('ATROPOS_CONFIG')
    if config_dir_path is None:
      raise Exception('Environment variable "ATROPOS_CONFIG" not set.')
    if not os.path.isdir(config_dir_path):
      os.mkdir(config_dir_path)

  async def on_ready(self):
    a = discord.Activity(
      type=discord.ActivityType.listening,
      name="+help quickstart")
    await self.change_presence(activity=a)

  async def on_message(self, msg):
    # Skip scanning Atropos' own messages, since not doing so can
    # allow for code injection.
    if msg.author.id == self.user.id:
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
    
    # Process the message to determine if it is a command.
    result = await self.result_of_command(msg)
    
    # Construct a debug message to print out, stating the user, message
    # location, message content, and the type of command it evaluated as.
    db = '\n'.join([
      f'[usr:{msg.author.display_name}] in [chn:{channel_name}] sent:',
      f'  {msg.content}',
      f'  [type:{result.rtype}] [value={result.value!r}]',
    ])
    print(db)
    
    # If the command was not valid, terminate processing here.
    if not result:
      return

    # Construct reply data based on the contents of the message, and
    # our copy of the dicelang interpreter.
    async with msg.channel.typing():
      reply_data = await self.reply_for_result(
        self.interpreter,
        msg.author,
        server_or_dm,
        result)
    
    text_or_embed, raw, out = reply_data
    if isinstance(text_or_embed, discord.Embed):
      text_or_embed.set_author(name=self.get_display_name(msg))
    await self.send(text_or_embed, raw, out, msg)
  
  def get_display_name(self, msg):
    for user in msg.channel.members:
      if user.id == self.user.id:
        return f'{user.display_name}'
    return 'Atropos'  
  
  async def result_of_command(self, msg):
    return self.command_parser.response_to(msg)
  
  async def reply_for_result(self, dicelang, author, channel, result):
    return reply.build(dicelang, author, channel, result)
  
  async def send_embed(self, embed, msg):
    await msg.channel.send(embed=embed)
  
  async def send(self, reply_body, raw_reply_text, printout, msg):
    if not reply_body:
      return
    
    try:
      if isinstance(reply_body, discord.Embed):
        await msg.channel.send(embed=reply_body)
      else:
        await msg.channel.send(reply_body)
    except discord.errors.HTTPException as e:
      if e.code == 50035: # Message too long.
        note = f"The response to `{msg.author.display_name}`'s request "
        note += "was too large, so I've uploaded it as a file instead:"
        with ResultFile(raw_reply_text, msg.author.name, printout) as rf:
          await msg.channel.send(content=note, file=rf)
    

if __name__ == '__main__':
  atropos = Atropos(max_messages=128)
  print('atropos initialized')
  atropos.run(auth.bot_token)


