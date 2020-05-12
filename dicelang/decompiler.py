class Decompiler(object):
  def __init__(self):
    self.indent = ' ' * 2
    self.level  = 0

  def binop_decompile(self, children):
    return (self.decompile(children[0]), self.decompile(children[1]))

  def decompile(self, tree):
    '''Recursively reconstruct a normalized source code form for an abstract
    syntax tree.'''
    if tree.data == 'start':
      out = '; '.join([self.decompile(child) for child in tree.children])
    elif tree.data == 'block':
      self.level += 1
      expressions = [self.decompile(child) for child in tree.children]
      indent = self.indent * self.level
      endent = self.indent * (self.level - 1)
      exprs = indent + f';\n{indent}'.join(expressions)
      out = f'begin\n{exprs}\n{endent}end'
      self.level -= 1
    
    elif tree.data == 'function':
      code = self.decompile(tree.children[-1])
      params = ', '.join([child.value for child in tree.children[:-1]])
      out = f'({params}) -> {code}'
    
    elif tree.data == 'for_loop':
      iterator = self.decompile(tree.children[0])
      expression = self.decompile(tree.children[1])
      code = self.decompile(tree.children[2])
      out = f'for {iterator} in {expression} do {code}'
    elif tree.data == 'while_loop':
      expression, code = self.binop_decompile(tree.children)
      out = f'while {expression} do {code}'
    elif tree.data == 'do_while_loop':
      code = self.decompile(tree.children[0])
      expression = self.decompile(tree.children[1])
      out = f'do {code} while {expression}'
    
    elif tree.data == 'conditional':
      out = self.decompile(tree.children[0])
    elif tree.data == 'if':
      condition, code = self.binop_decompile(tree.children)
      out = f'if {condition} then {code}'
    elif tree.data == 'if_else':
      condition, if_code, else_code = [self.decompile(child) for child in tree.children]
      out = f'if {condition} then {if_code} else {else_code}'
    
    elif tree.data == 'short_body':
      out = self.decompile(tree.children[0])
    elif tree.data == 'expression':
      out = self.decompile(tree.children[0])
    elif tree.data == 'import':
      out = self.decompile(tree.children[0])
    elif tree.data == 'standard_import':
      ident = self.decompile(tree.children[1])
      out = f'import {ident}'
    elif tree.data == 'as_import':
      ident = self.decompile(tree.children[1])
      alias = self.decompile(tree.children[2])
      out = f'import {ident} as {alias}'

    elif tree.data == 'deletion':
      out = self.decompile(tree.children[0])
    elif tree.data == 'delete_variable':
      ident = self.decompile(tree.children[0])
      out = f'del {ident}'
    elif tree.data == 'delete_element':
      ident = self.decompile(tree.children[0])
      subscripts = ''.join([f'[{self.decompile(child)}]' for child in tree.children[1:]])
      out = f'del {ident}{subscripts}'

    elif tree.data == 'assignment':
      out = self.decompile(tree.children[0])
    elif tree.data == 'setattr':
      chain = '.'.join([self.decompile(child) for child in tree.children[:-1]])
      expression = self.decompile(tree.children[-1])
      out = f'{chain} = {expression}'
    elif tree.data == 'identifier_set':
      ident, expr = self.binop_decompile(tree.children)
      out = f'{ident} = {expr}'
    elif tree.data == 'identifier_set_subscript':
      identifier = self.decompile(tree.children[0])
      subscripts = ''.join([f'[{self.decompile(c)}]' for c in tree.children[1:-1]])
      expression = self.decompile(tree.children[-1])
      out = f'{identifier}{subscripts} = {expression}'
    
    elif tree.data == 'identifier_get':
      out = self.decompile(tree.children[0])
    
    elif tree.data == 'if_expr':
      out = self.decompile(tree.children[0])
    elif tree.data == 'inline_if':
      if_expr = self.decompile(tree.children[0])
      condition = self.decompile(tree.children[1])
      else_expr = self.decompile(tree.children[2])
      out = f'{if_expr} if {condition} else {else_expr}'
    elif tree.data == 'inline_if_binary':
      if_expr, else_expr = self.binop_decompile(tree.children)
      out = f'{if_expr} if else {else_expr}'
    
    elif tree.data == 'repeat':
      out = self.decompile(tree.children[0])
    elif tree.data == 'repetition':
      left, right = self.binop_decompile(tree.children)
      out = f'{left} ^ {right}'
    elif tree.data == 'bool_or':
      out = self.decompile(tree.children[0])
    elif tree.data == 'logical_or':
      left, right = self.binop_decompile(tree.children)
      out = f'{left} or {right}'

    elif tree.data == 'bool_xor':
      out = self.decompile(tree.children[0])
    elif tree.data == 'logical_xor':
      left, right = self.binop_decompile(tree.children)
      out = f'{left} xor {right}'

    elif tree.data == 'bool_and':
      out = self.decompile(tree.children[0])
    elif tree.data == 'logical_and':
      left, right = self.binop_decompile(tree.children)
      out = f'{left} and {right}'

    elif tree.data == 'bool_not':
      out = self.decompile(tree.children[0])
    elif tree.data == 'logical_not':
      operand = self.decompile(tree.children[1])
      out = f'not {operand}'
    
    elif tree.data == 'comp':
      out = self.decompile(tree.children[0])
    elif tree.data == 'comp_math':
      operands_and_operators = [self.decompile(child) for child in tree.children]
      out = ' '.join(operands_and_operators)
    elif tree.data == 'math_comp':
      out = tree.children[0].value
    elif tree.data == 'comp_obj':
      out = ' '.join([self.decompile(child) for child in tree.children])
    elif tree.data == 'obj_comp':
      out = "is" if len(tree.children) == 1 else "is not"
    elif tree.data == 'present':
      left, right = self.binop_decompile(tree.children)
      out = f'{left} in {right}'
    elif tree.data == 'absent':
      left, right = self.binop_decompile(tree.children)
      out = f'{left} not in {right}'
    
    elif tree.data == 'shift':
      out = self.decompile(tree.children[0])
    elif tree.data == 'left_shift':
      left, right = self.binop_decompile(tree.children)
      out = f'{left} << {right}'
    elif tree.data == 'right_shift':
      left, right = self.binop_decompile(tree.children)
      out = f'{left} >> {right}'
    
    elif tree.data == 'arithm':
      out = self.decompile(tree.children[0])
    elif tree.data == 'addition':
      left, right = self.binop_decompile(tree.children)
      out = f'{left} + {right}'
    elif tree.data == 'subtraction':
      left, right = self.binop_decompile(tree.children)
      out = f'{left} - {right}'
    elif tree.data == 'catenation':
      left, right = self.binop_decompile(tree.children)
      out = f'{left} $ {right}'
    
    elif tree.data == 'term':
      out = self.decompile(tree.children[0])
    elif tree.data == 'multiplication':
      left, right = self.binop_decompile(tree.children)
      out = f'{left} * {right}'
    elif tree.data == 'division':
      left, right = self.binop_decompile(tree.children)
      out = f'{left} / {right}'
    elif tree.data == 'remainder':
      left, right = self.binop_decompile(tree.children)
      out = f'{left} % {right}'
    elif tree.data == 'floor_division':
      left, right = self.binop_decompile(tree.children)
      out = f'{left} // {right}'
    
    elif tree.data == 'factor':
      out = self.decompile(tree.children[0])
    elif tree.data == 'negation':
      out = f'-{self.decompile(tree.children[0])}'
    elif tree.data == 'absolute_value':
      out = f'+{self.decompile(tree.children[0])}'
    
    elif tree.data == 'power':
      out = self.decompile(tree.children[0])
    elif tree.data == 'exponent':
      left, right = self.binop_decompile(tree.children)
      out = f'{left} ** {right}'
    elif tree.data == 'logarithm':
      left, right = self.binop_decompile(tree.children)
      out = f'{left} %% {right}'
    
    elif tree.data == 'reduction':
      out = self.decompile(tree.children[0])
    elif tree.data == 'sum_or_join':
      out = f'&{self.decompile(tree.children[0])}'
    elif tree.data == 'length':
      out = f'#{self.decompile(tree.children[0])}'
    elif tree.data == 'selection':
      out = f'@{self.decompile(tree.children[0])}'
    elif tree.data == 'minimum':
      out = f'!<{self.decompile(tree.children[0])}'
    elif tree.data == 'maximum':
      out = f'!>{self.decompile(tree.children[0])}'
    elif tree.data == 'flatten':
      out = f'|{self.decompile(tree.children[0])}'
    elif tree.data == 'stats':
      out = f'?{self.decompile(tree.children[0])}'
    elif tree.data == 'sort':
      out = f'<>{self.decompile(tree.children[0])}'
    elif tree.data == 'shuffle':
      out = f'><{self.decompile(tree.children[0])}'
    
    elif tree.data == 'slice':
      out = self.decompile(tree.children[0])
    elif tree.data == 'whole_slice':
      out = f'{decompile(tree.children[0])}[:]'
    elif tree.data == 'start_slice':
      indexable, start = self.binop_decompile(tree.children)
      out = f'{indexable}[{start}:]'
    elif tree.data == 'start_step_slice':
      indexable, start, step = [self.decompile(child) for child in tree.children]
      out = f'{indexable}[{start}::{step}]'
    elif tree.data == 'start_stop_slice':
      indexable, start, stop = [self.decompile(child) for child in tree.children]
      out = f'{indexable}[{start}:{stop}]'
    elif tree.data == 'fine_slice':
      indexable, start, stop, step = [self.decompile(child) for child in tree.children]
      out = f'{indexable}[{start}:{stop}:{step}]'
    elif tree.data == 'stop_slice':
      indexable, stop = self.binop_decompile(tree.children)
      out = f'{indexable}[:{stop}]'
    elif tree.data == 'stop_step_slice':
      indexable, stop, step = [self.decompile(child) for child in tree.children]
      out = f'{indexable}[:{stop}:{step}]'
    elif tree.data == 'step_slice':
      indexable, step = self.binop_decompile(tree.children)
      out = f'{indexable}[::{step}]'
    elif tree.data == 'not_a_slice':
      indexable, index = self.binop_decompile(tree.children)
      out = f'{indexable}[{index}]'
    
    elif tree.data == 'application':
      out = self.decompile(tree.children[0])
    elif tree.data == 'apply':
      left, right = self.binop_decompile(tree.children)
      out = f'{left} -: {right}'
    
    elif tree.data == 'die':
      out = self.decompile(tree.children[0])
    elif tree.data == 'scalar_die_all':
      dice, sides = self.binop_decompile(tree.children[::2])
      out = f'{dice} d {sides}'
    elif tree.data == 'scalar_die_highest':
      dice, sides, keep = [self.decompile(child) for child in tree.children[::2]]
      out = f'{dice} d {sides} h {keep}'
    elif tree.data == 'scalar_die_lowest':
      dice, sides, keep = [self.decompile(child) for child in tree.children[::2]]
      out = f'{dice} d {sides} l {keep}'
    elif tree.data == 'vector_die_all':
      dice, sides = self.binop_decompile(tree.children[::2])
      out = f'{dice} r {sides}'
    elif tree.data == 'vector_die_highest':
      dice, sides, keep = [self.decompile(child) for child in tree.children[::2]]
      out = f'{dice} r {sides} h {keep}'
    elif tree.data == 'vector_die_lowest':
      dice, sides, keep = [self.decompile(child) for child in tree.children[::2]]
      out = f'{dice} r {sides} l {keep}'
    
    elif tree.data == 'plugin_op':
      out = self.decompile(tree.children[0])
    elif tree.data == 'plugin_call':
      name, operand = self.binop_decompile(tree.children)
      out = f'{name} :: {operand}'
    
    elif tree.data == 'call_or_atom':
      out = self.decompile(tree.children[0])
    elif tree.data == 'function_call':
      handle = self.decompile(tree.children[0])
      arguments = ', '.join([self.decompile(child) for child in tree.children[1:]])
      out = f'{handle}({arguments})'
    
    elif tree.data == 'get_attribute':
      out = self.decompile(tree.children[0])
    elif tree.data == 'getattr':
      obj = self.decompile(tree.children[0])
      chain = '.'.join([self.decompile(child) for child in tree.children[1:]])
      out = f'{obj}.{chain}'
    
    elif tree.data == 'regex':
      out = self.decompile(tree.children[0])
    elif tree.data == 'match':
      text, pattern = [self.decompile(c) for c in tree.children[0::2]]
      out = f'{text} like {pattern}'
    elif tree.data == 'search':
      text, pattern = [self.decompile(c) for c in tree.children[0::2]]
      out = f'{text} seek {pattern}'
    
    elif tree.data == 'reflection':
      out = self.decompile(tree.children[0])
    elif tree.data == 'typeof':
      out = f'typeof {self.decompile(tree.children[1])}'
    
    elif tree.data == 'atom':
      out = self.decompile(tree.children[0])
    elif tree.data == 'number_literal':
      out = tree.children[-1].value
    elif tree.data == 'string_literal':
      out = tree.children[-1].value
    elif tree.data == 'boolean_literal':
      out = tree.children[-1].value
    elif tree.data == 'undefined_literal':
      out = tree.children[-1].value
    
    elif tree.data == 'list_literal':
      out = self.decompile(tree.children[0])
    elif tree.data == 'populated_list':
      chain = ', '.join([self.decompile(child) for child in tree.children])
      out = f'[{chain}]'
    elif tree.data == 'empty_list':
      out = '[]'
    
    elif tree.data == 'tuple_literal':
      out = self.decompile(tree.children[0])
    elif tree.data == 'mono_tuple':
      out = f'({self.decompile(tree.children[0])},)'
    elif tree.data == 'multi_tuple':
      chain = ', '.join([self.decompile(child) for child in tree.children])
      out = f'({chain})'
    elif tree.data == 'empty_tuple':
      out = '()'
    
    elif tree.data == 'range_list':
      start, stop = self.binop_decompile(tree.children)
      out = f'[{start} to {stop}]'
    elif tree.data == 'range_list_stepped':
      start, stop, step = [self.decompile(child) for child in tree.children]
      out = f'[{start} to {stop} by {step}]'
    elif tree.data == 'closed_list':
      start, stop = [self.decompile(child) for child in tree.children]
      out = f'[{start} through {stop}]'
    elif tree.data == 'closed_list_stepped':
      start, stop, step = [self.decompile(child) for child in tree.children]
      out = f'[{start} through {stop} by {step}]'
    
    elif tree.data == 'dict_literal':
      out = self.decompile(tree.children[0])
    elif tree.data == 'empty_dict':
      out = '{}'
    elif tree.data == 'populated_dict':
      chain = ', '.join([self.decompile(child) for child in tree.children])
      out = '{' + f'{chain}' + '}'
    elif tree.data == 'key_value_pair':
      key, value = self.binop_decompile(tree.children)
      out = f'{key}: {value}'
    
    elif tree.data == 'identifier':
      out = self.decompile(tree.children[0])
    elif tree.data == 'scoped_identifier':
      out = tree.children[0].value
    elif tree.data == 'private_identifier':
      out = f'my {tree.children[-1].value}'
    elif tree.data == 'server_identifier':
      out = f'our {tree.children[-1].value}'
    elif tree.data == 'global_identifier':
      out = f'global {tree.children[-1].value}'
    elif tree.data == 'core_identifier':
      out = f'core {tree.children[-1].value}'
    elif tree.data == 'priority':
      out = f'({self.decompile(tree.children[0])})'
    else:
      print('missed decompiling:', tree.data)
      out = f'__UNIMPLEMENTED__: {tree.data}'
    
    return out


