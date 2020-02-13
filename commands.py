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
  base_pattern = "(\+(atropos[ \t]+)?{kw})"
  roll_pattern = base_pattern.format(kw='roll')
  view_pattern = base_pattern.format(kw='view')
  help_pattern = base_pattern.format(kw='help')
  roll  = re.match(roll_pattern, message_text)
  view  = re.match(view_pattern, message_text)
  help_ = re.match(help_pattern, message_text)
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
  glob = bool(re.search('(global(s)?([ \t]vars)?)', c))
  shar = bool(re.search('(shared(s)?|our[ \t]+vars)', c))
  priv = bool(re.search('(private(s)?|my[ \t]+vars)', c))
  if all_:
    r = ResponseType.VIEW_ALL
  elif glob:
    r = ResponseType.VIEW_GLOBALS
  elif shar:
    r = ResponseType.VIEW_SHAREDS
  elif priv:
    r = ResponseType.VIEW_PRIVATES
  else:
    r = ResponseType.NONE
  return (r, c)
  
def help_response(match_obj, text):
  c = text.replace(match_obj.group(0), '')
  r = ResponseType.HELP
  return (r, c)





