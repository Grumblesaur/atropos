#### If (conditional)

`if` is a conditional construct which takes multiple forms. The first is a
simple clausal form:

```
if condition then expression
```

When `condition` is `True`, then the expression is evaluated, and the if clause
returns that value. Otherwise, `Undefined` is returned.

Example:
```
  y = if x > 10 then x - 10;
```

In this example, `y` will be set to the value of `x - 10` if `x > 10`,
otherwise, it will be set to `Undefined`.

Next is the compound clausal form:

```
if condition then expression1 else expression2
```

When `condition` is `True`, then `expression1` is evaluated, and the if-else
clause returns that value, otherwise, `expression2` is evaluated, and the if-
else clause returns that instead. `expression2` can be another conditional, to
form a chain:

```
  if condition1 then
    expression1
  else if condition2 then
    expression2
  else
    expression3
```

This can be useful for selecting a value, and blocks can be used to execute
more complex sequences of code for a given condition.

Example:
```
  result = 1d6;
  score = if result == 1 then
    result
  else if score in (2, 3, 4, 5) then
    result // 2
  else begin
    bonus = 1d6;
    (result // 2) + bonus
  end
```

In an if-else chain, only one expression (or block) will be evaluated. The
first condition in top-to-bottom order which evaluates True will have its
corresponding expression executed, ignoring the rest of the chain. 

The last form is of a Python-like inline form, akin to the more laconic `? :`
ternary operator of C-like programming languages:

```
expression1 if condition else expression2
```

`condition` is evaluated. If it is `True`, then `expression1`'s value is
returned, otherwise `expression2`'s value is returned.

As before the `expression`s can be replaced by blocks of expressions, but due
to the unconventional order for this expression's syntax, it's more advisable
to reserve this form for simple inline selection of values.

