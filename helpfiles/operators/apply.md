#### Apply / map

`-:` is the apply operator. It expects its left operand to be a function, and
its right operand to be a list. For each element of the list, it calls the
function on that element, and appends the result to the new list, and returns
the new list when finished.

Examples:
```
  ((x) -> x ** 2) -: [1, 2, 3, 4]
  >>> [1, 4, 9, 16]
  
  half = (x) -> x / 2
  half -: [1, 2, 3, 4]
  >>> [0.5, 1, 1.5, 2]
```

