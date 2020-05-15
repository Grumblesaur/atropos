class IntegerValidator(object):
  def __init__(self, max_digit_length=8,exc_type=Exception):
    self.size_limit = 8
  
  def validate(self, an_integer, msg='Integer too large!'):
    if len(str(an_integer)) > self.size_limit:
      raise exc_type(msg)

