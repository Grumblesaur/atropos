#### Like (regex match)

`like` is a string-matching operation which takes a string as its left operand
and a special string called a "pattern" as its right operand. A pattern is a
string that uses [regular expression syntax][1]. If the left operand matches
the pattern, this operation returns True, otherwise False.

Examples:
```
  'a' like '.' ~ match a single character that isn't a newline
  >>> True
  
  '.' like '\.' ~ match an actual dot
  >>> True
  
  '298374' like '\d+' ~ match one or more digits
  >>> True
  
  'Steve' like '.*eve.*' ~ match if substring 'eve' is present
  >>> True
  
  '666' like '6{2}' ~ match exactly two 6s
  >>> False
  
  'd' like '[abc]' ~ match if single character from set a, b, or c
  >>> False
```


[1]: <https://docs.python.org/3/library/re.html#re-syntax> "Python regex syntax"

