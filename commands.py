import re
import enum
import lark
import discord
from lark import UnexpectedToken, UnexpectedCharacters, UnexpectedInput
from dicelang import interpreter
from dicelang.exceptions import DicelangError

command_grammar = r'''
  start: "+" ("atropos")? command
  command: roll -> command_roll
         | view -> command_view
         | help -> command_help
  
  roll: "roll" /(.|\n)+/  -> roll_code
      | "lit" /(.|\n)+/ -> roll_lit
      | "roll"            -> roll_help
  
  view: "view"    "all"   ("vars")?                  -> view_all
      | "view" (( "global" ("vars")?) | "globals"  ) -> view_public
      | "view" (( "our"    ("vars")?) | "shareds"  ) -> view_shared
      | "view" (( "my"     ("vars")?) | "privates" ) -> view_private
      | "view" (( "core"   ("vars")?) | "library"  ) -> view_core
      | "view" (/\w+/)?                              -> view_help
  
  help: "help" /\b\w+\b/+ -> help_topic
      | "help"            -> help_help
  
  %import common.WS
  %ignore WS
'''

class CommandType:
  error = 'error'
  roll_code = 'roll_code'
  roll_lit  = 'roll_lit'
  roll_help = 'roll_help'
  view_all  = 'view_all'
  view_public = 'view_public'
  view_shared = 'view_shared'
  view_private = 'view_private'
  view_core = 'view_core'
  view_help = 'view_help'
  help_topic = 'help_topic'
  help_help = 'help_help'
  
  pass_by = ['start', 'command_roll', 'command_view', 'command_help']
  no_arg = [
    view_public, view_private,
    view_core,   view_shared,
    view_help,   help_help
  ]

class Command(object):
  parser = lark.Lark(
    command_grammar,
    start='start',
    parser='earley',
    lexer='dynamic_complete')
  
  def __init__(self, message):
    data = self.visit(self.__class__.parser(message.text))
    if data['error']:
      self.type = CommandType.error
      self.kwargs = {}
    else:
      self.type, self.kwargs = data['output']
    self.originator = message
  
  def __bool__(self):
    return not self.type == CommandType.error
    
  def parse(self, message):
    try:
      tree_or_error = self.__class__.parser.parse(message.text)
    except (UnexpectedCharacters, UnexpectedToken, UnexpectedInput) as e:
      tree_or_error = e.get_context(message_text, 20)
      error = True
    except Exception as e:
      tree_or_error = e
      error = True
    return {'error' : error, 'output' : tree_or_error}

  def visit(self, tree):
    if tree.data in CommandType.pass_by:
      out = self.visit(tree.children[0])
    elif tree.data in CommandType.no_arg:
      out = tree.data, {}
    elif tree.data == CommandType.roll_code:
      out = tree.data, {'value': tree.children[0].value}
    elif tree.data == CommandType.roll_lit:
      out = tree.data, {'value': tree.children[0].value, 'option': 'literate'}
    elif tree.data == CommandType.help_topic:
      option = tree.children[1].value if len(tree.children) > 1 else ''
      out = tree.data, {'value': tree.children[0].value, 'option': option}
    else:
      out = Result(Response.ERROR, f'UNIMPLEMENTED: {tree.data}')
    return out

  
  async def send_reply_as(self, user):
    if self.type == CommandType.roll_code:
      d = Build.dice_reply(self.kwargs['value'], self.originator)
      action = d['action']
      result = d['result']
      error = d['error'] * ' error'
      c = f'{self.originator.author.display_name} received{error}:\n'
      if d['action']:
        c += f'```{action}```\n'
      c += f'```{result}```'
      reply = {'content' : c}
    elif self.type == CommandType.roll_lit:
      d = Build.dice_reply(self.kwargs['value'], self.originator)
      action = d['action']
      result = d['result']
      error = 'Error' if d['error'] else 'Roll'
      embed_kw = {
        'title' : f'{error} result for {self.originator.author.display_name}',
        'description': f'```{self.originator.text}```',
        'color' : self.originator.author.color,
      }
      embed = discord.Embed(**kw)
      if action:
        embed.add_field(name='Action', value=f'```{action}```', inline=False)
      embed.add_field(name='Result', value=f'```{result}```', inline=False)
      reply = {'embed' : embed}
    elif #TODO: THE REST OF THE CASES
      
      
    
class Build:
  dicelang = interpreter.Interpreter()
  
  @staticmethod
  def get_server_id(msg):
    if isinstance(msg.channel, (discord.GroupChannel, discord.DMChannel)):
      return msg.channel.id
    return msg.channel.guild.id
  
  @staticmethod
  def dice_reply(code, message):
    server_id = Build.get_server_id(message)
    act, res = '', ''
    error = True
    try:
      res, act = Build.dicelang.execute(code, msg.author.id, server_id)
    except (UnexpectedCharacters, UnexpectedToken, UnexpectedInput) as e:
      res = e.get_context(code, max(15, len(code) // 10))
      act = 'Syntax Error'
    except UnexpectedEOF as e:
      res = str(e).split('.')[0] + '.'
      act = 'Unexpected End of Input'
    except (ParseError, LexError) as e:
      res = f'{e!s}'
      act = 'Lexer/Parser Error'
    except NameError as e:
      res = 'Missing internal identifier: {e!s}'
      act = 'Interpreter Error'
      traceback.print_tb(e.__traceback__)
    except DicelangError as e:
      act = Build.dicelang.get_print_queue_on_error(msg.author.id)
      classname = e.__class__.__name__
      try:
        res = f'{classname}: {e.msg}'
      except AttributeError:
        res = f'{classname}: {e.args[0]!s}'
    except Exception as e:
      act = Build.dicelang.get_print_queue_on_error(msg.author.id)
      res = f'{e.__class__.__name__}: {e!s}'
      traceback.print_tb(e.__traceback__)
    else:
      error = False
    return {'action': act, 'result': result, 'error': error}





