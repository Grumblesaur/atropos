import enum
import re
import os

class LookupType(enum.Enum):
  EMPTY = -1
  PATH = 0
  LIST_OF_ARGUMENTS = 1

class HelpText(object):
  def __init__(self, help_path='helpfiles/'):
    self.help_path   = help_path
    self.help_topics, self.help_options = self._build_help_table()
    
  def _build_help_table(self):
    table = { }
    options = { }
    for help_file_path in os.listdir(self.help_path):
      if help_file_path.endswith('.md'):
        key = help_file_path.split(os.sep)[-1].replace('.md', '')
        table[key] = help_file_path
        table[key] = os.path.join(self.help_path, help_file_path)
      else:
        option_key = help_file_path.split(os.sep)[-1]
        options[option_key] = { }
        directories = os.listdir(os.path.join(self.help_path, option_key))
        for option_file_path in directories:
          key = option_file_path.split(os.sep)[-1].replace('.md', '')
          location = os.path.join(self.help_path, option_key, option_file_path)
          options[option_key][key] = location
    return table, options

  def _topic_initial_substring(self, keyword):
    pattern = re.compile(keyword)
    matches = [ ]
    for topic in self.help_topics:
      if pattern.match(topic):
        matches.append((topic, ''))
    return matches
  
  def _option_in_some_topic(self, keyword):
    out = None
    for topic in self.help_options:
      if keyword in self.help_options[topic]:
        out = self.help_options[topic][keyword]
        break
    return out
  
  def _option_initial_substring(self, keyword):
    pattern = re.compile(keyword)
    matches = []
    for topic in self.help_options:
      for option in self.help_options[topic]:
        if pattern.match(option):
          matches.append((topic, option))
    return matches
  
  def _option_initial_substring_for_topic(self, keyword, topic):
    pattern = re.compile(keyword)
    matches = [ ]
    for opt in self.help_options[topic]:
      if pattern.match(opt):
        matches.append((topic, opt))
    return matches
  
  def _unary_lookup(self, topic):
    '''Try the keyword as a general topic,
      or else try the keyword as an initial substring of a general topic,
      or else try the keyword as a(n initial substring of a) subtopic,
      or else show the list of topics.'''
    # If none of the other cases pan out, this is the default value.
    out = (LookupType.EMPTY, ())
    try:
      out = (LookupType.PATH, self.help_topics[topic])
    except KeyError:
      possible_topics = self._topic_initial_substring(topic)
      if len(possible_topics) > 1:
        out = (LookupType.LIST_OF_ARGUMENTS, possible_topics)
      elif len(possible_topics) == 1:
        out = (LookupType.PATH, self.help_topics[possible_topics[0]])
      else:
        possible_reverse_lookup_path = self._option_in_some_topic(topic)
        if possible_reverse_lookup_path:
          out = (LookupType.PATH, possible_reverse_lookup_path)
        else:
          possible_topic_option_pairs = self._option_initial_substring(topic)
          if len(possible_topic_option_pairs) > 1:
            out = (LookupType.LIST_OF_ARGUMENTS, possible_topic_option_pairs)
          elif len(possible_topic_option_pairs) == 1:
            p = possible_topic_option_pairs.pop()
            out = (LookupType.PATH, self.help_options[p[0]][p[1]])
    return out
      
  
  def _binary_lookup(self, topic, option):
    tpattern = re.compile(topic)
    opattern = re.compile(option)
    out = (LookupType.EMPTY, ())
    if topic in self.help_options and option in self.help_options[topic]:
      out = (LookupType.PATH, self.help_options[topic][option])
    elif topic in self.help_options and option not in self.help_options[topic]:
      out = (
        LookupType.LIST_OF_ARGUMENTS,
        self._option_initial_substring_for_topic(option, topic)
      )
    else:
      topic_matches  = self._topic_initial_substring(topic)
      option_matches = [ ]
      for tm in topic_matches:
        option_matches.extend(
          self._option_initial_substring_for_topic(option, tm[0])
        )
      argument_tuples = [ ]
      for t in topic_matches:
        for o in option_matches:
          argument_tuples.append((t[0], o[1]))
      if len(argument_tuples) > 1:
        out = (LookupType.LIST_OF_ARGUMENTS, argument_tuples)
      elif len(argument_tuples) == 1:
        t = argument_tuples.pop()
        out = (LookupType.PATH, self.help_options[t[0]][t[1]])
    return out
      
  
  def lookup(self, keyword, option=None):
    keyword = keyword.lower()
    option  = option.lower()  if option is not None else None
    if option is None:
      lookup_result = self._unary_lookup(keyword)
    else:
      lookup_result = self._binary_lookup(keyword, option)
    
    out = ''
    if lookup_result[0] == LookupType.PATH:
      with open(lookup_result[1], 'r') as f:
        out = f.read()
    elif lookup_result[0] == LookupType.LIST_OF_ARGUMENTS:
      rows_of_args = '\n'.join(['  %s %s' % t for t in lookup_result[1]])
      out =  'Your search yielded ambiguous results. Try the `+help` command '
      out += f'with any of the following arguments:\n```{rows_of_args}```'
    else:
      with open(self.help_topics['topics']) as f:
        standard = f.read()
      out = 'Your search did not yield any results. Try the `+help` command '
      out += f'with one of the standard topics:\n```{standard}```'
    return out
  
