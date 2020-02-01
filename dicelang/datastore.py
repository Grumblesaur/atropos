from collections.abc import Iterable
from .undefined import Undefined
from .function  import SyntaxToken
from .function  import SyntaxTree
from .function  import Function

class _DataStore(object):
  '''Internal class for saving, loading, accessing, and mutating
  standing variables during the use of the chat bot.'''
  def __init__(self, storage_file_name):
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

private = None
server  = None
public  = None


def configure(private_path, server_path, public_path):
  private = _OwnedDataStore(private_path)
  server  = _OwnedDataStore(server_path)
  public  = _DataStore(public_path)

def save():
  private.save()
  server.save()
  public.save()


