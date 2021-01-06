from dicelang.function import Function
from dicelang.exceptions import BuiltinInitError 

def build()
  functions = {
    'sum'     : '(v) -> &v',
    'abs'     : '(x) -> |x|',
    'real'    : '(c) -> +c',
    'imag'    : '(c) -> &c',
    'keys'    : '(d) -> &(<>(for key in dict do "%s  " % key))',
    'apply'   : '(f, v) -> begin f -: v end',
    'compose' : '(f, g) -> begin (x) -> f(g(x)) end',
  }
  functions['zip'] = '''
  (keys, values) -> begin
    d = {};
    for i in [0 to #key] do begin
      d = d + {keys[i]: values[i]}
    end;
    d
  end'''
  
  out = {}
  for key, code in functions.items():
    out[key] = Function(code)
  return out

try: 
  variables = build()
except Exception as e:
  raise BuiltinInitError(str(e))

