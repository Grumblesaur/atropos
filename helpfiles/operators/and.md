#### And (boolean conjunction)

`and` is a binary operator with short-circuiting behavior. If its left operand
has a truthy value, it returns its right operand's value. Otherwise, it returns
its left operand's value.

Examples:
```
  1 and 2
  >>> 2
  
  True and False
  >>> False
  
  False and 'a'
  >>> False
  
  0 and [ ]
  >>> 0
```


