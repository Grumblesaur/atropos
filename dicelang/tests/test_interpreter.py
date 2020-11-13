import pytest
from dicelang.interpreter import Interpreter
from dicelang.function    import Function
from dicelang.undefined   import Undefined
Skip = object
files_to_test = ['block_comment.txt', 'comment_lines.txt']
user = 10 
server = 11

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

class TestInterpreter:
  interpreter = Interpreter()

  @pytest.mark.parametrize("command, expected", get_lines('data/lines.txt'))
  def test_lines(self, command, expected):
    result = TestInterpreter.interpreter.execute(command, user, server)
    actual = result[0]
    predicate = actual == expected if expected is not Skip else True
    print(actual)
    assert predicate

