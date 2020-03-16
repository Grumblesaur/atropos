#### Assignment (variable creation)

`=` is the assignment operator, which enables the creation and update of
variables. The left operand must be an identifier, and the right operand can be
any valid expression. If the identifier is not currently in use, a new variable
is created for it and assigned the value of the right operand. Otherwise, the
variable is updated to have the value of the right operand. It returns the
value of its right operand for chained assignments.

Examples:
```
  x = 1   ~ Creates or updates a value called x in the current scope with the
          ~ value of 1. Outside of blocks or functions, this is automatically
          ~ the global scope.
  
  global x = 1   ~ Creates or updates a value called x in the global scope,
                 ~ regardless of the location of this expression.
  
  my y = 'g'     ~ Creates or updates a user-owned variable called y with the
                 ~ value 'g'.
  
  our list = [1, 2, 3, 4]   ~ Creates or updates a server-owned variable called
                            ~ list with the value of [1, 2, 3, 4].
```

Additionally, attributes or indices of an object can be assigned.

Examples:
```
  obj = {};   ~ Creates a dict called obj.
  obj.x = 1   ~ Creates an attribute of obj called x with the value of 1.
```

This is equivalent to:

```
  obj = {};
  obj['x'] = 1
```


