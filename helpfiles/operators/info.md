#### Info / Number summary

`?` is a unary operator which expects a collection of numbers, and returns
a dict of statistics on those numbers.

Example (possible output):
```
  ?(100r100) ~ Take the stats on 100 random numbers 1 through 100.
  >>> {
    'average' : 47.04,
    'minimum' : 1,
    'median'  : 42.5,
    'maximum' : 100,
    'size'    : 100,
    'sum'     : 4707,
    'stddev'  : 30.070003325573477,
    'q1'      : 19.0,
    'q3'      : 73.5
  }
```

This dict can be saved, accessed, and mutated like any other dict.

