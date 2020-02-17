_help_messages = {
  'functions'   : '[function help text coming soon]',
  'operators'   : '[operator help text coming soon]',
  'source'      : 'https://github.com/Grumblesaur/atropos',
  'limitations' : '[limitations help text coming soon]',
}

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

def lookup(keyword):
  try:
    key = _aliases[keyword]
  except KeyError:
    key = keyword
  try:
    out = _help_messages[key]
  except KeyError:
    out = _help_messages['topics']
  return out


