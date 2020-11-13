#### Less than-equal to

`<=` is a non-strict inequality operator. It will compare the values of the
same type according to that type's defined means of ordering (implementation-
defined by Python), and return `True` if the left operand is less than or equal
to the right operand, and `False` otherwise. If the operands are not of the
same type (floating point and integer types are both considered "numeric" for
this purpose), an error will be raised.

Examples:
```
  40 <= 100
  >>> True
  
  -10 <= -11.1
  >>> False
  
  'cat' <= 'hat'
  >>> True
  
  () <= 40
  >>> TypeError: `<=` not supported between instances of `tuple` and `int`
```

