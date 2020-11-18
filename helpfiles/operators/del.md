#### Deletion (variable removal)

`del` is the deletion operator, which allows a user to destroy a variable they
are no longer using. It is a unary operator, and so only has a right operand.
Its operand must be an identifier, or an attribute or indexing operation on
some object.

When the item is deleted, its value is returned for capture, which allows for
easy move operations.

Examples
```
  global x = 10;
  del global x;  ~ simple delete with a global variable.
  >>> 10
  
  my z = {'a' : 4, 'z' : 9};
  del my z.a  ~ attribute delete with a private variable.
  >>> 4
  
  foo = {'bar' : 10, 'baz' : 50};
  del foo['bar']  ~ index delete with an untagged variable.
  >>> 10
  
  global foo = del foo ~ Move/rename foo to a global
  >>> {'baz' : 50}
```


