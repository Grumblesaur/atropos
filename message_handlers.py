from lark import ParseError, LexError, GrammarError
from lark.exceptions import UnexpectedEOF
from lark import UnexpectedToken, UnexpectedCharacters, UnexpectedInput

class Result(object):
  def __init__(self, is_error, value):
    self.value    = value
    self.is_error = is_error
  
  def __bool__(self):
    return not self.is_error

def handle_dicelang_command(lang, command, user_id, username, server_id):
  is_error = True
  try:
    value = lang.execute(command, user_id, server_id)
    is_error = False
  except (UnexpectedCharacters, UnexpectedToken, UnexpectedInput) as e:
    value = e.get_context(command, 5)
  except UnexpectedEOF as e:
    value = str(e).split('.')[0] + '.'
  except (ParseError, LexError, GrammarError) as e:
    value = '{}: {}'.format(e.__class__.__name__, e)
  except Exception as e:
    value = '(Non-Lark error){}: {}'.format(e.__class__.__name__, e)
  return Result(is_error, value)
  



