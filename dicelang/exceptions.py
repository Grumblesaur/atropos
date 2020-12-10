class DicelangError(Exception):
  pass

class ExecutionTimeout(DicelangError):
  pass

class LoopTimeout(ExecutionTimeout):
  pass

class DicelangSignal(Exception):
  pass

loop_msg = '\n'.join([
  '\n{do1} while loop iterated %s times without terminating,',
  "or your loop's condition never changed state. You may",
  'need to mark certain variables with "our" in front.',
  '\nSee "+help {do1}while" for more information.'
])

class WhileLoopTimeout(LoopTimeout):
  def __init__(self, msg=loop_msg.format(do1=''), *args, **kwargs):
    super().__init__(self, msg % kwargs['times'])
  
class DoWhileLoopTimeout(LoopTimeout):
  def __init__(self, msg=loop_msg.format(do1='do'), *args, **kwargs):
    super().__init__(self, msg % kwargs['times'])

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


