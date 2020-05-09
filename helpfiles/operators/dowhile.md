#### Do-while (indefinite iteration)

`do-while` is a loop construct which always executes its associated body code
at least once, even if its condition starts out false. It has the form:

```do expression while condition```

It is often useful to use a `block` as the expression, as a `do-while` loop
will usually need to do more than one operation. As the entire construct is
itself an expression, it will return a value. This value is a list of the
values of each iteration of the `do-while` loop's expression.

Examples
```
  ~ This is an example for use directly in a command. As do-while loops push
  ~ their own scope, retrieving and assigning variables sometimes works in an
  ~ unintuitive manner, since scoped variables (that is, without `core`, `our`,
  ~ `global`, or `my`) behave as `our` outside of a block or function scope,
  ~ but as a local variable inside a block or function scope.
  ~ A full explanation available at "+help scope".
  
  our x = 7;
  do begin
    our x = our x - 1;
    our x ** 2
  end while our x > 0;
  >>> [36, 25, 16, 9, 4, 1, 0]
  
  ~ Function example (the scoping is more intuitive and consistent here,
  ~ and you're more likely to need a loop inside a function than outside
  ~ anyway.
  w = (x) -> begin
    do begin
      x = x - 1;
      x ** 2;
    end while x > 0;
  end;
  w(10)
  >>> [81, 64, 49, 36, 25, 16, 9, 4, 1, 0]
```

