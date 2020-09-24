#### Equal to

`==` is the equality operator. It compares the value of its operands. If the
operands have the same value, it returns `True`, otherwise it returns `False`.

Floating point values and integer values that are logically the same value
are treated as equivalent.

Examples:
```
  1.0 == 1
  >>> True
  
  (1, 2, 3) == (1, 2, 3)
  >>> True
  
  (1, 2, 3) == [1, 2, 3]
  >>> False
  
  'STRING' == 'string'
  >>> False
```

