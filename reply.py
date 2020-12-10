import traceback
from lark import ParseError, LexError, GrammarError
from lark.exceptions import UnexpectedEOF
from lark import UnexpectedToken, UnexpectedCharacters, UnexpectedInput
from dicelang.exceptions import DicelangError
from commands import Response
import helptext

helptable = helptext.HelpText()

def _fold(names):
  return '  '.join(names)

def dice_reply(interpreter, author, server, argument):
  context_size = max(15, len(argument) // 10)
  is_error = True
  printout = ''
  try:
    evaluated, printout = interpreter.execute(argument, author.id, server.id)
    is_error = False
  except (UnexpectedCharacters, UnexpectedToken, UnexpectedInput) as e:
    evaluated = 'Syntax error:\n' + e.get_context(argument, context_size)
  except UnexpectedEOF as e:
    evaluated = str(e).split('.')[0] + '.'
  except (ParseError, LexError) as e:
    evaluated = f'{e.__class__.__name__}: {e!s}'
  except NameError as e:
    evaluated = f'(Interpreter Error) Missing internal identifier: {e!s}'
    traceback.print_tb(e.__traceback__)
  except DicelangError as e:
    printout = interpreter.get_print_queue_on_error(author.id)
    evaluated = f'{e.__class__.__name__}: {e.msg}'
  except Exception as e:
    printout = interpreter.get_print_queue_on_error(author.id)
    evaluated = f'{e.__class__.__name__}: {e!s}'
    traceback.print_tb(e.__traceback__)
  
  user = author.display_name
  if is_error:
    if not printout:
      msg = f'{user} received error:\n```diff\n{evaluated}```'
    else:
      msg = f'{user} received error:\n```{printout}```\n```{evaluated}```'
  else:
    if not printout:
      msg = f'{user} received:\n```diff\n{evaluated}```'
    else:
      msg = f'{user} received:\n```{printout}```\n```diff\n{evaluated}```'
  return (msg, evaluated, printout)
  
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
  po = ''
  response = result.rtype
  argument = result.value.strip()
  if result.other:
    option = result.other.strip()
  else:
    option = None
  
  if response in (Response.ERROR, Response.NONE):
    reply = ''
  
  elif response == Response.DICE:
    reply, raw_reply, po = dice_reply(interpreter, author, channel, argument)
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
    options = map(lambda s: f'  {s}', ['my', 'our', 'global', 'all', 'core'])
    optstring = '\n'.join(options)
    reply = f'Options for `+view`:\n```{optstring}```'
  
  elif response == Response.HELP_HELP:
    help_string1 = helptable.lookup('help', None)
    help_string2 = helptable.lookup('topics', None)
    reply = f'{help_string1}{help_string2}'
  
  elif response == Response.HELP_KEYWORD:
    help_string = helptable.lookup(argument, option)
    raw_reply = help_string
    optstring = (' ' + option) if option else ''
    reply = f'Help for `{argument}{optstring}`:\n{help_string}'
  return (reply, raw_reply, po)

 
