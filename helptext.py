import os
HELP_PATH = 'helpfiles/'

def build_help_table():
  table = { }
  for help_file in [hf for hf in os.listdir(HELP_PATH) if hf.endswith('.md')]:
    key = help_file.split(os.sep)[-1].rstrip('.md')
    text = f'[{key}.md failed to load]'
    with open(os.path.join(HELP_PATH, help_file), 'r') as f:
      text = f.read()
    table[key] = text
  return table

def build_option_table():
  options = { }
  for directory in [hf for hf in os.listdir(HELP_PATH) if not hf.endswith('.md')]:
    option = directory.split(os.sep)[-1].strip()
    options[option] = {}
    dirpath = os.path.join(HELP_PATH, directory)
    for filename in [hf for hf in os.listdir(dirpath) if hf.endswith('.md')]:
      key = filename.split(os.sep)[-1].rstrip('.md')
      text = f'[{key}.md failed to load]'
      with open(os.path.join(dirpath, filename), 'r') as f:
        text = f.read()
      options[option][key] = text
  return options

_help_messages = build_help_table()
_options       = build_option_table()

topics = sorted(list(_help_messages.keys()) + ['topics'])

_help_messages['topics'] = '  '.join(topics)

_aliases = {
  'function'   : 'functions',
  'fn'         : 'functions',
  'func'       : 'functions',
  'operator'   : 'operators',
  'op'         : 'operators',
  'limit'      : 'limitations',
  'limits'     : 'limitations',
  'limitation' : 'limitations',
  'code'       : 'source',
  'github'     : 'source',
  'topic'      : 'topics',
  'keyword'    : 'topics',
  'keywords'   : 'topics',
}

def get_canonical_key(alias):
  try:
    key = _aliases[alias]
  except KeyError:
    key = alias
  return key

def lookup(keyword, option):
  print('lookup:', keyword, ',', option)
  key = get_canonical_key(keyword)
  if key in _options and option is not None:
    message = _options[key][option]
  elif key in _help_messages:
    message = _help_messages[key]
  else:
    message = _help_messages['topics']
  return message


