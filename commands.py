import re
import enum
import traceback
import lark
import discord
from lark import UnexpectedToken
from lark import UnexpectedCharacters
from lark import UnexpectedInput
from lark import ParseError
from lark import LexError
from lark.exceptions import UnexpectedEOF

import helptext
from dicelang import interpreter
from dicelang.exceptions import DicelangError
from result_file import ResultFile

syntax = r'''
  start: "+" ("atropos")? command
  command: roll -> command_roll
         | view -> command_view
         | help -> command_help
  
  roll: "old" /(.|\n)+/  -> roll_code
      | "roll" /(.|\n)+/ -> roll_lit
      | "roll"            -> roll_help
  
  view: "view"    "all"   ("vars")?                  -> view_all
      | "view" (( "global" ("vars")?) | "globals"  ) -> view_public
      | "view" (( "our"    ("vars")?) | "shareds"  ) -> view_shared
      | "view" (( "my"     ("vars")?) | "privates" ) -> view_private
      | "view" (( "core"   ("vars")?) | "library"  ) -> view_core
      | "view" (( "builtin"("vars")?) | "builtins" ) -> view_builtins
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
  view_builtins = 'view_builtins'
  help_topic = 'help_topic'
  help_help = 'help_help'
  
  pass_by = ['start', 'command_roll', 'command_view', 'command_help']
  views = [
    view_public, view_private,
    view_core,   view_shared,
    view_help,   view_all,
    view_builtins,
  ]
  
  no_args = views + [help_help] + [roll_help]
  rolls = [roll_code, roll_lit]
  helps = [help_help, help_topic]
  
  all_rolls = [roll_code, roll_lit, roll_help]
  

class Builder(object):
  def __init__(self, dicelang_interpreter, helptext_engine):
    # Use dependency injection here because we want references to these shared
    # objects, which are held elsewhere as they may someday be used elsewhere.
    self.dicelang = dicelang_interpreter
    self.helptable = helptext_engine
  
  def get_server_id(self, msg):
    is_dm = isinstance(msg.channel, (discord.GroupChannel, discord.DMChannel))
    return msg.channel.id if is_dm else msg.channel.guild.id
  
  def view_reply(self, command_type, msg):
    server_id = self.get_server_id(msg)
    user_id = msg.author.id
    cores, pubs, servs, privs, builtins = ('',) * 5
    sep = '  '
    if command_type in (CommandType.view_public, CommandType.view_all):
      pubs = sep.join(self.dicelang.keys('global'))
    if command_type in (CommandType.view_shared, CommandType.view_all):
      servs = sep.join(self.dicelang.keys('server', server_id))
    if command_type in (CommandType.view_private, CommandType.view_all):
      privs = sep.join(self.dicelang.keys('private', user_id))
    if command_type in (CommandType.view_core, CommandType.view_all):
      cores = sep.join(self.dicelang.keys('core'))
    if command_type in (CommandType.view_builtins, CommandType.view_all):
      builtins = sep.join(self.dicelang.builtin_keys())
    
    if command_type == CommandType.view_help:
      viewtypes = ['all', 'builtin', 'core', 'global', 'my', 'our']
      return {
        'action': 'Possible options',
        'result': '\n'.join(map(lambda s:f'  {s}', viewtypes)),
        'help' : True,
      }
    
    content = 'Variables:\n'
    if builtins:
      content += f'  BUILTINS:\n    {builtins}\n'
    if cores:
      content += f'  CORE:\n    {cores}\n'
    if pubs:
      content += f'  GLOBALS:\n    {pubs}\n'
    if servs:
      content += f'  SHAREDS:\n    {servs}\n'
    if privs:
      content += f'  PRIVATES:\n    {privs}'
    
    action = f'{msg.author.display_name} requested to view:\n'
    result = content
    return {'action' : action, 'result' : result, 'help' : False}
      
  
  def dice_reply(self, code, msg):
    server_id = self.get_server_id(msg)
    act, res = '', ''
    error = True
    try:
      res, act = self.dicelang.execute(code, msg.author.id, server_id)
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
      act = self.dicelang.get_print_queue_on_error(msg.author.id)
      classname = e.__class__.__name__
      try:
        res = f'{classname}: {e.msg}'
      except AttributeError:
        res = f'{classname}: {e.args[0]!s}'
    except Exception as e:
      act = self.dicelang.get_print_queue_on_error(msg.author.id)
      res = f'{e.__class__.__name__}: {e!s}'
      traceback.print_tb(e.__traceback__)
    else:
      error = False
    return {'action': act, 'result': res, 'error': error}

  def help_reply(self, argument, option, meta=False):
    reply_data = { }
    if meta:
      reply_data['action'] = 'Possible topics'
      reply_data['result'] = ''.join([
        self.helptable.lookup('help', None),
        self.helptable.lookup('topics', None)
      ])
    else:
      optstring = f' {option}' * bool(option)
      reply_data['action'] = f'Help for `{argument}{optstring}`'
      reply_data['result'] = self.helptable.lookup(argument, option)
    return reply_data


class Command(object):
  pkw = {'start':'start', 'parser':'earley', 'lexer':'dynamic_complete'}
  parser = lark.Lark(syntax, **pkw)
  builder = Builder(interpreter.Interpreter(), helptext.HelpText())
  
  def __init__(self, message):
    parser_output = self.parse(message.content)
    if parser_output['error']:
      self.type = CommandType.error
      self.kwargs = {}
    else:
      self.type, self.kwargs = self.visit(parser_output['tree'])
    self.originator = message
    self.stashed = None
  
  def __repr__(self):
    return f'{self.__class__.__name__}<{self.type}:{self.kwargs!r}>'
  
  def __bool__(self):
    '''Invalid commands evaluate False, otherwise True.'''
    return self.type != CommandType.error
  
  def get_client_alias(self, client):
    '''Retrives the client's display name for the channel whence the message
    originated.'''
    try:
      for user in self.originator.channel.members:
        if user.id == client.user.id:
          return user.display_name
    except AttributeError:
      pass
    return 'Atropos'
    
  def parse(self, message_text):
    '''Parses the text to decide whether it is a valid command.'''
    try:
      tree_or_error = self.__class__.parser.parse(message_text)
    except (UnexpectedCharacters, UnexpectedToken, UnexpectedInput) as e:
      tree_or_error = e.get_context(message_text, 20)
      error = True
    except Exception as e:
      tree_or_error = e
      error = True
    else:
      error = False
    return {'error' : error, 'tree' : tree_or_error}

  def visit(self, tree):
    '''Retrieves the command's parameters from the parse tree.'''
    if tree.data in CommandType.pass_by:
      out = self.visit(tree.children[0])
    elif tree.data in CommandType.no_args:
      out = tree.data, {}
    elif tree.data == CommandType.roll_code:
      out = tree.data, {'value': tree.children[0].value}
    elif tree.data == CommandType.roll_lit:
      out = tree.data, {'value': tree.children[0].value, 'option': 'literate'}
    elif tree.data == CommandType.help_topic:
      option = tree.children[1].value if len(tree.children) > 1 else ''
      out = tree.data, {'value': tree.children[0].value, 'option': option}
    else:
      out = tree.data, {'value': f'UNIMPLEMENTED: {tree.data}'}
    return out

  async def send_reply_as(self, client):
    '''Called from the bot's event handlers. Accepts the object representing
    the bot's client instance, and sends a reply to the correctly-parsed
    command as that client for the particular server and channel where the
    message originated from. If this command instance is invalid, this
    operation is a no-op.'''
    if not self:
      return
    async with self.originator.channel.typing():
      reply = await self.reply(client)
    await self.send(reply)
  
  async def send(self, reply, retry=True):
    '''Directly handles sending the message, changing the message to a file
    attachment if it exceeds Discord's maximum size.'''
    msg = self.originator
    username = msg.author.display_name
    try:
      await msg.channel.send(**reply)
    except discord.errors.HTTPException as e:
      print(e)
      if e.code == 50035: # Message too long
        if retry: # Retry middling-sized messages as standard messages.
          if self.type in CommandType.all_rolls:
            noun = 'Roll'
          elif self.type in CommandType.helps:
            noun = 'Help'
          elif self.type in CommandType.views:
            noun = 'View'
          else:
            noun = 'Command'
          title = f'{noun} result for {username} (too large for embed):'
          bare = self.type in CommandType.helps
          new_reply = self.pack_content(title, bare=bare, **self.stashed)
          await self.send(new_reply, retry=False)
        else: # If retry failed, attach as file.
          args = (self.stashed.get('result'), self.stashed.get('action', ''))
          await self.attach_as_file(*args)
  
  async def attach_as_file(self, content, extra):
    msg = self.originator
    username = msg.author.display_name
    note = f"The response to `{username}`'s request was too large, "
    note += "so I've uploaded it as a file instead:"
    with ResultFile(content, username, extra) as rf:
      await msg.channel.send(content=note, file=rf)
  
  def pack_embed(self, client, title, description, **kwargs):
    '''Helper method for building embed-style replies.'''
    embed = discord.Embed(
      title=title,
      description=description,
      color=self.originator.author.color)
    action = kwargs.get('action', None)
    result = kwargs.get('result', 'Something went wrong.')
    bare = kwargs.get('bare', False)
    action_value = action if bare else f'```{action}```'
    result_value = result if bare else f'```{result}```'
    if action:
      embed.add_field(name='Action', value=action_value, inline=False)
    embed.add_field(name='Result', value=result_value, inline=False)
    embed.set_author(name=self.get_client_alias(client))
    return {'embed' : embed}
  
  def pack_content(self, header, **kwargs):
    '''Helper method for building message-style replies.'''
    action = kwargs.get('action', None)
    result = kwargs.get('result')
    bare = kwargs.get('bare', False)
    content = header
    if action:
      if bare:
        content += f'\n{action}'
      else:
        content += f'\n```{action}```'
    if bare:
      content += f'\n{result}'
    else:
      content += f'\n```{result}```'
    return {'content' : content}
  
  async def reply(self, client):
    '''Construct a reply for the type of command we are.'''
    username = self.originator.author.display_name
    if self.type == CommandType.roll_code:
      self.stashed = Command.builder.dice_reply(
        self.kwargs['value'],
        self.originator)
      
      error = self.stashed['error'] * ' error'
      header = f'{username} received{error}:'
      reply = self.pack_content(header, **self.stashed)
    
    elif self.type == CommandType.roll_lit:
      self.stashed = Command.builder.dice_reply(
        self.kwargs['value'],
        self.originator)
      
      titletype = 'Error' if self.stashed['error'] else 'Roll'
      title = f'{titletype} result for {username}'
      desc = f'```{self.originator.content}```'
      reply = self.pack_embed(client, title, desc, **self.stashed)
    
    elif self.type == CommandType.roll_help:
      reply = {'content' : 'See `+atropos help quickstart` for more info.'}
    
    elif self.type in CommandType.views:
      self.stashed = Command.builder.view_reply(self.type, self.originator)
      noun = 'help' if self.stashed['help'] else 'view'
      title = f'Database {noun} for {username}'
      desc = f'```{self.originator.content}```'
      reply = self.pack_embed(client, title, desc, **self.stashed)
    
    elif self.type in CommandType.helps:
      self.stashed = Command.builder.help_reply(
        self.kwargs.get('value', None),
        self.kwargs.get('option', None),
        self.type == CommandType.help_help)
      title = f'Help for {username}'
      desc = f'```{self.originator.content}```'
      reply = self.pack_embed(client, title, desc, bare=True, **self.stashed)
    else:
      reply = {'content': f'Unimplemented reply: {self.type} (This is a bug.)'}
      print(reply)
    
    return reply      
    

