import re
import os
HELP_PATH = 'helpfiles/'

def build_help_table():
  table = { }
  options = { }
  for help_file_path in os.listdir(HELP_PATH):
    if hf.endswith('.md'):
      key = help_file_path.split(os.sep)[-1].rstrip('.md')
      table[key] = help_file_path
    else:
      option_key = help_file_path.split(os.sep)[-1]
      options[option_key] = { }
      for option_file_path in os.listdir(os.path.join(HELP_PATH, option_key)):
        key = option_file_path.split(os.sep)[-1].rstrip('.md')
        options[option_key][key] = option_file_path
  return table, options

_help_messages, _options = build_help_table()

topics = sorted(list(_help_messages.keys()) + ['topics'])

_help_messages['topics'] = '  '.join(topics)

def get_canonical_key(keyword):
  keyword = keyword.lower()
  if keyword not in _help_messages:
    pattern = re.compile(keyword)
    found = False
    for key in _help_messages:
      match = pattern.match(keyword)
      if match:
        keyword = key
        found = True
        break
    if not found:
      keyword = None
  return keyword

def keyword_if_an_option(keyword):
  keyword = keyword.lower()
  pattern = re.compile(keyword)
  out = None
  for topic in _options:
    if keyword not in _options[topic]:
      found = False
      for option in _options[topic]:
        if pattern.match(option):
          out = topic
          found = True
          break
  return out
      
def lookup(keyword, option=None):
  canonical_key = get_canonical_key(keyword)
  keyword_if_option = keyword_if_an_option(keyword)
  path = ''
  if canonical_key and not keyword_if_an_option:
    path = _help_messages[canonical_key]
  elif keyword_if_an_option and not canonical_key:
    path = _options[keyword_if_an_option][keyword]
  elif option is not None:
    path = _options[canonical_key][option]
  else:
    path = _help_messages['topics']
  
  with open(path, 'r') as f:
    text = f.read()
  return text

