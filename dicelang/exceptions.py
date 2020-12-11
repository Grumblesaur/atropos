class DicelangError(Exception):
  pass

class ExecutionTimeout(DicelangError):
  pass

class LoopTimeout(ExecutionTimeout):
  pass

while_loop_msg = '\n'.join([
  '\nwhile loop iterated %s times without terminating,',
  "or your loop's condition never changed state. You may",
  'need to mark certain variables with "our" in front.',
  '\nSee "+help while" for more information.'
])

do_while_loop_msg = while_loop_msg.replace('while', 'do while')

class WhileLoopTimeout(LoopTimeout):
  def __init__(self, n):
    self.msg = while_loop_msg % n
  
class DoWhileLoopTimeout(LoopTimeout):
  def __init__(self, n):
    self.msg = do_while_loop_msg % n

class ExponentiationTimeout(ExecutionTimeout):
  pass

class DiceRollTimeout(ExecutionTimeout):
  pass

class FunctionError(DicelangError):
  pass

class AliasError(DicelangError):
  pass

class DefinitionError(FunctionError):
  pass

class CallError(FunctionError):
  pass

class OperationError(DicelangError):
  pass

class StorageError(DicelangError):
  pass

class PrivilegeError(StorageError):
  pass


class DicelangSignal(Exception):
  def __init__(self, data=None):
    self.is_set = data is not None
    self.data = data if data is not None else Undefined
    self.msg = "Generic Dicelang Signal"
  
  def __str__(self):
    return self.msg

class BreakSignal(DicelangSignal):
  def __init__(self, data):
    super().__init__(self, data)
    self.msg = f'Break in execution with data: {data!s}'

class ReturnSignal(DicelangSignal):
  def __init__(self, data):
    super().__init__(self, data)
    self.msg = f'Return from function with data: {data!s}'

class SkipSignal(DicelangSignal):
  def __init__(self, data):
    super().__init__(self, data)
    self.msg = f'Skip iteration with data: {data!s}'

