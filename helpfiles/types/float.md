## Float

Floating point is a numeric type in Dicelang, which approximates a wide range
of real numbers. Dicelang inherits its implementation of floats from Python,
which in turn is based on IEEE 754.

None of this is important, though. Use this type when you need a numeric
representation with a fractional part and you don't need to worry about small
rounding errors.

Syntax:
```
  1.05  ~ Whole part, decimal point, fractional part.
  .05   ~ Decimal point, fractional part.
  1.    ~ Decimal point, fractional part.
  
  -1.05 ~
  -.05  ~ The same, but negative.
  -1.   ~
```

Floating point values will mathematically interact with integers in a fairly
predictable way. Worth noting, the `/` division operator will always return a
floating point value, while the `//` floor division operator will always return
an integral value.

Additionally, the `$` numeric concatenation operator will convert all numeric
values to integers first, so `1.5 $ 3.5` reduces to `13`.


