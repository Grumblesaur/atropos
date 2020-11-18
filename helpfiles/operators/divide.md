#### Divide

`/` is a binary operator which returns the quotient of its left operand divided
by its right operand. It expects both its arguments to be numeric -- floating
point or integer. It will generate an error if the divisor (right operand) is
zero, or if either operand is non-numeric, but will otherwise always return a
floating point value.

Examples:
```
  1 / 5    ~ Division of int by int.
  >>> 0.2
  
  2.0 / 7  ~ Division of float by int.
  >>> 0.2857142857142857
  
  9 / 6.0  ~ Division of int by float.
  >>> 1.5
  
  -9.1 / 4.09  ~ Division of float by float.
  >>> -2.2249388753056234
```


