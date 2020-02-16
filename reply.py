import traceback
from lark import ParseError, LexError, GrammarError
from lark.exceptions import UnexpectedEOF
from lark import UnexpectedToken, UnexpectedCharacters, UnexpectedInput
from commands import Response

def build(interpreter, author, channel, result):
  response = result.rtype
  argument = result.value.strip()
  
  if response in (Response.ERROR, Response.NONE):
    reply = ''
  
  elif response == Response.DICE:
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
    reply = fmt.format(user=author.display_name, value=evaluated)
  
  elif response == Response.DICE_HELP:
    reply = '[dice help message unimplemented]'
  
  elif response == Response.VIEW_GLOBALS:
    names = interpreter.datastore.public.variables.keys()
    names = sorted(names)
    fmt = '```Variables:\n  GLOBALS:\n    {keys}```'
    reply = fmt.format(keys='  '.join(names))
  
  elif response == Response.VIEW_SHAREDS:
    names = interpreter.datastore.server.variables[channel.id].keys()
    names = sorted(names)
    fmt = '```Variables:\n  SHAREDS:\n    {keys}```'
    reply = fmt.format(keys='  '.join(names))
  
  elif response == Response.VIEW_PRIVATES:
    names = interpreter.datastore.private.variables[author.id].keys()
    names = sorted(names)
    fmt = '```Variables:\n  PRIVATES:\n    {keys}```'
    reply = fmt.format(keys='  '.join(names))
  
  elif response == Response.VIEW_ALL:
    pubs  = interpreter.datastore.public.variables.keys()
    servs = interpreter.datastore.server.variables[channel.id].keys()
    privs = interpreter.datastore.private.variables[author.id].keys()
    fold = lambda keylist: '  '.join(sorted(keylist))
    pubnames, servnames, privnames = map(fold, (pubs, servs, privs))
    joinables = [ ]
    joinables.append('Variables:\n  GLOBALS:\n    {keys}'.format(keys=pubnames))
    joinables.append('  SHAREDS:\n    {keys}'.format(keys=servnames))
    joinables.append('  PRIVATES:\n    {keys}'.format(keys=privnames))
    reply = '```{}```'.format('\n'.join(joinables))
  
  elif response == Response.HELP_HELP:
    help_topics = 'source  types  operators  functions  limitations'
    reply = f'`topics: {help_topics}`\n enter `+help <topic>` for more info.'
  
  elif response == Response.HELP_SOURCE:
    reply = 'View the source code and README here:\n'
    reply += 'https://github.com/Grumblesaur/atropos'
  
  elif response == Response.HELP_TYPES:
    reply = '[types help information unimplemented]'
  
  elif response == Response.HELP_OPERATORS:
    reply = '[operators help information unimplemented]'
  
  elif response == Response.HELP_FUNCTIONS:
    reply = '[functions help information unimplemented]'
  
  elif response == Response.HELP_LIMITATIONS:
    reply = '[limitations help information unimplemented]'
  
  return reply

 
