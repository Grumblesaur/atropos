## Functions

Functions are a type of object in Dicelang. A function is some code that a user
stores for later use, and can optionally take some parameters. A function is
defined with the following syntax.

```  (some, list, of, parameters) -> function_code```

Multiple parameters within the parentheses must be separated by commas. Unary
functions require no commas, and nullary functions use an empty pair of
parentheses. Since functions are objects, they can be assigned to a variable.

The function code must be either a single expression, or a code block. In a
function using a code block, the last expression evaluated in the function
determines the return value.

### Examples:
```
  foo = () -> 1          ~ Simple nullary function that always returns 1.

  square = (a) -> a * a  ~ Squares a number.

  divmod = (a, b) -> [a // b, a % b]  ~ Returns the integer quotient and
                                      ~ remainder of a / b.
  
  bar = (a, b, c) -> begin  ~ An example of a simple block function.
    z = a + b;              ~ New variables are created in the block's scope.
    y = c - z;              ~ Parameters are available in the function.
    y ** 3                  ~ Last expression, thus, the return value.
  end
```

### Calls:
```
  foo()
  >>> 1

  square(4)
  >>> 16

  divmod(9, 4)
  >>> [2, 1]
  
  bar(2, 3, 4)
  >>> -1
```


