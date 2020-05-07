#### Choice

`@` is the choice operator, which randomly selects an item from a list, a dict,
a string, or a tuple. It is a unary operator, and so only has a right operand.

When the operand is a list, a string, or a tuple, it will return a single item
from that object. When the operand is a dict, it returns a list containing the
key and the value of the selected item, with the key coming first.

This can be used to construct "dice" with non-sequential sides, or with sides
that don't even have numbers at all.

Examples
```
  @(1, 3, 'a', 'q')  ~ Tuple example
  ~ Possible output:
  >>> 'a'
  
  @[10, 10, 6, 6, 2, 2]  ~ List example
  ~ Possible output:
  >>> 10
  
  @'string'  ~ String example
  ~ Possible output:
  >>> 'g'
  
  @{'a' : 1, 'b' : 2, 'c' : 3}
  ~ Possible output:
  >>> ['a', 1]
```

Such an operation can be saved for future use, to simulate a special die:
```
  odds = () -> @[1, 3, 5, 7, 9];
  odds()
  ~ Possible output:
  >>> 7
```


