#!/usr/bin/env python3
import interpreter
import pytest
from undefined import Undefined

def get_test_cases(filename):
  test_cases = [ ]
  with open(filename, 'r') as f:
    for line in f:
      line = line.strip()
      if line:
        command, expected = map(lambda s: s.strip(), line.split('===>'))
        test_cases.append((command, eval(expected)))
  return test_cases 


class TestInterpreter:
  @pytest.mark.parametrize("command, expected", get_test_cases('test_cases.txt'))
  def test_execute(self, command, expected):
    dicelark = interpreter.Interpreter("grammar.lark")
    user = "Tester"
    server = "Test Server"
    actual = dicelark.execute(command, user, server)
    assert actual == expected
    return 1

if __name__ == '__main__':
  ti = TestInterpreter()
  passed = 0
  test_cases = get_test_cases('test_cases.txt')
  for test_case in test_cases:
    try:
      passed += ti.test_execute(*test_case)
    except AssertionError as e:
      print(e)
      break
  print('{} out of {} test cases passed.'.format(passed, len(test_cases)))


