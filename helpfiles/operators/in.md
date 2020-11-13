#### In (Membership)

`in` is the membership test operator. It assumes that its left operand is an
element and that its right operand is a collection to search for the element
in. If the element can be found, `in` returns `True`, otherwise `False`.

Examples:
```
  10 in [5 through 30 by 5] ~ 10 is a multiple of 5 <= 30
  >>> True
  
  6 in ((x) -> x**2) -: [1 through 10] ~ 6 is not one of the first 10 squares
  >>> False
```

While the syntax of Dicelang allows to check the lack of membership via

```not (element in collection)```

the more idiomatic way of doing so is

```element not in collection```

which eliminates a set of parentheses and conveys the point more legibly.

Examples:
```
  'age' not in {'name' : 'Dave', 'gender' : 'm'}
  >>> True
  
  'vi' not in 'sieve'
  >>> True
```

When using strings as the operands, `in` and `not in` will treat their left
operands as substrings to match, looking for the presence or absence of the
characters in the right operand.

