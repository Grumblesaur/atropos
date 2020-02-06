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

bot_token = BotTokenRetreiver().get_token()

