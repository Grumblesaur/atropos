#### Dice
`d` and `r` are operators which generate random numbers so as to simulate real
tabletop dice. Dice expressions can have suffixes with `h` or `l`. All of the
operands of these phrases must be natural numbers (non-negative integers).

`d` and `r` are both binary operators, where the left operand is the number of
dice to roll, while the right operand is the number of sides of each die. The
dice are always sequentially numbered, from 1 to number of sides, inclusive.
`d` will always sum the dice, while `r` will return a list of the individual
rolls.

`h` and `l` are the "keep" suffixes. `h` means "keep the highest n dice", while
`l` means "keep the lowest n dice". These cannot be used outside the context of
`d` or `r`.

Examples
```
  3d6  ~ Simple d operation
  ~ Possible output anywhere between 3 and 18 inclusive:
  >>> 8
  

  5r20  ~ Simple r operation
  ~ Possible output is 5 numbers anywhere between 1 and 20 inclusive:
  >>> [5, 2, 13, 19, 8]
  
  
  4d6h3  ~ Keep-highest d operation
  ~ Possible output is anywhere between 3 and 18 inclusive:
  >>> 9
  
  
  3d20l2  ~ Keep-lowest d operation
  ~ Possible output is anywhere between 2 and 40 inclusive:
  >>> 14

  
  6r6h3  ~ Keep-highest r operation
  ~ Possible output is 3 numbers between 1 and 6 inclusive:
  >>> [6, 5, 3]
  
  
  7r9l4  ~ Keep-lowest r operation
  ~ Possible output is 4 numbers anywhere between 1 and 9 inclusive:
  >>> [1, 2, 2, 3]
```

