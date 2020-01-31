#!/usr/bin/env python3

import interpreter
def main(*args):
  m = interpreter.Interpreter('grammar.lark')
  files = [ ]
  for arg in args:
    with open(arg, 'r') as f:
      files.append(f.read())
  
  for command in files:
    print(m.execute(command, 'file tester', 'test server'))
  
  return 0

if __name__ == '__main__':
  import sys
  exit_code = main(*sys.argv[1:])
  sys.exit(exit_code)

  
