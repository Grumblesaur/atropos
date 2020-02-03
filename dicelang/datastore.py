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
  def __init__(self, storage_file_name):
    """Internal class for saving, loading, accessing, and mutating
    standing variables during the use of the chat bot."""
    self.storage_file_name = storage_file_name
    with open(self.storage_file_name, 'r') as f:
      storage_text = f.read()
    try:
      self.variables = eval(storage_text)
    except Exception as e:
      self.variables = {}
    
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
  
  def save(self):
    with open(self.storage_file_name, 'w') as f:
      f.write(repr(self.variables))
  

class _OwnedDataStore(_DataStore):
  def get(self, owner_tag, key, default=Undefined):
    try:
      out = self.variables[owner_tag][key]
    except KeyError as e:
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
    filenames = 'private server public'.split()
    try:
      vars_directory = os.environ['DICELANG_DATASTORE']
    except KeyError:
      vars_directory = 'vars'
    paths = ['{}/{}'.format(vars_directory, name) for name in filenames]
    if not os.path.isdir(vars_directory):
      os.mkdir(vars_directory)
    for path in paths:
      if not os.path.isfile(path):
        os.mknod(path)
    private_path, server_path, public_path = paths
    
    self.private = _OwnedDataStore(private_path)
    self.server  = _OwnedDataStore(server_path)
    self.public  = _DataStore(public_path)

  def save():
    private.save()
    server.save()
    public.save()

persistence = Persistence()

