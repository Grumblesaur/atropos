from lark import ParseError, LexError, GrammarError
from lark.exceptions import UnexpectedEOF
from lark import UnexpectedToken, UnexpectedCharacters, UnexpectedInput
from commands import ResponseType

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
  
def handle_view_command(lang, response_type, userid, serverid):
  global_names = shared_names = private_names = [ ]
  if response_type == ResponseType.VIEW_ALL:
    global_names  = lang.datastore.public.keys()
    shared_names  = lang.datastore.server[server_id].keys()
    private_names = lang.datastore.private[user_id].keys()
  elif response_type == ResponseType.VIEW_GLOBALS:
    global_names  = lang.datastore.public.keys()
  elif response_type == ResponseType.VIEW_SHAREDS:
    shared_names = lang.datastore.server[server_id].keys()
  elif response_type == ResponseType.VIEW_PRIVATES:
    private_names = lang.datastore.private[user_id].keys()
  
  global_text = '  '.join(sorted(global_names))
  shared_text = '  '.join(sorted(shared_names))
  private_text = '  '.join(sorted(private_names))
  
  output = ''
  if global_text:
    output += " GLOBALS:\n   {}".format(global_text)
  if shared_text:
    output += " SHAREDS:\n   {}".format(shared_text)
  if private_text:
    output += " SHAREDS:\n   {}".format(private_text)
  return output

