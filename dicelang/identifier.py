import os
from dicelang.ownership import NotLocal
from dicelang.undefined import Undefined

class StorageError(Exception):
  pass

class PrivilegeError(StorageError):
  pass

def error(mode):
  raise StorageError(f'Unknown identifier type: {mode!r}')

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
  
  def __init__(self, name, scoping_data, mode, pub, serv, priv, core):
    '''Creates an Identifier object.
      name: the name of this identifier.
      mode: the scoping method to use to look up a variable's value
      scoping_data: an object of ScopingData type'''
    assert mode in ('private', 'server', 'scoped', 'global', 'core')
    self.name = name
    self.mode = mode
    self.scoping_data = scoping_data
    self.core = core
    self.public = pub
    self.server = serv
    self.private = priv
  
  def __repr__(self):
    '''verbose string representation of an Identifier.'''
    return f'Identifier({self.name!r}, {self.mode!r}, {self.scoping_data!r})'
  
  def __str__(self):
    return self.name
  
  def get(self):
    '''Retrieves the identifier's value from the appropriate datastore.'''
    if self.mode == 'private':
      out = self.private.get(self.scoping_data.user, self.name)
    elif self.mode == 'server':
      out = self.server.get(self.scoping_data.server, self.name)
    elif self.mode == 'scoped':
      if self.scoping_data:
        lookup = self.scoping_data.get(self.name)
      if not self.scoping_data or lookup is NotLocal:
        lookup = self.server.get(self.scoping_data.server, self.name)
      out = lookup if lookup is not None else Undefined
    elif self.mode == 'global':
      out = self.public.get(-1, self.name)
    elif self.mode == 'core':
      out = self.core.get(-1, self.name)
    else:
      error()
    return out
  
  def put(self, value):
    '''Stores the identifier's value in the appropriate datastore.'''
    if self.mode == 'private':
      out = self.private.put(self.scoping_data.user, self.name, value)
    elif self.mode == 'server':
      out = self.server.put(self.scoping_data.server, self.name, value)
    elif self.mode == 'scoped':
      if self.scoping_data:
        put = self.scoping_data.put(self.name, value)
      if not self.scoping_data or put is NotLocal:
        put = self.server.put(self.scoping_data.server, self.name, value)
      out = put
    elif self.mode == 'global':
      out = self.public.put(-1, self.name, value)
    elif self.mode == 'core':
      if self.scoping_data.user not in Identifier.core_editors:
        raise PrivilegeError('non-privileged user cannot modify core library')
      out = self.core.put(-1, self.name, value)
    else:
      error()
    return out

  def drop(self):
    '''Removes the identifier from the appropriate datastore.'''
    if self.mode == 'private':
      out = self.private.drop(self.scoping_data.user, self.name)
    elif self.mode == 'server':
      out = self.server.drop(self.scoping_data.server, self.name)
    elif self.mode == 'scoped':
      if self.scoping_data:
        drop = self.scoping_data.drop(self.name)
      if not self.scoping_data or drop is NotLocal:
        drop = self.server.drop(self.scoping_data.server, self.name)
      out = drop if drop is not None else Undefined
    elif self.mode == 'global':
      out = self.public.drop(-1, self.name)
    elif self.mode == 'core':
      if self.scoping_data.user not in Identifier.core_editors:
        raise PrivilegeError('non-privileged user cannot delete core library')
      out = self.core.drop(-1, self.name)
    else:
      error()
    return out


