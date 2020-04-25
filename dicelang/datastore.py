import os
import copy
from collections.abc import Iterable

os.environ['DJANGO_SETTINGS_MODULE'] = 'db_config.settings'
import django
django.setup()
from atropos_db.models import Variable
from asgiref.sync import sync_to_async

# The following imports are not used by name in this file, but are
# necessary for enabling `eval` to work correctly. Do not let
# PyCharm "optimize" them out.
from dicelang.undefined import Undefined
from dicelang.function  import Function

class Cache(object):
  def __init__(self, modes=['private', 'server', 'core', 'global']):
    self.vars = {}
    for mode in modes:
      self.vars[mode] = {}
  
  def get(self, owner_id, key, mode):
    mode_dict = self.vars[mode]
    try:
      out = mode_dict[owner_id][key]
    except KeyError:
      out = None
    return out
  
  def put(self, owner_id, key, value, mode):
    if owner_id not in self.vars[mode]:
      self.vars[mode][owner_id] = {}
    self.vars[mode][owner_id][key] = value
    return value
  
  def drop(self, owner_id, key, mode):
    if owner_id in self.vars[mode] and key in self.vars[mode][owner_id]:
      out = copy.copy(self.vars[mode][owner_id][key])
    else:
      out = None
    return out

 
class DataStore(object):
  '''Specialization of _DataStore where keys are associated by
  some other key specifying ownership, such as a username or
  server handle.'''
  
  def __init__(self, migrate=False):
    self.cache = Cache()
    if migrate is True:
      self.migrate_all()
  
  def migrate_all(self):
    storage_dir = os.environ['DICELANG_DATASTORE']
    for prefix in ['core', 'global', 'server', 'private']:
      self.migrate(storage_dir, prefix)
    print('migration complete')
    
  def migrate(self, storage_directory, prefix):
    print(f'migrating {prefix} ...')
    filenames = os.listdir(storage_directory)
    filenames = filter(lambda s: s.startswith(prefix), filenames)
    builder = lambda fn: '{}{}{}'.format(storage_directory, os.path.sep, fn)
    filenames = map(builder, filenames)
    for filename in filenames:
      print(f"loading '{filename}' ...")
      _, owner = filename.rsplit('_', 1)
      try:
        with open(filename, 'r') as f:
          for line in f:
            try:
              k_repr, v_repr = line.strip().split(":", 1)
              self.put(int(owner), eval(k_repr), eval(v_repr), prefix)
            except Exception as e:
              print(f'Bad var when loading {filename!r}: {e!s}')
      except SyntaxError as e:
        print(e)
    return
  
  def view(self, mode, owner_id):
    results = Variable.objects.filter(var_type=mode, owner_id=owner_id)
    names = [ ]
    for result in results:
      names.append(result.name)
    return names
  
  def get(self, owner_tag, key, mode):
    out = self.cache.get(owner_tag, key, mode)
    if out is None:
      try:
        out = eval(Variable.objects.get(owner_id=owner_tag, var_type=mode, name=key).value_string)
      except Exception as e:
        out = None
      else:
        self.cache.put(owner_tag, key, out, mode)
    return out

  def put(self, owner_tag, key, value, mode):
    self.cache.put(owner_tag, key, value, mode)
    
    Function.use_serializable_function_repr(True)
    mutating = {'value_string': repr(value)}
    Function.use_serializable_function_repr(False)
    
    variable = Variable.objects.update_or_create(
      owner_id=owner_tag,
      var_type=mode,
      name=key,
      defaults=mutating)
    
    variable = variable[0].value_string
    return eval(variable)

  def drop(self, owner_tag, key, mode):
    drop = self.cache.drop(owner_tag, key, mode)
    if drop is not None:
      variable = Variable.objects.get(owner_id=owner_tag, var_type=mode, name=key)
      out = eval(variable.value_string)
      variable.delete()
    else:
      out = drop
    return out

