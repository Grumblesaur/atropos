#### Greater than-equal to

`>=` is a non-strict inequality operator. It will compare values of the same
type according to that type's defined means of ordering (implementation-defined
by Python), and return `True` if the left operand is greater than or equal to
the right operand, and `False` otherwise. If the operands are not of the same
type (floating point and integer types are both considered "numeric" for this
purpose), an error will be raised.

Examples:
```
  1.2 >= 1
  >>> True
  
  's' >= 't'
  >>> False
  
  's' > 2
  >>> TypeError: `>=` not supported between instances of 'str' and 'int'
```

