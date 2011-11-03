#!/usr/bin/python26
import logging
import os,sys
import glob
from optparse import OptionParser
import traceback,inspect

LOG = logging.getLogger("JmapAnalyzer")
logging.basicConfig(level=logging.DEBUG)
JMAP_FILE_PATTERN = 'jmap*out'
STRICTLY_INCREASING = False

class JmapEntry:
  def __init__(self, class_name, size , instances):
    self.cname = class_name
    self.value = EntryValue(long(size), long(instances))

  def __str__(self):
    return " JmapEntry [name:%s, bytes:%d, instances:%d] " % (self.cname, self.value.size, self.value.instances)

class EntryValue:
  def __init__(self, size, instances):
    self.size = size
    self.instances = instances

  def __str__(self):
    return "Value [bytes:%d, instances:%d]" % (self.size, self.instances)

class JmapOutFile:
  def __init__(self, file_name):
    self.entry_map = self.__load_jmap_out(file_name)

  def __load_jmap_out(self, fname):
    jmap_file = open(fname, "r")
    jmap_lines = jmap_file.readlines()[3:-1] # first three lines are useless
    entry_map = {}
    for line in jmap_lines:
      entry = self.parse_jmap_line(line)
      entry_map[entry.cname] = entry.value
    return entry_map
    
  def parse_jmap_line(self, jmap_line):
    jmap_line = jmap_line.strip()
    members = jmap_line.split()[1:] # ignore the first member, the serial number
    return JmapEntry(members[2], members[1], members[0])
 
class JmapAnalyzer:
  def __init__(self, directory):
    self.timesorted_jmapfile_map_list = self.__load_all_files(directory)
    self.unique_classnames = self.__get_unique_classnames(self.timesorted_jmapfile_map_list)

  def __load_all_files(self, dir):
    map_list = []
    files = glob.glob( os.path.join(dir, JMAP_FILE_PATTERN) )
    if (len(files) == 0):
      LOG.warn("No files found")
    files.sort(key=lambda x: os.path.basename(x))
    for file in files:
      outfile = JmapOutFile(file)
      map_list.append(outfile.entry_map)
    return map_list

  def __get_unique_classnames(self, map_list):
    #a generator that will convert the list of dicts into an iterable sequence of sets of keys. 
    sets = (set(x.keys()) for x in map_list)
    find_common = lambda a,b: a.intersection(b)
    return list(reduce(find_common, sets))

  def analyze(self):
    result = []
    for name in self.unique_classnames:
      ordered_class_instances = []
      for map_list in self.timesorted_jmapfile_map_list:
        if map_list.has_key(name):
          ordered_class_instances.append(map_list[name].instances)
        else:
          break
      min_len = 2 #assuming there are atleast two entries for each class name
      if STRICTLY_INCREASING:
        min_len = len(ordered_class_instances)
      if len(ordered_class_instances) == len(self.timesorted_jmapfile_map_list) \
            and not len(set(ordered_class_instances)) < min_len \
            and is_sorted(ordered_class_instances):
        result_entry = (name, (ordered_class_instances, sum(ordered_class_instances)))
        result.append(result_entry)
    return sorted(result, key=lambda entry:entry[1][1], reverse=True)

def is_sorted(x, key = lambda x: x): 
  return all([key(x[i]) <= key(x[i + 1]) for i in xrange(len(x) - 1)]) 

if __name__ == '__main__':
  usage = "usage: %prog [options]. -h prints help."
  parser = OptionParser(usage)
  parser.add_option("-d", "--directory", dest="dir",
                            help="(mandatory) full absolute directory path.")
  parser.add_option("-s", "--strictly_increasing", 
                            help="specify this if you want to o/p only classes whose instances are increasing strictly", 
                            action="store_true", dest="strictlyIncreasing")
  (options, args) = parser.parse_args()
  mandatories = ['dir']
  for m in mandatories:
    if not options.__dict__[m]:
      print "mandatory option is missing\n"
      parser.print_help()
      sys.exit(-1)
  if(options.strictlyIncreasing):
    STRICTLY_INCREASING=True
  analyzer = JmapAnalyzer(options.dir)
  for i in analyzer.analyze():
    print("%s, list: %s, total: %s" % (i[0], i[1][0], i[1][1]))
