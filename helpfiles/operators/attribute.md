#### Attribute

`.` is the attribute operator, which provides access to a field of a dict. The
right operand must be an identifier, but the left can be a dict literal or an
identifier. If the access is for an assignment, the left operand of `.` must
be an identifier too.

When not part of an assignment, the value stored at the attribute is retrieved
by its name and returned. If an attribute with that name does not exist, an
error will be raised.

When part of an assignment, the object will be given a new attribute with the
value on the right side of the equals sign, and that same value will be
returned.

Examples (assignments):
```
  character = { };             ~ Create a new dict called character
  character.name = 'Stewart';  ~ Add an attribute to the character called name
                               ~ with the value of 'Stewart'.
  character.age = 37;          ~ Add an attribute called age with the value of 37.
  character.abilities = {};    ~ Dicts are allowed to nest.
  
  character.abilities.strength = 10;  ~ This syntax is recursive, allowing for
                                      ~ objects with complex structure.
  character.abilities.charisma = 16;  ~ If you've used JavaScript, it works like
                                      ~ JavaScript's object prototyping syntax.
```

Examples (retrievals):
```
  character.name
  >>> 'Stewart'
  
  character.abilities.charisma
  >>> 16

```

The attribute operator has some equivalence with the index `[ ]` operator for
dicts. Specifically, the following is true:

```
  character.name == character['name']
  >>> True
  
  (character.level = 6) == (character['level'] = 6)
  >>> True
```



