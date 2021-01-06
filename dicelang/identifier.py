import os
from dicelang.ownership import NotLocal
from dicelang.undefined import Undefined
from dicelang.exceptions import PrivilegeError, StorageError, ProtectedError
from dicelang import builtin

def load_core_editors():
  core_editors = []
  try:
    editors_file = os.environ['DICELANG_CORE_EDITORS']
  except KeyError:
    editors_file = 'editors'
  with open(editors_file, 'r') as f:
    for line in f:
      id_string = line.strip()
      if id_string:
        core_editors.append(eval(id_string))
  return core_editors

class Identifier(object):
  '''Internal class for storing the information of
  an identifier prior to its evaluation.'''
  
  core_editors = load_core_editors()
  
  def __init__(self, name, scoping_data, mode, variable_data):
    '''Creates an Identifier object.
      name: the name of this identifier.
      mode: the scoping method to use to look up a variable's value
      scoping_data: an object of ScopingData type'''
    assert mode in ('private', 'server', 'scoped', 'global', 'core')
    self.name = name
    self.mode = mode
    self.scoping_data = scoping_data
    self.datastore = variable_data
  
  def __repr__(self):
    '''verbose string representation of an Identifier.'''
    return f'Identifier({self.name!r}, {self.mode!r}, {self.scoping_data!r})'
  
  def __str__(self):
    return self.name
  
  def get(self):
    '''Retrieves the identifier's value from the appropriate datastore.'''
    if self.mode == 'private':
      out = self.datastore.get(self.scoping_data.user, self.name, self.mode)
    elif self.mode == 'server':
      out = self.datastore.get(self.scoping_data.server, self.name, self.mode)
    elif self.mode == 'global' or self.mode == 'core':
      out = self.datastore.get(-1, self.name, self.mode)
    elif self.mode == 'scoped':
      try:
        lookup = builtin.variables[self.name]
      except KeyError:
        lookup = None
        if self.scoping_data:
          lookup = self.scoping_data.get(self.name)
        if not self.scoping_data or lookup is NotLocal:
          lookup = self.datastore.get(self.scoping_data.server, self.name, 'server')
      out = lookup
    else:
      raise StorageError(f'Unknown identifier type: "{self.mode}".')
    return out if out is not None else Undefined
  
  def put(self, value):
    '''Stores the identifier's value in the appropriate datastore.'''
    if self.mode == 'private':
      out = self.datastore.put(self.scoping_data.user, self.name, value, self.mode)
    elif self.mode == 'server':
      out = self.datastore.put(self.scoping_data.server, self.name, value, self.mode)
    elif self.mode == 'global':
      out = self.datastore.put(-1, self.name, value, self.mode)
    elif self.mode == 'core':
      if self.scoping_data.user not in Identifier.core_editors:
        raise PrivilegeError('non-privileged user cannot modify core library')
      out = self.datastore.put(-1, self.name, value, self.mode)
    elif self.mode == 'scoped':
      if self.name in builtin.variables:
        e = f'Builtin variable {self.name!r} may not be overwritten.'
        raise ProtectedError(e)
      if self.scoping_data:
        put = self.scoping_data.put(self.name, value)
      if not self.scoping_data or put is NotLocal:
        put = self.datastore.put(self.scoping_data.server, self.name, value, 'server')
      out = put
    else:
      raise StorageError(f'Unknown identifier type: "{self.mode}".')
    return out if out is not None else Undefined

  def drop(self):
    '''Removes the identifier from the appropriate datastore.'''
    if self.mode == 'private':
      out = self.datastore.drop(self.scoping_data.user, self.name, self.mode)
    elif self.mode == 'server':
      out = self.datastore.drop(self.scoping_data.server, self.name, self.mode)
    elif self.mode == 'global':
      out = self.datastore.drop(-1, self.name, self.mode)
    elif self.mode == 'core':
      if self.scoping_data.user not in Identifier.core_editors:
        raise PrivilegeError('non-privileged user cannot delete core library')
      out = self.datastore.drop(-1, self.name, self.mode)
    elif self.mode == 'scoped':
      if self.name in builtin.variables:
        e = f'Builtin variable {self.name!r} may not be deleted.'
        raise ProtectedError(e)
      if self.scoping_data:
        drop = self.scoping_data.drop(self.name)
      if not self.scoping_data or drop is NotLocal:
        drop = self.datastore.drop(self.scoping_data.server, self.name, 'server')
      out = drop
    else:
      raise StorageError(f'Unknown identifier type: "{self.mode}".')
    return out if out is not None else Undefined


