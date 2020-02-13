import os

class BotTokenRetriever(object):
  def __init__(self):
    bot_token = None
    atropos_token_file = os.environ['ATROPOS_TOKEN_FILE']
    with open(atropos_token_file, 'r') as f:
      bot_token = f.read().strip()
    self.bot_token = bot_token

  def get_token(self):
    return self.bot_token

class BotIDRetriever(object):
  def __init__(self):
    bot_id = None
    atropos_id_file = os.environ['ATROPOS_ID_FILE']
    with open(atropos_id_file, 'r') as f:
      bot_id = f.read().strip()
    self.bot_id = bot_id
  
  def get_id(self):
    return self.bot_id


bot_token = BotTokenRetriever().get_token()
bot_id    = BotIDRetriever().get_token()

