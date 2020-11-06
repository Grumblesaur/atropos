# Int

Integers represent whole numbers, negative and positive. Dicelang integers, as
implemented in Python, are not limited in magnitude.

Syntax:
```
  0      ~
  1      ~ You can enter an arbitrary number of digits, optionally
  -2     ~ headed by a negative sign.
  348    ~
  -20934 ~
```

Integers will mathematically interact with floating point values in a fairly
predictable way. Worth noting, the `/` division operator will always return a
floating point value between any numeric operands, while the `//` floor
division operator will always return an integral value.

The result of the `d` dice-rolling operator will always be an integer.

