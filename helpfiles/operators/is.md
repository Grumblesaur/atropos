#### Is (identity)

`is` is the identity operator, *not* to be confused with `==`, which tests
for equality. `is` checks to see whether its left and right operands are the
exact same object, and not merely equal. This is useful for comparing to
`True`, `False`, and `Undefined`, which are all singleton objects.

In particular, this is useful to see whether a variable has been defined yet.

Examples:
```
  new_name is Undefined;
  >>> True, we have not defined new_name yet.
  
  new_name = 10;
  
  new_name is Undefined
  >>> False; we have defined it as 10.
```

While the syntax of Dicelang allows to check that two objects are different via

```
not (obj1 is obj2)
```

the more idiomatic way of doing it is

```
obj1 is not obj2
```

which eliminates a set of parentheses and conveys the point more legibly.

Examples:
```
  new_name is not Undefined;
  >>> False; we have not defined it in this example yet.
  
  new_name = 10;
  
  new_name is not Undefined;
  >>> True; we have now defined it.
```

