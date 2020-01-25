from collections import defaultdict

class _Singleton(object):
  '''Used for the implementation of `Undefined`. This class should
  never be used for any other reason.'''
  _instance = None
  def __new__(cls, *args, **kwargs):
    if not isinstance(cls._instance, cls):
      cls._instance = object.__new__(cls, *args, **kwargs)
    return cls._instance
  
class Undefined(_Singleton, object):
  '''A placeholder singleton value like Python's `None` to stand in
  when a a user references an identifier that does not yet exist.'''
  def __repr__(self):
    return 'Undefined()'
  def __str__(self):
    return 'Undefined'
  def __bool__(self):
    return False

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
    
  def get(self, key, default=Undefined()):
    try:
      out = self.variables[key]
    except KeyError:
      out = default
    return out
  
  def put(self, key, value):
    self.variables[key] = value
   
  def save(self):
    with open(self.storage_file_name, 'w'):
      f.write(repr(self.variables))


private = _DataStore('vars/private')
server  = _DataStore('vars/server')
public  = _DataStore('vars/public')
  
