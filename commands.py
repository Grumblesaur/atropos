import re
import enum

class ResponseType(enum.Enum):
  NONE = 0
  DICE = 1

def scan(message_text):
  prefix = re.match('(\+roll|\+atropos[ \t]+\+roll)', message_text)
  if prefix:
    command = message_text.remove(prefix.group(0))
  else:
    command = ''
  response = ResponseType.NONE if not command else ResponseType.DICE
  return (response, command)


