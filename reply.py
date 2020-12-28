import traceback
from lark import ParseError, LexError, GrammarError
from lark.exceptions import UnexpectedEOF
from lark import UnexpectedToken, UnexpectedCharacters, UnexpectedInput
from dicelang.exceptions import DicelangError
from commands import Response

import discord
import helptext

helptable = helptext.HelpText()

def _fold(names):
  return '  '.join(names)

def dice_execute(code, author_id, server_id):
  printout = ''
  evaluated = ''
  is_error = True
  context_size = max(15, len(argument) // 10)
  try:
    evaluated, printout = interpreter.execute(argument, author_id, server_id)
    is_error = False
  except (UnexpectedCharacters, UnexpectedToken, UnexpectedInput) as e:
    evaluated = 'Syntax error:\n' + e.get_context(code, context_size)
  except UnexpectedEOF as e:
    evaluated = str(e).split('.')[0] + '.'
  except (ParseError, LexError) as e:
    evaluated = f'{e.__class__.__name__}: {e!s}'
  except NameError as e:
    evaluated = f'(Interpreter Error) Missing internal identifier: {e!s}'
    traceback.print_tb(e.__traceback__)
  except DicelangError as e:
    printout = interpreter.get_print_queue_on_error(author_id)
    classname = e.__class__.__name__
    try:
      evaluated = f'{classname}: {e.msg}'
    except AttributeError:
      evaluated = f'{classname}: {e.args[0]!s}'
  except Exception as e:
    printout = interpreter.get_print_queue_on_error(author_id)
    evaluated = f'{e.__class__.__name__}: {e!s}'
    traceback.print_tb(e.__traceback__)
  return evaluated, printout, is_error

def dice_reply_literate(interpreter, author, server, argument):
  value, printout, is_error = dice_execute(interpreter, author.id, server.id)
  user = author.display_name
  kw = {
    'title' : f'Roll result for {user}',
    'description' : f'```{argument}```',
    'color' : author.color,
  }
  embed = discord.Embed(**kw)
  if printout:
    embed.add_field(name='Action', value=printout, inline=False)
  embed.add_field(name='Result', value=value, inline=False)
  return embed, value, printout
  
def dice_reply(interpreter, author, server, argument):
  value, printout, is_error = dice_execute(interpreter, author.id, server.id)
  user = author.display_name
  error = is_error * ' error'
  if not printout:
    msg = f'{user} received{error}:\n```diff\n{value}```'
  else:
    msg = f'{user} received{error}:\n```{printout}```\n```{value}```'
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
  reply = ''
  raw_reply = ''
  po = ''
  response = result.rtype
  argument = result.value.strip()
  if result.other:
    option = result.other.strip()
  else:
    option = None
  
  if response == Response.DICE:
    args = (interpreter, author, channel, argument)
    if option == 'literate':
      reply, raw_reply, po = dice_reply_literate(*args)
    else:
      reply, raw_reply, po = dice_reply(*args)
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

 
