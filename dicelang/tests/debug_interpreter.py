import pytest
from dicelang.interpreter import Interpreter
from dicelang.function import Function
from dicelang.undefined import Undefined
from test_interpreter import get_lines
m = Interpreter()
for command, expected in get_lines('data/lines.txt'):
  actual = m.execute(command, 'debug', 'debug-server')
  print(f'{actual} ===> {expected}')


