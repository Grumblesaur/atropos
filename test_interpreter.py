#!/usr/bin/env python3
import interpreter
import pytest
from undefined import Undefined

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

