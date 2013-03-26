import time

class FeedItem:
  "Represents a single feed item"
  STATUS_UNREAD = 0
  STATUS_READ = 1
  STATUS_DOWNLOADED = 2

  title = ""
  srcurl = ""
  date = []
  links = []
  feed = ""
  statusflag = STATUS_UNREAD
  dlflag = False
  datestr = ""
  
  summary = []
  releaseName = []
  thumbUrl = None
  thumbLocalPath = None
  properties = {}
  links = {}  #cqn contain imdb qnd trailer
  
  """
  links[] --> trailer, samples
  
  in __del__: if local thumb exist, delete it
  
  Links: nfo | imdb | trailer | torrent
  """

  def __init__(self, title="", date=time.localtime(), srcurl=""):
    self.title = title
    self.srcurl = srcurl
    self.date = date
    self.links = {}
    self.feed = ""
    self.statusflag = FeedItem.STATUS_UNREAD
    self.dlflag = False
    self.summary = []
    self.releaseName = []
    self.thumbUrl = None
    self.thumbLocalPath = None
    self.properties = {}
    self.links = {}  #cqn contain imdb qnd trailer
    
    curtime = time.localtime()
    if (curtime.tm_mday == date.tm_mday) and (curtime.tm_mon == date.tm_mon) and (curtime.tm_year == date.tm_year):
      self.datestr = "%02d:%02d:%02d  %02d/%02d/%02d" % (date.tm_hour, date.tm_min, date.tm_sec, date.tm_mday ,date.tm_mon, date.tm_year%100)
    else:
      self.datestr = "%02d/%02d/%02d  %02d:%02d:%02d" % (date.tm_mday ,date.tm_mon, date.tm_year%100, date.tm_hour, date.tm_min, date.tm_sec)

  def __repr__(self):
    return "%s(%r)" % (self.__class__, self.__dict__)

  def __str__(self):
    return "Title:%s\n\tDate:%s\n\tURL:%s\n\tFeed:%s\n\tLinks:%s\n\tSummary:%s" % (self.title, self.date, self.srcurl, self.feed, self.links, self.summary.value)

  def getOverview(self):
    pass
  
  def getDetails(self):
    pass

  def setProperties(self, props):
    self.properties.update(props)
  
  def  setProperty(self, key, value):
    self.properties[key] = value

  def  getProperty(self, key):
    return self.properties[key]

  def  getPropertyKeys(self):
    return self.properties.keys()
  
  def  getLink(self, key):
    return self.links[key]

  def  getLinkKeys(self):
    return self.links.keys()

  def dump(self):
    return "------\n"+ self.__str__()+'\n'
    #log(feeditem.releaseName)
    #log(feeditem.thumbUrl)
    #log(repr(feeditem.summary))
    #log(feeditem.properties)
    #log(feeditem.links);log("")

