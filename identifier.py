import datastore
from undefined import Undefined
class Identifier(object):
  '''Internal class for storing the information of
  an identifier prior to its evaluation.'''
  
  def __init__(self, name, scoping_data, mode):
    '''Creates an Identifier object.
      name: the name of this identifier.
      mode: the scoping method to use to look up a variable's value
      scoping_data: an object of ScopingData type'''
    assert mode in ('private', 'server', 'scoped')
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
      else:
        lookup = datastore.public.get(self.name)
      out = lookup if lookup is not None else Undefined
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
      else:
        put = datastore.public.put(self.name, value)
      out = put
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
      else:
        drop = datastore.public.drop(self.name)
      out = drop if drop is not None else Undefined
    return out


