import traceback
from lark import ParseError, LexError, GrammarError
from lark.exceptions import UnexpectedEOF
from lark import UnexpectedToken, UnexpectedCharacters, UnexpectedInput
from commands import Response
import helptext

def _fold(names):
  return '  '.join(sorted(names))

def dice_reply(interpreter, author, channel, argument):
  context_size = max(15, len(argument) // 10)
  is_error = True
  try:
    evaluated = interpreter.execute(argument, author.id, channel.id)
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
  return fmt.format(user=author.display_name, value=evaluated)
  
def view_globals_reply(lang, user):
  names = _fold(lang.datastore.public.variables.keys())
  body = f'```Variables:\n  GLOBALS:\n    {names}```'
  head = f'{user.display_name} requested to view:\n'
  return head + body

def view_all_reply(lang, user, channel):
  pubs  = lang.datastore.public.variables.keys()
  try:
    servs = lang.datastore.server.variables[channel.id].keys()
  except KeyError:
    servs = [ ]
  try:
    privs = lang.datastore.private.variables[user.id].keys()
  except KeyError:
    privs = [ ]
  pubnames, servnames, privnames = map(_fold, (pubs, servs, privs))
  joinables = [ ]
  joinables.append(f'Variables:\n  GLOBALS:\n    {pubnames}')
  joinables.append(f'  SHAREDS:\n    {servnames}')
  joinables.append(f'  PRIVATES:\n    {privnames}')
  joined = '\n'.join(joinables)
  body = f'```{joined}```'
  head = f'{user.display_name} requested to view:\n'
  return head + body

def view_shareds_reply(lang, user, channel):
  try:
    names = _fold(lang.datastore.server.variables[channel.id].keys())
  except KeyError:
    names =''
  body = f'```Variables:\n  SHAREDS:\n    {names}```'
  head = f'{user.display_name} requested to view:\n'
  return head + body

def view_privates_reply(lang, user):
  try:
    names = _fold(lang.datastore.private.variables[user.id].keys())
  except KeyError:
    names = ''
  body = f'```Variables:\n  PRIVATES:\n    {names}```'
  head = f'{user.display_name} requested to view:\n'
  return head + body

def build(interpreter, author, channel, result):
  response = result.rtype
  argument = result.value.strip()
  
  if response in (Response.ERROR, Response.NONE):
    reply = ''
  
  elif response == Response.DICE:
    reply = dice_reply(interpreter, author, channel, argument)
  elif response == Response.DICE_HELP:
    reply = '[dice help message unimplemented]'
  
  elif response == Response.VIEW_GLOBALS:
    reply = view_globals_reply(interpreter, author)
  
  elif response == Response.VIEW_SHAREDS:
    reply = view_shareds_reply(interpreter, author, channel)
  
  elif response == Response.VIEW_PRIVATES:
    reply = view_privates_reply(interpreter, author)
  
  elif response == Response.VIEW_ALL:
    reply = view_all_reply(interpreter, author, channel)
  
  elif response == Response.VIEW_HELP:
    options = ['my vars', 'our vars', 'global vars', 'all vars']
    optstring = '   '.join(options)
    reply = f'Options for `+view`:\n```{optstring}```'
  
  elif response == Response.HELP_HELP:
    topics = '  '.join(helptext.topics)
    reply = f'Topic keywords:\n```{topics}```\nEnter `+help <topic>` for more info.'
  
  elif response == Response.HELP_KEYWORD:
    help_string = helptext.lookup(argument)
    reply = f'Help for `{argument}`:\n{help_string}'
  
  return reply

 
