class Function(object):
  def __init__(self, code, *param_names):
    self.code = code
    self.params = param_names
  
  def __repr__(self):
    return 'Function({code}, {params})'.format(code=self.code, params=self.params)
  

