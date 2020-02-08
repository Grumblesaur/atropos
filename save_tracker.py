import time

class SaveTracker(object):
  def __init__(self, save_interval=300):
    start_time = time.time()
    self.message_at = start_time 
    self.save_at    = start_time
    self.save_interval   = save_interval
    
  def update(self):
    self.message_at = time.time()
  
  def should_save(self):
    return time.time() - self.save_at > self.save_interval
  
  def saved(self):
    self.save_at = time.time()
  
