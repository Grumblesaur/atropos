## Dictionary

Dictionaries are a type of object in Dicelang, which are a mapping of "keys" to
"values". As Dicelang is implemented in Python, Dicelang's dicts inherit their
features and rules from Python's dicts.

A key must be a hashable value. The hashable types in Dicelang are:
  * integer
  * float
  * string
  * tuple

The value that a given key refers to can be of any type, including another dict.

Syntax:
```
  { }       ~ This is an empty dict, with no keys (and no values) defined.
  
  {'a' : 1} ~ This is a dict with one key-value pair defined. A key is always
            ~ on the left-hand side of the colon, and the value is on the right.
  
  ~ You can have arbitrarily many key-value pairs in a dictionary. The pairs
  ~ must be separated by commas.
  
  {'a' : 1, 'b' : (x) -> x / (x + 1)}
```

Key-value pairs can be added, accessed, and removed from a dict over the course
of its lifetime.

```
  things = {'a' : 1, 'b' : 2, 'c' : 3, 'd' : 4};  ~ define the dict
  
  things['a'] = 5;  ~ Update the value for the key 'a' to 5
  
  things['e'] = 1;  ~ Create a new key 'e' with the value 1
  
  thing = things['c']  ~ Get the value paired with the key 'c' and capture it
                       ~ in a variable.
  
  things[(1, 2, 3)] = 6  ~ Keys don't have to be just strings.
  
  del things['b']  ~ Remove the value at key 'b'. This returns the value that
                   ~ was stored at key 'b'.
```

As the brackets and quotation marks can be a lot to type at times, there is a
shorthand accessible for any keys that start with a letter or an underscore,
and are a series of letters, digits, and underscores.

```
  things.a = 5;  ~ This is the same as   things['a'] = 5
  del things.b   ~ This is the same as   del things['b']
  things.c;      ~ This is the same as   things.c
```

By using strings as keys and functions as values, you can create a simple
library of functions.
