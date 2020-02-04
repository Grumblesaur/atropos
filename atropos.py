#!/usr/bin/env python3

import sys
import time
import asyncio
import discord
import commands
from dicelang.interpreter import Interpreter

client = discord.Client(max_messages=128)
interpreter = Interpreter()

class SaveTracker(object):
  def __init__(self, save_interval=300, backup_interval=1800):
    start_time = time.time()
    self.message_at = start_time 
    self.save_at    = start_time
    self.backup_at  = start_time
    
    self.save_interval   = save_interval
    self.backup_interval = backup_interval
    
  def update(self):
    self.message_at = time.time()
  
  def should_save(self):
    return time.time() - self.save_at > self.save_interval
  
  def saved(self):
    self.save_at = time.time()
  
  def should_back_up(self):
    return time.time() - self.backup_at > self.backup_interval
  
  def backed_up(self):
    t = time.time()
    self.backup_at = t
    self.save_at   = t
  
last = SaveTracker()

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
    result = interpreter.execute(command, user_id, server_id)
    reply = '{} rolled:\n  {}'.format(user_name, result)
    await msg.channel.send(reply)
  else:
    pass
  
  last.update()
  if last.should_save():
    interpreter.datastore.save()
    last.saved()
  elif last.should_back_up():
    interpreter.datastore.backup()
    last.backed_up()
  
if __name__ == '__main__':
  import auth
  print('atropos initialized')
  client.run(auth.bot_token)


