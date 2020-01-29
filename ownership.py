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
  
  def get(self, key):
    '''For anonymous scopes (e.g. block expressions not inside a function)
    this attempts to retrieve a key from innermost anonymous scope outward.
    
    For scopes within stack frames (e.g. block expressions forming the body
    of a function), this attempts to retrieve a key from the innermost scope
    of the stack frame outward.
    
    In either case, this function will report with the NotLocal object to
    indicate that a global variable lookup is necessary.'''
    out = None
    frame = self.get_frame()
    if frame is NotLocal:
      if self.anonymous_scopes:
        for scope in reversed(self.anonymous_scopes):
          if key in scope:
            out = scope[key]
            break
      else:
        out = frame
    else:
      for scope in reversed(frame):
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
      else:
        out = frame
    else:
      for scope in reversed(frame):
        if key in scope:
          out = scope[key]
          del   scope[key]
    return out if out is not None else NotLocal
  
  def __repr__(self):
    return 'ScopingData({usr}, {svr}, {scp})'.format(
      usr=repr(self.user),
      svr=repr(self.server),
      scp=repr(self.stack))


