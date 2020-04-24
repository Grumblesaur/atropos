import os
from collections.abc import Iterable

from atropos_db.models import Variable

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
      except SyntaxError as e:
        print(e)
      except IOError as e:
        with open(filename, 'w') as f:
          pass
      
  def get(self, owner_tag, key, default=Undefined, mode=Variable.SERVER):
    return eval(Variable.objects.get(owner_id=owner_tag, var_type=mode, name=key).value_string)

  def put(self, owner_tag, key, value, mode=Variable.SERVER):
    Function.use_serializable_function_repr(True)
    variable = Variable.objects.update_or_create(owner_id=owner_tag, var_type=mode, name=key, value_string=repr(value)).value_string
    Function.use_serializable_function_repr(False)
    return variable

  def drop(self, owner_tag, key, mode=Variable.SERVER):
    variable = Variable.objects.get(owner_id=owner_tag, var_type=mode, name=key)
    out = variable.value_string
    variable.delete()
    return eval(out)
