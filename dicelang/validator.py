class IntegerValidator(object):
  def __init__(self, max_digit_length=8,exc_type=Exception):
    self.size_limit = 8
    self.exc_type = exc_type
  
  def validate(self, an_integer, msg='Integer too large!'):
    if len(str(an_integer)) > self.size_limit:
      raise self.exc_type(msg)

