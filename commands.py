import re
import enum

class ResponseType(enum.Enum):
  NONE          = 0
  DICE          = 1
  VIEW_GLOBALS  = 2
  VIEW_SHAREDS  = 3
  VIEW_PRIVATES = 4
  VIEW_ALL      = 5
  HELP          = 6

def scan(message_text):
  pattern = '(\+{kw}|\+atropos[ \t]+{kw}'
  roll  = re.match(pattern.format(kw='roll'), message_text)
  view  = re.match(pattern.format(kw='view'), message_text)
  help_ = re.match(pattern.format(kw='help'), message_text)
  if roll:
    response, command = roll_response(roll, message_text)
  elif view:
    response, command = view_response(view, message_text)
  elif help_:
    response, command = help_response(help_, message_text)
  else:
    command = ''
    response = ResponseType.NONE
  return (response, command)

def roll_response(match_obj, text):
  c = text.replace(match_obj.group(0), '')
  r = ResponseType.DICE
  return (r, c)

def view_response(match_obj, text):
  c = text.replace(match_obj.group(0), '')
  all_ = bool(re.search('all([ \t]+vars)?', c))
  glob = bool(re.search('(global(s)?|global[ \t]+)?vars)', c))
  shar = bool(re.search('shared(s)?|our[ \t]+vars)', c))
  priv = bool(re.search('private(s)?|my [ \t]+vars)', c))
  if all_:
    r = ResponseType.VIEW_ALL
  elif glob:
    r = ResponseType.VIEW_GLOBALS
  elif shar:
    r = ResponseType.VIEW_SHAREDS
  elif priv:
    r = ResponseType.VIEW_PRIVATES
  return (r, c)
  
def help_response(match_obj, text):
  c = text.replace(match_obj.group(0), '')
  r = ResponseType.HELP
  return (r, c)





