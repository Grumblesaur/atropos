class IntegerValidator(object):
  def __init__(self, max_digit_length, exc_type=Exception):
    self.size_limit = max_digit_length
    self.exc_type = exc_type
  
  def validate(self, an_integer, msg='Integer too large!'):
    if len(str(an_integer)) > self.size_limit:
      raise self.exc_type(msg)

