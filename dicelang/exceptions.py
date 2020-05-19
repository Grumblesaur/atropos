class DicelangError(Exception):
  pass

class ExecutionTimeout(DicelangError):
  pass

class LoopTimeout(ExecutionTimeout):
  pass

loop_msg = ' '.join([
  '{do1}while loop iterated %s times without terminating.',
  "or your loop's condition never changed state.",
  'You may need to mark certain variables with "our" in front.',
  '\nSee "+help {do2}while" for more information.'
])

class WhileLoopTimeout(LoopTimeout):
  def __init__(self, msg=loop_msg.format(do1='', do2=''), *args, **kwargs):
    super().__init__(self, msg % kwargs['times'], *args, **kwargs)
  
class DoWhileLoopTimeout(LoopTimeout):
  def __init__(self, msg=loop_msg.format(do1='do ', do2='do', *args, **kwargs):
    super().__init__(self, msg % kwargs['times'], *args, **kwargs)

class ExponentiationTimeout(ExecutionTimeout):
  pass

class DiceRollTimeout(ExecutionTimeout):
  pass

class FunctionError(DicelangError):
  pass

class DefinitionError(FunctionError):
  pass

class CallError(FunctionError):
  pass

class OperationError(DicelangError):
  pass

