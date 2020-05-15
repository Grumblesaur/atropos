class IntegerValidator(object):
  def __init__(self, max_digit_length=8):
    self.size_limit = 8
  
  def validate(self, an_integer):
    return len(str(an_integer)) <= self.size_limit

