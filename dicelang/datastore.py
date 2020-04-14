import os
from collections.abc import Iterable

# The following imports are not used by name in this file, but are
# necessary for enabling `eval` to work correctly. Do not let
# PyCharm "optimize" them out.
from dicelang.undefined import Undefined
from dicelang.function  import Function
 
class DataStore(object):
  '''Specialization of _DataStore where keys are associated by
  some other key specifying ownership, such as a username or
  server handle.'''
  
  def __init__(self, storage_directory, prefix):
    '''Internal class for saving, loading, accessing, and mutating
    standing variables during the use of the chat bot.'''
    self.storage_directory = storage_directory
    self.prefix = prefix
    self.variables = {}
    self.sep = ':'
    filenames = os.listdir(self.storage_directory)
    filenames = filter(lambda s: s.startswith(self.prefix), filenames)
    builder = lambda fn: '{}{}{}'.format(
      self.storage_directory,
      os.path.sep,
      fn)
    filenames = map(builder, filenames)
    for filename in filenames:
      print(f"loading '{filename}' ...")
      _, owner = filename.rsplit('_', 1)
      owner = eval(owner)
      self.variables[owner] = { }
      try:
        with open(filename, 'r') as f:
          for line in f:
            try:
              k_repr, v_repr = line.strip().split(self.sep, 1)
              key = eval(k_repr)
              value = eval(v_repr)
              self.variables[owner][key] = value
            except Exception as e:
              print(f'Bad var when loading {filename!r}: {e!s}')
              raise
      except SyntaxError as e:
        print(e)
      except IOError as e:
        with open(filename, 'w') as f:
          pass
      
  def save(self):
    owners = self.variables.keys()
    for owner in owners:
      filename = f'{self.storage_directory}{os.path.sep}{self.prefix}_{owner}'
      with open(filename, 'w') as f:
        Function.use_serializable_function_repr(True)
        for key, value in self.variables[owner].items():
          f.write(f'{key!r}{self.sep}{value!r}\n')
        Function.use_serializable_function_repr(False)
  
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
    if isinstance(target, Iterable) and not isinstance(target, str):
      target = target.copy()
    out = target
    del self.variables[owner_tag][key]
    return out

