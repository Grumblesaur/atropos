#### Block (compound expression)

A block is initiated with the word `begin` and terminated with the word `end`.
The body of a block is a sequence of expressions, which may or may not have
side effects. These expressions must be separated by `;`. Optionally, a `;`
may also trail the last expression.

As blocks are themselves expressions, they return a value. The return value of
a block expression is the value of the last expression inside the block.

Additionally, blocks may form the body of functions, and can be used with
conditional structures. When the interpreter control enters a block, the
a new scope is pushed onto the stack. Variables defined inside a block will
be destroyed when control exits the block.

Examples
```
  ~ A block as a simple expression.
  average_d4_roll = begin
    v = [1, 2, 3, 4];
    sum = &v;
    sum / #v
  end;

  >>> 2.5
```  

```
  ~ A block as the body of a condition or a loop.
  x = 10;
  squares = [ ];
  while x > 0 do begin
    squares = squares + [x ** x];
    x = x - 1
  end;
    
  if #squares == 10 then begin
    "We squared 10 numbers!"
  end else begin
    "We only squared {} numbers..." %% #squares
  end;
  
  >>> "We squared 10 numbers!"
```


    



