#!/usr/bin/env python3
from dicelang import interpreter
import pytest
from dicelang.undefined import Undefined
from dicelang.function  import Function

Skip = object
def get_test_cases(filename):
  '''test cases file pointed to by filename must have the following properties:
    * lines are either blank or contain a test case
    * test cases consist of three things in the following order:
      * the command to be executed by the dicelang interpreter
      * the exact sequence of characters '===>' without quotes
      * the value in Python to which the command should resolve'''
  test_cases = [ ]
  with open(filename, 'r') as f:
    for line in f:
      line = line.strip()
      if line:
        command, expected = map(lambda s: s.strip(), line.split('===>'))
        expected = Skip if expected == '__NO_TEST_CASE__' else eval(expected)
        test_cases.append((command, expected))
  return test_cases 

class TestInterpreter:
  dicelark = interpreter.Interpreter('../dicelang/grammar.lark')
  
  @pytest.mark.parametrize("command, expected", get_test_cases('../data/lines.txt'))
  def test_execute(self, command, expected):
    user = 'Tester'
    server = 'Test Server'
    actual = TestInterpreter.dicelark.execute(command, user, server)
    if expected is not Skip:
      assert actual == expected
    else:
      assert True


