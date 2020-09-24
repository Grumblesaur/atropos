#### For (fixed iteration)

`for` is a loop construct which executes a fixed number of times. It has the
form:

```for iterator in iterable do expression```

It is often useful to use a `block` as the expression, as a `for` loop will
usually need to do more than one operation. As the entire construct is itself
an expression, it will return a value. This value is a list containing the
value of `expression` section after each iteration.

`iterator` is an identifier which the user defines in the header of the `for`
loop and which has scope only within the loop. `iterable` is a list, dict,
tuple, or string. `iterator` takes a new value from `iterable` during each
iteration of the loop, which is in order from first index to last index for the
types `list`, `string`, and `tuple`, and in an implementation-defined order for
`dict`s, for which the `key`, not the `value`, is taken.

Examples:
```
  for x in [1, 2, 4, 8, 16] do begin
    x * 3
  end
  >>> [3, 6, 12, 24, 48]
```

