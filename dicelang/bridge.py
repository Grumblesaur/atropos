from dicelang import kernel

def get_function_call_handler():
  return kernel.handle_instruction

def get_decompiler():
  return kernel.decompile


