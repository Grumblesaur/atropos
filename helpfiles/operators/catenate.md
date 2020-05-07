#### Catenate

`$` is the catenation operator, which attaches the digits of two numbers
together. The digits of the right operand are attached, from highest order
position to lowest order position, to the low order position of the left
operand.

This operator additionally works with any string representations of non-
negative integers, although leading zeroes will be ignored on the left-hand
operand.

A useful behavior of this operator is that it allows for the truncation of
floating point numbers when the left operand is zero.

Examples
```
  4 $ 10    ~ Integer and integer.
  >>> 410
  
  "6" $ 8   ~ Integer string and integer.
  >>> 68
  
  10 $ "0"  ~ Integer and integer string.
  >>> 100
  
  0 $ 1.5   ~ Floating point truncation.
  >>> 1
  
  -43 $ 9   ~ Negatives work on the left operand.
```

