import copy

class StackException(Exception):
  pass

NotLocal = object

class ScopingData(object):
  def __init__(self, user='', server=''):
    self.user = user
    self.server = server
    self.frame_id = 0
    self.frames = { }
    self.anonymous_scopes = [ ]
    self.closure = []
  
  def push_closure(self, saved_environment):
    self.closure.append(saved_environment)
  
  def pop_closure(self):
    self.closure.pop()
  
  def clear_closure(self):
    self.closure = []
  
  def calling_environment(self):
    frame = self.get_frame()
    if frame is NotLocal:
      try:
        frame = [copy.deepcopy(self.get_scope())]
      except IndexError:
        frame = [{}]
    else:
      frame = copy.deepcopy(frame)
    return frame
  
  def push_frame(self):
    self.frame_id += 1
    self.frames[self.frame_id] = [ ]
  
  def pop_frame(self):
    out = self.frames.pop(self.frame_id)
    self.frame_id -= 1
    return out
  
  def get_frame(self):
    try:
      out = self.frames[self.frame_id]
    except KeyError:
      out = NotLocal
    return out
  
  def push_scope(self, scope=None):
    new_scope = scope if scope is not None else {}
    try:
      self.frames[self.frame_id].append(new_scope)
    except KeyError:
      self.anonymous_scopes.append(new_scope)
    return self.frame_id
  
  def pop_scope(self):
    try:
      self.frames[self.frame_id].pop()
    except IndexError as e:
      if 'pop from empty list' in str(e):
        raise StackException('Cannot pop scope from empty stack frame!')
      else:
        raise StackException('Cannot pop scope from global stack frame!')
    except KeyError:
      self.anonymous_scopes.pop()
    return self.frame_id
    
  def get_scope(self):
    try:
      scope = self.frames[self.frame_id][-1]
    except IndexError as e:
      if 'list index out of range' in str(e):
        raise StackException('Cannot get scope from empty stack frame!')
      else:
        raise StackException('Cannot get scope from global stack frame!')
    except KeyError:
      scope = self.anonymous_scopes[-1]
    return scope
  
  def get(self, key):
    '''For anonymous scopes (e.g. block expressions not inside a function)
    this attempts to retrieve a key from innermost anonymous scope outward.
    
    For scopes within stack frames (e.g. block expressions forming the body
    of a function), this attempts to retrieve a key from the innermost scope
    of the stack frame outward.
    
    If applicable, the lookup will search the current frame of closed
    variables. If this also fails, the function will return NotLocal.
    Otherwise, a value will be returned.'''
    out = None
    frame = self.get_frame()
    if frame is NotLocal:
      if self.anonymous_scopes:
        for scope in reversed(self.anonymous_scopes):
          if key in scope:
            out = scope[key]
            break
      if not self.anonymous_scopes or out is None:
        out = frame
    else:
      for scope in reversed(frame):
        if key in scope:
          out = scope[key]
          break
    
    if out is None:
      for scope in reversed(self.closure[-1]):
        if key in scope:
          out = scope[key]
          break
    return out if out is not None else NotLocal
  
  def put(self, key, value):
    '''For anonymous scopes, this attempts to emplace a value at a key from
    the outermost anonymous scope inward. If the key is not found, it will
    create it at the innermost anonymous scope.
    
    For scopes within stack frames, this attempts to emplace a value at a key
    from the outermost scope of the stack frame inward. If the key is not found,
    it will create it at the innermost scope of the stack frame.
    
    If there is no current scope whatsoever, it will return the NotLocal
    object to indicate that a global variable emplacement is necessary.'''
    frame = self.get_frame()
    if frame is NotLocal:
      if self.anonymous_scopes:
        in_scope = None
        for scope in self.anonymous_scopes:
          if key in scope:
            in_scope = scope
            break
        in_scope = self.anonymous_scopes[-1] if in_scope is None else in_scope
        in_scope[key] = value
      else:
        value = frame
    else:
      in_scope = None
      for scope in self.get_frame():
        if key in scope:
          in_scope = scope
          break
      if in_scope is not None:
        scope[key] = value
      else:
        self.get_scope()[key] = value
    return value
  
  def drop(self, key):
    '''For anonymous scopes, this attempts to delete a value at a key from
    the innermost anonymous scope outward and return that value.
    
    For scopes within stack frames, this attempts to delete a value at a key
    from the innermost scope of the stack frame outward and return that value.
    
    If there is no current scope whatsoever, it will return the NotLocal object
    to indicate that a global variable deletion is necessary.'''
    out = None
    frame = self.get_frame()
    if frame is NotLocal:
      if self.anonymous_scopes:
        for scope in reversed(self.anonymous_scopes):
          if key in scope:
            out = scope[key]
            break
      if not self.anonymous_scopes or out is None:
        out = frame
    else:
      for scope in reversed(frame):
        if key in scope:
          out = scope[key]
          del   scope[key]
    return out if out is not None else NotLocal
  
  def __repr__(self):
    return f'ScopingData({self.user!r}, {self.server!r}, {self.frames!r})'


