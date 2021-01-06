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
    print('\n'.join([
      f'[usr:{msg.author.display_name}]',
      f'  in [chn:{channel_name}]',
      f'    sent {msg.content!r}',
      f'    which parsed as {command!r}',
    ]))
  
  def is_our_message(self, msg):
    return msg.author.id == self.user.id
  
  async def on_message(self, msg):
    if self.is_our_message(msg):
      return
    
    # Process the message to generate a command object.
    cmd = commands.Command(msg)
    self.console_log(msg, cmd)
    
    # Reply will be sent if command was valid, or ignored otherwise.
    await cmd.send_reply_as(self)
    

def main(*argv):
  Atropos(max_messages=128).run(auth.bot_token)

if __name__ == '__main__':
  main(*sys.argv)


