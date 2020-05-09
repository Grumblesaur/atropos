## Quickstart

This is a quick guide for some common operations when using Atropos. If you
want Atropos to see your message, make sure to start it with `+roll`. If this
would trigger another bot as well, you can use `+atropos roll` instead.

Roll dice (Examples)
```
  +roll 1d20    ~ a twenty-sided die
  +roll 4d6     ~ sum of 4 six-sided dice
  +roll 7d8h4   ~ sum of highest 4 of 7 eight-sided dice
  +roll 10d3l5  ~ sum of lowest 5 of 10 three-sided dice
  
  ~ Any number of dice or sides 1 or greater will work.
```

For the rest of the examples, I'm going to leave off the `+roll` prefix.

Multiply and divide (Examples)
```
  5 / 10      ~ gives 0.5
  8.8 / -2    ~ gives -4.4
  -3.0 * -3.0 ~ gives 9.0
  5 // 2      ~ gives 2  (// always gives an integer result)
```
Add and subtract (Examples)
```
  6 + 4   ~ gives 10
  5 - 6   ~ gives -1
```
Repeat (Example)
```
  4d6h3 ^ 6  ~ Does the following 6 times:
             ~   sums highest 3 of 4 six-sided dice
             ~   adds sum to a list.
             ~ Returns list.
```
These are all examples of expressions, which can be combined to your heart's
content. You can roll two different dice and add their totals together,
```
  1d6 + 1d10
```
or modify a roll
```
  1d100 - 10
  10 * 5d4
  10 / 1d20
```

Exponents (Examples)
```
  3 ** 2      ~ gives 9
  10 ** (-1)  ~ gives 0.1
```

Just like with regular math, Atropos' dice engine adheres to an order of
operations (also known as operator precedence). For the operations defined
above, the order of precedence is:
  * parentheses
  * dice
  * exponents
  * negative sign
  * multiplication and division
  * addition and subtraction

There are many more operations left out of the quickstart guide, but these are
all most games require. Other help topics will explain other features, and
elaborate on the ones listed.


