from . import datastore
from .ownership import NotLocal
from .undefined import Undefined

class StorageError(Exception):
  pass

def error(mode):
  raise StorageError('Unknown identifier type: {}'.format(repr(mode)))

class Identifier(object):
  '''Internal class for storing the information of
  an identifier prior to its evaluation.'''
  
  def __init__(self, name, scoping_data, mode):
    '''Creates an Identifier object.
      name: the name of this identifier.
      mode: the scoping method to use to look up a variable's value
      scoping_data: an object of ScopingData type'''
    assert mode in ('private', 'server', 'scoped', 'global')
    self.name = name
    self.mode = mode
    self.scoping_data = scoping_data
  
  def __repr__(self):
    '''verbose string representation of an Identifier.'''
    return 'Identifier({n}, {m}, {s})'.format(
      n=repr(self.name),
      m=repr(self.mode),
      s=repr(self.scoping_data))
  
  def __str__(self):
    return self.name
  
  def get(self):
    '''Retrieves the identifier's value from the appropriate datastore.'''
    if self.mode == 'private':
      out = datastore.private.get(self.scoping_data.user, self.name)
    elif self.mode == 'server':
      out = datastore.server.get(self.scoping_data.server, self.name)
    elif self.mode == 'scoped':
      if self.scoping_data:
        lookup = self.scoping_data.get(self.name)
      if not self.scoping_data or lookup is NotLocal:
        lookup = datastore.public.get(self.name)
      out = lookup if lookup is not None else Undefined
    elif self.mode == 'global':
      out = datastore.public.get(self.name)
    else:
      error()
    return out
  
  def put(self, value):
    '''Stores the identifier's value in the appropriate datastore.'''
    if self.mode == 'private':
      out = datastore.private.put(self.scoping_data.user, self.name, value)
    elif self.mode == 'server':
      out = datastore.server.put(self.scoping_data.server, self.name, value)
    elif self.mode == 'scoped':
      if self.scoping_data:
        put = self.scoping_data.put(self.name, value)
      if not self.scoping_data or put is NotLocal:
        put = datastore.public.put(self.name, value)
      out = put
    elif self.mode == 'global':
      out = datastore.public.put(self.name, value)
    else:
      error()
    return out

  def drop(self):
    '''Removes the identifier from the appropriate datastore.'''
    if self.mode == 'private':
      out = datastore.private.drop(self.scoping_data.user, self.name)
    elif self.mode == 'server':
      out = datastore.server.drop(self.scoping_data.server, self.name)
    elif self.mode == 'scoped':
      if self.scoping_data:
        drop = self.scoping_data.drop(self.name)
      if not self.scoping_data or drop is NotLocal:
        drop = datastore.public.drop(self.name)
      out = drop if drop is not None else Undefined
    elif self.mode == 'global':
      out = datastore.public.drop(self.name)
    else:
      error()
    return out


