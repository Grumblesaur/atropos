from lark import Lark
with open('grammar.lark', 'r') as f:
  grammar = f.read()

if not grammar:
  raise ValueError('grammar.lark file renamed or missing!')

parser = Lark(grammar)

tests = [
  '4d4',
  '1 + 7',
  'x = 9',
  '-9 / 3',
  '3 r 6',
]

for test in tests:
  print(parser.parse(test))



