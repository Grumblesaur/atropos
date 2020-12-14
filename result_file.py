import os
import time

ROOT_PATH = os.environ['ATROPOS_CONFIG']
FILE_AREA = os.path.join(ROOT_PATH, 'tmp')
if not os.path.isdir(FILE_AREA):
  os.mkdir(FILE_AREA)

def get(raw_result_text, user_name, printout):
  timestamp = time.strftime("%Y-%m-%d-%H:%M:%S")
  filename = f'{user_name}-{timestamp}.txt'
  full_path = os.path.join(FILE_AREA, filename)
  with open(full_path, 'w') as f:
    printout = printout + '\n' if printout else ''
    f.write(f'{printout}{raw_result_text}')
  return full_path
  
  
