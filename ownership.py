class ScopingData(object):
  def __init__(self, user='', server=''):
    self.user = user
    self.server = server
    self.scopes = [ ]
  
  def clear_params(self):
    self.set_params('', '')
  
  def depth(self):
    return len(self.scopes)
  
  def __bool__(self):
    return self.depth() > 0
  
  def __len__(self):
    return self.depth()
  
  def push_scope(self, new_scope=None):
    if new_scope is None:
      new_scope = {}
    self.scopes.append(new_scope)
  
  def pop_scope(self):
    return self.scopes.pop()
  
  def get(self, key):
    out = None
    for scope in reversed(self.scopes):
      try:
        out = scope[key]
      except KeyError:
        out = None
      else:
        break
    return out
  
  def put(self, key, value):
    self.scopes[-1][key] = value
    return value
  
  def drop(self, key):
    try:
      out = self.scopes[-1][key]
      del   self.scopes[-1][key]
    except KeyError:
      out = Undefined
    return out
  
  def __repr__(self):
    return 'ScopingData({usr}, {svr}, {scp})'.format(
      usr=repr(self.user),
      svr=repr(self.server),
      scp=repr(self.scopes))


