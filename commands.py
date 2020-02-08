import re
import enum

class ResponseType(enum.Enum):
  NONE          = 0
  DICE          = 1
  VIEW_GLOBALS  = 2
  VIEW_SHAREDS  = 3
  VIEW_PRIVATES = 4
  VIEW_ALL      = 5

def scan(message_text):
  roll = re.match('(\+roll|\+atropos[ \t]+roll)', message_text)
  view = re.match('(\+view|\+atropos[ \t]+view)', message_text)
  if roll:
    command = message_text.replace(roll.group(0),'')
    response = ResponseType.DICE
  elif view:
    command = message_text.replace(view.group(0),'')
    all_      = bool(re.search('all([ \t]+vars)?', command))
    globals_  = bool(re.search('(global(s)?|(global[ \t]+)?vars)', command))
    shareds_  = bool(re.search('(shared(s)?|our[ \t]+vars)', command))
    privates_ = bool(re.search('(private(s)?|my[ \t]+vars)', command))
    response = ResponseType.VIEW_ALL
    if privates_:
      response = ResponseType.VIEW_PRIVATES
    elif shareds_:
      response = ResponseType.VIEW_SHAREDS
    elif globals_:
      response = ResponseType.VIEW_GLOBALS
  else:
    command = ''
    response = ResponseType.NONE
  return (response, command)


