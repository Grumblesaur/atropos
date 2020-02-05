from dicelang.undefined import Undefined
# import plugins here


# associate a name for the plugin with the function in its API to call
operations = {
  
}

aliases = {

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
