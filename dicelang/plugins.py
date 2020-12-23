import os
from dicelang.undefined import Undefined
# import plugins here
from tesnames.generator import generate_name
from timestamp.timestamp import stamp
from behindthename import RandomName

def btn_name_requestor():
  path = os.environ['BEHINDTHENAME_API_KEY_FILE']
  key = None
  try:
    with open(path, 'r') as f:
      key = f.read().strip()
  except Exception:
    pass
  
  if key is None:
    return lambda s: Undefined
  
  def name_generator(d):
    random = RandomName(api_key=key, **d)
    data = random.get()
    return ' '.join(data['names'])
  
  return name_generator

# associate a name for the plugin with the function in its API to call
operations = {
  'tesnames' : generate_name,
  'timestamp': stamp,
  'behindthename': btn_name_requestor(),
}

aliases = {
  'name'  : 'tesnames',
  'names' : 'tesnames',
  'time'  : 'timestamp',
  'realname': 'behindthename',
}

def lookup(plugin_alias_or_name):
  try:
    name = aliases[plugin_alias_or_name]
  except KeyError:
    name = plugin_alias_or_name
  try:
    callee = operations[name]
  except KeyError:
    callee = lambda arg: Undefined
  return callee


