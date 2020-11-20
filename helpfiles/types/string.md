## String

String is an iterable type that holds text in Dicelang, which allows users to
create more literate outputs for their commands than mere numbers. Strings are
contained within quotation marks. Either "" or '' will work, as long as they
match. Use the opposite kind of quote to delimit a string when you need to use
quotes inside your string.

```
  "This is a string."
  'This is also a string.'
  "Use double quotes if you need apostrophes (')"
```

Nested quotes are technically possible, but require the string to be
constructed through concatenation. The result of such a string as it appears
in the chat won't necessarily be copyable back into a +roll command.

```
  'He said, "' + "I don't know what a 'mastiff' is, actually." + '"'
```

should come out looking like

```He said, "I don't know what a 'mastiff' is, actually."```

While string concatenation uses the `+` symbol, it does not have the same
properties as the `+` operation for numbers. With strings, concatenation is
not commutative -- order matters.

Since strings are iterable, they can be indexed. The first character of a
string has index 0.

```
  message = "Hello, world!";
  message[0]
  >>> 'H'
```

A string's length is the number of characters contained within.

```
  #""       ~ Length of empty string
  >>> 0
  
  #"Attack" ~ Length of a non-empty string
  >>> 6
```

Strings can be formatted with other values. See

```
  +atropos help operators format
  +atropos help operators interpolate
```

for more information.

