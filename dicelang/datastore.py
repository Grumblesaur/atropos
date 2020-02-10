import os
from collections.abc import Iterable

# The following imports are not used by name in this file, but are
# necessary for enabling `eval` to work correctly. Do not let
# PyCharm "optimize" them out.
from dicelang.undefined import Undefined
from dicelang.function  import SyntaxToken
from dicelang.function  import SyntaxTree
from dicelang.function  import Function

class _DataStore(object):
  separator = '?sep?'
  def __init__(self, storage_file_name):
    """Internal class for saving, loading, accessing, and mutating
    standing variables during the use of the chat bot."""
    self.storage_file_name = storage_file_name
    self.variables = {}
    try:
      with open(self.storage_file_name, 'r') as f:
        for line in f:
          k_repr, v_repr = line.strip().split(_DataStore.separator, 1)
          key = eval(k_repr)
          value = eval(v_repr)
          self.variables[key] = value
    except SyntaxError as e:
      print(e)
    except IOError as e:
      with open(self.storage_file_name, 'w') as f:
        pass
    
  def get(self, key, default=Undefined):
    try:
      out = self.variables[key]
    except KeyError:
      out = default
    return out
  
  def put(self, key, value):
    self.variables[key] = value
    return value
  
  def drop(self, key):
    out = self.variables[key]
    del self.variables[key]
    return out
  
  def save(self, filename=None):
    filename = self.storage_file_name if filename is None else filename
    with open(filename, 'w') as f:
      for key, value in self.variables.items():
        f.write('{k}{s}{v}\n'.format(
          k=repr(key),
          s=_DataStore.separator,
          v=repr(value)))
  
class _OwnedDataStore(_DataStore):
  '''Specialization of _DataStore where keys are associated by
  some other key specifying ownership, such as a username or
  server handle.'''
  
  def __init__(self, storage_directory, prefix):
    """Internal class for saving, loading, accessing, and mutating
    standing variables during the use of the chat bot."""
    self.storage_directory = storage_directory
    self.prefix = prefix
    self.variables = {}
    filenames = os.listdir(self.storage_directory)
    filenames = filter(lambda s: s.startswith(self.prefix), filenames)
    builder = lambda fn: '{}{}{}'.format(
      self.storage_directory,
      os.path.sep,
      fn)
    filenames = map(builder, filenames)
    for filename in filenames:
      _, owner = filename.rsplit('_', 1)
      owner = eval(owner)
      self.variables[owner] = { }
      try:
        with open(filename, 'r') as f:
          for line in f:
            k_repr, v_repr = line.strip().split(_DataStore.separator, 1)
            key = eval(k_repr)
            value = eval(v_repr)
            self.variables[owner][key] = value
      except SyntaxError as e:
        print(e)
      except IOError as e:
        with open(filename, 'w') as f:
          pass
      
  def save(self):
    owners = self.variables.keys()
    for owner in owners:
      filename = '{}{}{}_{}'.format(
        self.storage_directory,
        os.path.sep,
        self.prefix,
        owner)
      with open(filename, 'w') as f:
        for key, value in self.variables[owner].items():
          f.write('{k}{s}{v}\n'.format(
            k=repr(key),
            s=_DataStore.separator,
            v=repr(value)))
  
  def get(self, owner_tag, key, default=Undefined):
    try:
      out = self.variables[owner_tag][key]
    except KeyError as e:
      print('_OwnedDataStore.get: {}'.format(e))
      if str(e) == owner_tag:
        self.variables[owner_tag] = { }
      out = default
    return out
  
  def put(self, owner_tag, key, value):
    if owner_tag not in self.variables:
      self.variables[owner_tag] = { }
    self.variables[owner_tag][key] = value
    return value
  
  def drop(self, owner_tag, key):
    target = self.variables[owner_tag][key]
    if isinstance(target, Iterable):
      target = target.copy()
    out = target
    del self.variables[owner_tag][key]
    return out

class Persistence(object):
  def __init__(self):
    '''Data persistence manager for tracking the three main datastores
    for use with dicelang's host chatbot. This manager will attempt to
    save variables in the directory specified by the environment variable
    DICELANG_DATASTORE if it exists, or will create a new datastore
    directory in place called `vars`.'''
    try:
      vars_directory = os.environ['DICELANG_DATASTORE']
    except KeyError:
      vars_directory = 'vars'
    public_path = '{}{}{}'.format(vars_directory, os.path.sep, 'public')
    server_path = vars_directory
    private_path = vars_directory
    if not os.path.isdir(vars_directory):
      os.mkdir(vars_directory)
    
    self.private = _OwnedDataStore(private_path, 'private')
    self.server  = _OwnedDataStore(server_path, 'server')
    self.public  = _DataStore(public_path)

  def save(self):
    self.private.save()
    self.server.save()
    self.public.save()
  
