import traceback
from lark import ParseError, LexError, GrammarError
from lark.exceptions import UnexpectedEOF
from lark import UnexpectedToken, UnexpectedCharacters, UnexpectedInput
from commands import Response
import helptext

def _fold(names):
  return '  '.join(names)

def dice_reply(interpreter, author, server, argument):
  context_size = max(15, len(argument) // 10)
  is_error = True
  try:
    evaluated = interpreter.execute(argument, author.id, server.id)
    is_error = False
  except (UnexpectedCharacters, UnexpectedToken, UnexpectedInput) as e:
    evaluated = e.get_context(argument, context_size)
  except UnexpectedEOF as e:
    evaluated = str(e).split('.')[0] + '.'
  except (ParseError, LexError) as e:
    evaluated = f'{e.__class__.__name__}: {e!s}'
  except IndexError:
    raise
  except Exception as e:
    evaluated = f'(Dicelang error) {e.__class__.__name__}: {e!s}'
    traceback.print_tb(e.__traceback__)
  
  if is_error:
    fmt = '{user} received error:\n```{value}```'
  else:
    fmt = '{user} rolled:\n```diff\n{value}```'
  return (fmt.format(user=author.display_name, value=evaluated), evaluated)
  
def view_globals_reply(lang, user):
  names = _fold(lang.keys('global'))
  body = f'```Variables:\n  GLOBALS:\n    {names}```'
  head = f'{user.display_name} requested to view:\n'
  return head + body

def view_all_reply(lang, user, channel):
  cores = _fold(lang.keys('core'))
  pubs  = _fold(lang.keys('global'))
  servs = _fold(lang.keys('server', channel.id))
  privs = _fold(lang.keys('private', user.id))
  joinables = [ ]
  joinables.append(f'Variables:\n  GLOBALS:\n    {pubs}')
  joinables.append(f'  CORE:\n    {cores}')
  joinables.append(f'  SHAREDS:\n    {servs}')
  joinables.append(f'  PRIVATES:\n    {privs}')
  joined = '\n'.join(joinables)
  body = f'```{joined}```'
  head = f'{user.display_name} requested to view:\n'
  return head + body

def view_shareds_reply(lang, user, channel):
  names = _fold(lang.keys('server', channel.id))
  body = f'```Variables:\n  SHAREDS:\n    {names}```'
  head = f'{user.display_name} requested to view:\n'
  return head + body

def view_privates_reply(lang, user):
  names = _fold(lang.keys('private', user.id))
  body = f'```Variables:\n  PRIVATES:\n    {names}```'
  head = f'{user.display_name} requested to view:\n'
  return head + body

def view_core_reply(lang, user):
  names = _fold(lang.keys('core'))
  body = f'```Variables:\n  CORE:\n    {names}```'
  head = f'{user.display_name} requested to view:\n'
  return head + body

def build(interpreter, author, channel, result):
  raw_reply = ''
  response = result.rtype
  argument = result.value.strip()
  if result.other:
    option = result.other.strip()
  else:
    option = None
  
  if response in (Response.ERROR, Response.NONE):
    reply = ''
  
  elif response == Response.DICE:
    reply, raw_reply = dice_reply(interpreter, author, channel, argument)
  elif response == Response.DICE_HELP:
    reply = '[dice help message unimplemented]'
  
  elif response == Response.VIEW_GLOBALS:
    reply = view_globals_reply(interpreter, author)
  
  elif response == Response.VIEW_SHAREDS:
    reply = view_shareds_reply(interpreter, author, channel)
  
  elif response == Response.VIEW_PRIVATES:
    reply = view_privates_reply(interpreter, author)
  
  elif response == Response.VIEW_CORE:
    reply = view_core_reply(interpreter, author)
  
  elif response == Response.VIEW_ALL:
    reply = view_all_reply(interpreter, author, channel)
  
  elif response == Response.VIEW_HELP:
    options = ['my vars', 'our vars', 'global vars', 'all vars', 'core vars']
    optstring = '   '.join(options)
    reply = f'Options for `+view`:\n```{optstring}```'
  
  elif response == Response.HELP_HELP:
    topics = '  '.join(helptext.topics)
    reply = f'Topic keywords:\n```{topics}```\nEnter `+help <topic>` for more info.'
  
  elif response == Response.HELP_KEYWORD:
    help_string = helptext.lookup(argument, option)
    reply = f'Help for `{argument}`:\n{help_string}'
  
  return (reply, raw_reply)

 
