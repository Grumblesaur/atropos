class DicelangError(Exception):
  pass

class ExecutionTimeout(DicelangError):
  pass

class LoopTimeout(ExecutionTimeout):
  pass

class DicelangSignal(Exception):
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

class BreakSignal(DicelangSignal):
  def __init__(self, data):
    self.data = data
    self.msg = f'Break in execution with data: {data!s}'
  def __str__(self):
    return self.msg


