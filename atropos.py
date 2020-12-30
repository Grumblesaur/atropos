#!/usr/bin/env python3
import os
import asyncio
import discord
import auth
import commands

class Atropos(discord.Client):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
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
    possible_command = commands.Command(msg)
    
    # Construct a debug message to print out, stating the user, message
    # location, message content, and the type of command it evaluated as.
    db = '\n'.join([
      f'[usr:{msg.author.display_name}] in [chn:{channel_name}] sent:',
      f'  {msg.content}',
      f'  {possible_command!r}',
    ])
    print(db)
    
    # Construct reply data based on the contents of the message, and
    # our copy of the dicelang interpreter.
    if possible_command:
      async with msg.channel.typing():
        await possible_command.send_reply_as(self)
    
if __name__ == '__main__':
  atropos = Atropos(max_messages=128)
  print('atropos initialized')
  atropos.run(auth.bot_token)


