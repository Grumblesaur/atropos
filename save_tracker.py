import time

class SaveTracker(object):
  def __init__(self, save_interval=300, backup_interval=1800):
    start_time = time.time()
    self.message_at = start_time 
    self.save_at    = start_time
    self.backup_at  = start_time
    
    self.save_interval   = save_interval
    self.backup_interval = backup_interval
    
  def update(self):
    self.message_at = time.time()
  
  def should_save(self):
    return time.time() - self.save_at > self.save_interval
  
  def saved(self):
    self.save_at = time.time()
  
  def should_back_up(self):
    return time.time() - self.backup_at > self.backup_interval
  
  def backed_up(self):
    t = time.time()
    self.backup_at = t
    self.save_at   = t
 
