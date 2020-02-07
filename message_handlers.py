from lark import ParseError, LexError, GrammarError
from lark import UnexpectedToken, UnexpectedCharacters

class Result(object):
  def __init__(self, is_error, value):
    self.value    = value
    self.is_error = is_error
  
  def __bool__(self):
    return not is_error

def handle_dicelang_command(command, user_id, username, server_id):
  is_error = True
  try:
    value = interpreter.execute(command, user_id, server_id)
    is_error = False
  except (UnexpectedCharacters, UnexpectedToken) as e:
    value = e.get_context(command, 5)
  except (ParseError, LexError, GrammarError) as e:
    value = e.get_context(command, 5)
  except Exception as e:
    value = str(e)
  return Result(is_error, value)
  



