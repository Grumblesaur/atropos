#!/usr/bin/env python3
import sys
import os
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
    
    print('Atropos initialized.')

  async def on_ready(self):
    a = discord.Activity(
      type=discord.ActivityType.listening,
      name="+help quickstart")
    await self.change_presence(activity=a)
  
  def console_log(self, msg, command):
    if isinstance(msg.channel, discord.GroupChannel):
      server_or_dm = msg.channel
      channel_name = server_or_dm.name
    elif isinstance(msg.channel, discord.DMChannel):
      server_or_dm = msg.channel
      channel_name = f'Atropos-{msg.author.name}'
    else:
      server_or_dm = msg.channel.guild
      channel_name = f'{server_or_dm.name}:{msg.channel.name}'
    s = '\n'.join([
      f'[usr:{msg.author.display_name}] in [chn:{channel_name}] sent:',
      f'  {msg.content}',
      f'  {command!r}',
    ])
    print(s)
    return

  async def on_message(self, msg):
    # Skip scanning Atropos' own messages to prevent code injection.
    if msg.author.id == self.user.id:
      return
    
    # Process the message to determine if it is a command.
    possible_command = commands.Command(msg)
    self.console_log(msg, possible_command)
    
    # Send a reply if it was a valid command, else this operation is a no-op..
    await possible_command.send_reply_as(self)
    

def main(*argv):
  Atropos(max_messages=128).run(auth.bot_token)

if __name__ == '__main__':
  main(*sys.argv)


