import re
import enum

class ResponseType(enum.Enum):
  NONE = 0
  DICE = 1

def scan(message_text):
  roll = re.match('(\+roll|\+atropos[ \t]+roll)', message_text)
  if roll:
    command = message_text.replace(roll.group(0),'')
  else:
    command = ''
  response = ResponseType.NONE if not command else ResponseType.DICE
  return (response, command)


