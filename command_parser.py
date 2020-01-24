#!/usr/bin/python3
from lark import Lark

def get_parser():
  with open('grammar.lark', 'r') as f:
    grammar = f.read()
  if not grammar:
    raise ValueError('grammar.lark file renamed or missing!')
  return Lark(grammar)

if __name__ == '__main__':
  tests = [
    '1.5',
  ]
  
  p = get_parser()
  for test in tests:
    print(p.parse(test).pretty())




