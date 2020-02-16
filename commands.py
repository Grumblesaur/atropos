import re
import enum
import lark
from lark import UnexpectedToken, UnexpectedCharacters, UnexpectedInput

class Result(object):
  def __init__(self, response_type, value=''):
    self.rtype = response_type
    self.value = value

class Response(enum.Enum):
  ERROR            = -1
  NONE             =  0
  DICE             =  1
  DICE_HELP        =  2
  VIEW_GLOBALS     =  3
  VIEW_SHAREDS     =  4
  VIEW_PRIVATES    =  5
  VIEW_ALL         =  6
  HELP_HELP        =  7
  HELP_SOURCE      =  8
  HELP_TYPES       =  9
  HELP_OPERATORS   = 10
  HELP_FUNCTIONS   = 11
  HELP_LIMITATIONS = 12


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
    
    help: "help" /function(s)?/     -> help_functions
        | "help" /operator(s)?/     -> help_operators
        | "help" /type(s)?/         -> help_types
        | "help" /limitation(s)?/   -> help_limitations
        | "help" /source/           -> help_source
        | "help" /topic(s)/         -> help_help
        | "help" (/(.|\n)+/)?       -> help_help
    
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
    elif tree.data == 'help_functions':
      out = Result(Response.HELP_FUNCTIONS)
    elif tree.data == 'help_operators':
      out = Result(Response.HELP_OPERATORS)
    elif tree.data == 'help_types':
      out = Result(Response.HELP_TYPES)
    elif tree.data == 'help_limitations':
      out = Result(Response.HELP_LIMITATIONS)
    elif tree.data == 'help_source':
      out = Result(Response.HELP_SOURCE)
    elif tree.data == 'help_help':
      out = Result(Response.HELP_HELP)
    else:
      out = Result(Response.ERROR, f'UNIMPLEMENTED: {tree.data}')
    return out


