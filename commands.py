import re
import enum
import lark
from lark import UnexpectedToken, UnexpectedCharacters, UnexpectedInput

class Result(object):
  def __init__(self, response_type, value='', other=''):
    self.rtype = response_type
    self.value = value
    self.other = other

class Response(enum.Enum):
  ERROR            = -1
  NONE             =  0
  DICE             =  1
  DICE_HELP        =  2
  VIEW_GLOBALS     =  3
  VIEW_SHAREDS     =  4
  VIEW_PRIVATES    =  5
  VIEW_ALL         =  6
  VIEW_HELP        =  7
  HELP_HELP        =  8
  HELP_KEYWORD     =  9


class CmdParser(object):
  grammar = r'''
    start: "+" ("atropos")? command
    command: roll -> command_roll
           | view -> command_view
           | help -> command_help
    
    roll: "roll" /(.|\n)+/  -> roll_code
        | "roll"          -> roll_help
    
    view: "view"    "all"   ("vars")?               -> view_all
        | "view" (( "global" "vars") | "globals"  ) -> view_public
        | "view" (( "our"    "vars") | "shareds"  ) -> view_shared
        | "view" (( "my"     "vars") | "privates" ) -> view_private
        | "view"                                    -> view_help
    
    help: "help" (/[A-Za-z0-9_]+/)+ -> help_topic
        | "help"                     -> help_help
    
    %import common.WS
    %ignore WS
  '''
  
  def __init__(self):
    self.parser = lark.Lark(
      CmdParser.grammar,
      start='start',
      parser='earley',
      lexer='dynamic_complete')
    
  def _parse(self, message_text):
    try:
      out = self.parser.parse(message_text)
      error = False
    except (UnexpectedCharacters, UnexpectedToken, UnexpectedInput) as e:
      out = e.get_context(message_text, 20)
      error = True
    except Exception as e:
      out = e
      error = True
    return {'error' : error, 'output' : out}
  
  def response_to(self, discord_message):
    parser_result = self._parse(discord_message.content)
    if parser_result['error']:
      result = Result(Response.ERROR, parser_result['output'])
    else:
      result = self._handle(parser_result['output'])
    return result    
    
  def _handle(self, tree):
    if tree.data == 'start':
      out = self._handle(tree.children[0])
    elif tree.data == 'command_roll':
      out = self._handle(tree.children[0])
    elif tree.data == 'command_view':
      out = self._handle(tree.children[0])
    elif tree.data == 'command_help':
      out = self._handle(tree.children[0])
    elif tree.data == 'roll_code':
      out = Result(Response.DICE, tree.children[0].value)
    elif tree.data == 'roll_help':
      out = Result(Response.DICE_HELP)
    elif tree.data == 'view_all':
      out = Result(Response.VIEW_ALL)
    elif tree.data == 'view_public':
      out = Result(Response.VIEW_GLOBALS)
    elif tree.data == 'view_shared':
      out = Result(Response.VIEW_SHAREDS)
    elif tree.data == 'view_private':
      out = Result(Response.VIEW_PRIVATES)
    elif tree.data == 'view_help':
      out = Result(Response.VIEW_HELP)
    elif tree.data == 'help_help':
      out = Result(Response.HELP_HELP)
    elif tree.data == 'help_topic':
      option = tree.children[1].value if len(tree.children) > 1 else ''
      out = Result(Response.HELP_KEYWORD, tree.children[0].value, option)
    else:
      out = Result(Response.ERROR, f'UNIMPLEMENTED: {tree.data}')
    return out


