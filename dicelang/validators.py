class NumberTooLarge(Exception):
  pass

default_msg = ' '.join([
  'The {} of your power (**) operation was too large, and',
  'executing that operation may cause other users to wait too long',
  'for their request to be processed.'
])

class ExponentTooLarge(NumberTooLarge):
  def __init__(self, msg=default_msg.format('exponent'), *args, **kwargs):
    super().__init__(msg, *args, **kwargs)

class BaseTooLarge(NumberTooLarge):
  def __init__(self, msg=default_msg.format('base'), *args, **kwargs):
    super().__init__(msg, *args, **kwargs)


class IntegerValidator(object):
  def __init__(self, exponent_size_limit=6, base_size_multiplier=300):
    self.size_limit = exponent_size_limit
    self.base_size_multiplier = base_size_multiplier
  
  def validate_base(self, base):
    '''Bases are allowed to be larger as they don't affect the size of a power
    operation's outcome nearly as much as an exponent does.'''
    if isinstance(base, int):
      orders_of_magnitude = len(str(base))
      if orders_of_magnitude >= self.size_limit * self.base_size_multiplier:
        raise BaseTooLarge()
    return True
  
  def validate_exponent(self, exponent):
    '''Exponents must be severely limited in magnitude to avoid locking up
    the interpreter.'''
    if isinstance(exponent, int):
      orders_of_magnitude = len(str(exponent))
      if orders_of_magnitude >= self.size_limit:
        raise ExponentTooLarge()
    return True


