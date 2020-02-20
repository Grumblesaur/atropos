import pytest
from dicelang.interpreter import Interpreter
from dicelang.function    import Function
from dicelang.undefined   import Undefined
Skip = object
files_to_test = ['block_comment.txt', 'comment_lines.txt']
user = 'User'
server = 'Server'

def get_lines(filename):
  cases = [ ]

  with open(filename, 'r') as f:
    for line in f:
      line = line.strip()
      if line:
        case = line.split('===>')
        command, expected = map(lambda s: s.strip(), case)
        expected = Skip if expected == '__NO_TEST_CASE__' else eval(expected)
        cases.append((command, expected))
  return cases

def get_files():
  cases = [ ]
  for filename in files_to_test:
    with open(f'data/{filename}', 'r') as f:
      code, result = map(lambda s: s.strip(), f.read().split('===>'))
      print(code, result)
      result = Skip if result == '__NO_TEST_CASE__' else eval(result)
      cases.append((code, result))
  return cases

class TestInterpreter:
  interpreter = Interpreter()

  @pytest.mark.parametrize("command, expected", get_lines('data/lines.txt'))
  def test_lines(self, command, expected):
    actual = TestInterpreter.interpreter.execute(command, user, server)
    predicate = actual == expected if expected is not Skip else True
    print(actual)
    assert predicate

  @pytest.mark.parametrize("code, result", get_files())
  def test_files(self, code, result):
    actual = TestInterpreter.interpreter.execute(code, user, server)
    predicate = actual == result if result is not Skip else True
    assert predicate

