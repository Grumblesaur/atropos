from dicelang.function import Function
from dicelang.exceptions import BuiltinInitError 

def build():
  functions = {
    'sum'     : '(v) -> &v',
    'abs'     : '(x) -> |x|',
    'real'    : '(c) -> +c',
    'imag'    : '(c) -> &c',
    'keys'    : '(d) -> &(<>(for key in d do "%s  " % key))',
    'apply'   : '(f, v) -> begin f -: v end',
    'compose' : '(f, g) -> begin (x) -> f(g(x)) end',
    'product' : '(v) -> begin x = 1; for n in v do x = x * n; x end',
    'coinflip': '() -> @["heads", "tails"]',
  }
  functions['zip'] = '''
  (keys, values) -> begin
    d = {};
    for i in [0 to #keys] do begin
      d = d + {keys[i]: values[i]}
    end;
    d
  end'''
  
  functions['reduce'] = '''
  (func_binary, v) -> begin
    out = v[0];
    for item in v[1:] do begin
      out = func_binary(out, item)
    end;
    out
  end'''
  
  functions['copy'] = '''
  (obj) -> begin
    new = Undefined;
    if typeof obj == 'dict' then begin 
      new = {};
      for key in obj do begin
        new[key] = obj[key]
      end;
      new
    end else if typeof obj == 'list' then begin
      new = obj[:]
    end else begin
      new = obj
    end;
    return new
  end'''
  
  out = {}
  for key, code in functions.items():
    out[key] = Function(code)
  return out

try: 
  variables = build()
except Exception as e:
  raise BuiltinInitError(str(e))

