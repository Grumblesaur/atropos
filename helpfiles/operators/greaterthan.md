#### Greater than

`>` is a strict inequality operator. It will compare values of the same type
according to that type's defined means of ordering (implementation-defined by
Python) and return `True` if the left operand is strictly greater than the
right operand, and `False` otherwise. If the operands are not of the same type
(floating point and integer types are both considered "numeric" for this
purpose), an error will be raised.

Examples:
```
  0 > -1
  >>> True
  
  'cork' > 'corn'
  >>> False
  
  1 > []
  >>> TypeError: '>' not supported between instances of 'int' and 'list'
```
