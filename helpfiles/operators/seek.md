#### Seek (regex search)

`seek` is a string-matching operation which takes a string as its left operand
and a special string called a "pattern" as its right operand. A poattern is a
string that uses [regular expression syntax][1]. This operand returns a dict
with keys `start` and `end`. If a match is found, `start` is set to the index
of the string at the start of the match, and `end` is set to the index of the
string at the end of the match. If no match is found, `start` and `end` are
both set to `-1`.

If multiple matches are possible, only the first one is found.

Example:
```
  'Richard Richard Richard Richard' seek 'ard'
  >>> {'start' : 4, 'end' : 7}
  
  'rats live on no evil star' seek '\d'
  >>> {'start' : -1, 'end' : -1}
```


[1]: <https://docs.python.org/3/library/re.html#re-syntax> "Python regex syntax"


