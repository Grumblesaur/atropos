class _Singleton(object):
  '''Used for the implementation of `Undefined`. This class should
  never be used for any other reason.'''
  _instance = None
  def __new__(cls, *args, **kwargs):
    if not isinstance(cls._instance, cls):
      cls._instance = object.__new__(cls, *args, **kwargs)
    return cls._instance
  
class Undefined(_Singleton, object):
  '''A placeholder singleton value like Python's `None` to stand in
  when a a user references an identifier that does not yet exist.'''
  def __repr__(self):
    return 'Undefined'
  def __str__(self):
    return 'Undefined'
  def __bool__(self):
    return False

Undefined = Undefined()

