import os
import copy
import threading
import time
from collections.abc import Iterable
from collections import defaultdict

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
from dicelang.alias import Alias
from dicelang.float_special import inf
from dicelang.float_special import nan

VAR_MODES = ['private', 'server', 'core', 'global']

class Cache(object):
  def __init__(self, modes=VAR_MODES, prune_below=10):
    self.vars = {}
    self.uses = {}
    self.threshold = prune_below
    for mode in modes:
      self.vars[mode] = {}
      self.uses[mode] = {}
  
  def get(self, owner_id, key, mode):
    try:
      out = self.vars[mode][owner_id][key]
      self.uses[mode][owner_id][key] += 1
    except KeyError:
      out = None
    return out
  
  def put(self, owner_id, key, value, mode):
    if owner_id not in self.vars[mode]:
      self.vars[mode][owner_id] = {}
      self.uses[mode][owner_id] = defaultdict(int)
    self.vars[mode][owner_id][key] = value
    self.uses[mode][owner_id][key] += 1
    return value
  
  def drop(self, owner_id, key, mode):
    if owner_id in self.vars[mode] and key in self.vars[mode][owner_id]:
      out = copy.copy(self.vars[mode][owner_id][key])
      del self.vars[mode][owner_id][key]
      del self.uses[mode][owner_id][key]
    else:
      out = None
    return out
  
  def prune(self):
    '''Don't prune `core` variables -- they're usually large, often-used, and
    well-curated, which means they're good candidates for remaining loaded.'''
    marked = [ ]
    for mode in filter(lambda s: s != 'core', self.uses):
      for owner in self.uses[mode]:
        for key in self.uses[mode][owner]:
          uses = self.uses[mode][owner][key]
          is_function = isinstance(self.vars[mode][owner][key], Function)
          function_sweep =     is_function and uses < self.threshold / 2
          value_sweep    = not is_function and uses < self.threshold
          if function_sweep or value_sweep:
            marked.append((mode, owner, key))
          else:
            self.uses[mode][owner][key] = 0
    
    objects_pruned = 0
    for item in marked:
      objects_pruned += self._remove(*item)
    return objects_pruned
  
  def _remove(self, mode, owner, key):
    print(f'prune {(mode, owner, key)} from cache')
    del self.vars[mode][owner][key]
    del self.uses[mode][owner][key]
    return 1
 
class DataStore(object):
  def __init__(self, cache_time=6*60*60):
    self.cache = Cache()
    
    def pruning_task(cycle_time):
      while True:
        time.sleep(cycle_time)
        pruned = self.cache.prune()
        print(f'{pruned} objects pruned from cache')
    
    self.pruner = threading.Thread(
      target=pruning_task,
      args=(cache_time,),
      daemon=True)
    self.pruner.start()
  
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
        out_repr = Variable.objects.get(
          owner_id=owner_tag,
          var_type=mode,
          name=key).value_string
        out = eval(out_repr)
      except Exception as e:
        out = None
      else:
        self.cache.put(owner_tag, key, out, mode)
    return out

  def put(self, owner_tag, key, value, mode):
    self.cache.put(owner_tag, key, value, mode)
    
    with Function.SerializableRepr() as _:
      mutating = {'value_string': repr(value)}
    
    variable = Variable.objects.update_or_create(
      owner_id=owner_tag,
      var_type=mode,
      name=key,
      defaults=mutating)
    
    variable = variable[0].value_string
    return eval(variable)

  def drop(self, owner_tag, key, mode):
    self.cache.drop(owner_tag, key, mode)
    try:
      var = Variable.objects.get(owner_id=owner_tag, var_type=mode, name=key)
    except Variable.DoesNotExist:
      out = None
    else:
      out = eval(var.value_string)
      var.delete()
    return out

