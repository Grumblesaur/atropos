import re
import os
HELP_PATH = 'helpfiles/'

def build_help_table():
  table = { }
  options = { }
  for help_file_path in os.listdir(HELP_PATH):
    if help_file_path.endswith('.md'):
      key = help_file_path.split(os.sep)[-1].replace('.md', '')
      table[key] = help_file_path
      table[key] = os.path.join(HELP_PATH, help_file_path)
    else:
      option_key = help_file_path.split(os.sep)[-1]
      options[option_key] = { }
      for option_file_path in os.listdir(os.path.join(HELP_PATH, option_key)):
        key = option_file_path.split(os.sep)[-1].replace('.md', '')
        location = os.path.join(HELP_PATH, option_key, option_file_path)
        options[option_key][key] = location
  return table, options

_help_messages, _options = build_help_table()

def get_canonical_key(keyword):
  out = None
  keyword = keyword.lower()
  pattern = re.compile(keyword)
  if keyword not in _help_messages:
    for topic in _help_messages:
      if pattern.match(topic):
        out = topic
        break
  return out

def get_canonical_option(option):
  out = None
  try:
    option = option.lower()
  except AttributeError:
    return out
  
  pattern = re.compile(option)
  for topic in _options:
    for o in _options[topic]:
      if pattern.match(o):
        out = o
        break
  return out

def get_keyword_if_keyword_is_option(keyword):
  keyword = keyword.lower()
  pattern = re.compile(keyword)
  out = None
  for topic in _options:
    print(topic, keyword)
    print(_options[topic].keys())
    found = False
    if keyword in _options[topic]:
      found = True
      out = topic
    else:
      for opt in _options[topic]:
        if pattern.match(opt):
          found = True
          out = topic
    if found:
      break
  return out
      
def lookup(keyword, option=None):
  canonical_key = get_canonical_key(keyword)
  canonical_option = get_canonical_option(option)
  
  if not option and not canonical_key:
    skipped_option = get_canonical_option(keyword)
    skipped_key = get_keyword_if_keyword_is_option(keyword)
  else:
    skipped_key = skipped_option = None
  
  if canonical_key and not canonical_option:
    path = _help_messages[canonical_key]
  elif canonical_key and canonical_option:
    path = _options[canonical_key][canonical_option]
  elif skipped_key and skipped_option:
    path = _options[skipped_key][skipped_option]
  else:
    path = _help_messages['topics']
  
  with open(path, 'r') as f:
    text = f.read()
  return text

