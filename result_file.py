import os
import time
import discord

def init_file_area():
  path = os.path.join(os.environ['ATROPOS_CONFIG'], 'tmp')
  if not os.path.isdir(path):
    os.mkdir(path)
  return path

class ResultFile(object):
  FILE_AREA = init_file_area()
  
  def __init__(self, raw_result_text, user_name, printout):
    self.timestamp = time.strftime("%Y-%m-%d-%H:%M:%S")
    filename = f'{user_name}-{self.timestamp}.txt'
    self.path = os.path.join(ResultFile.FILE_AREA, filename)
    with open(self.path, 'w') as f:
      printout = printout + '\n' if printout else ''
      f.write(f'{printout}{raw_result_text}')
  
  def __enter__(self):
    return discord.File(self.path)
  
  def __exit__(self, exc_type, exc, tb):
    os.remove(self.path)
  

