class PrintQueue(object):
  def __init__(self):
    self.queues = { }
  
  def append(self, user, msg):
    try:
      self.queues[user].append(msg)
    except KeyError:
      self.queues[user] = [msg]
    return len(msg)
  
  def flush(self, user):
    try:
      out = ''.join(self.queues[user])
      del self.queues[user]
    except KeyError:
      out = ''
    return out

