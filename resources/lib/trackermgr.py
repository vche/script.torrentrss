import os, sys, unicodedata, pickle, traceback, time
#TODO: Update feed manager
# feedItem: +object_sum_parsed summary_parsed()
#              |--> pic, rls links, desc,...
# urllist[] => sourcefeed[] url = sourcefeed.url
#
# - obj sourcefeed()
#    -getUrl()
#    -getArticles() --> call feedparser, to call insteaf of feedparser directly in fetch()
#    -parseArticle(feeditem,htmlcontent) --> to add when creating new feeditem, internaly by getArticles, 
#                                            return a feeditem based on a feed entry
#    objsourcefedRlslog()
#    objsourcefedRlslog()
#
# - remove add urls
#
##########################################
# If xbmc libs can't be loaded import stubs for local testing
try:
  import xbmc
except ImportError:  
  import resources.lib.stubs.xbmc as xbmc

TRACKER_MAX_ITEMS=200

def log(txt):
  xbmc.log(msg = "[SCRIPT] 'torrentrss.trackermgr': %s" % (txt, ), level=xbmc.LOGDEBUG)
##########################################


##########################################
class TrackerMgr:
  "Manage a collection of feeds"

  def __init__(self, trackerlist):
    "Class constructor"
    self.__trackerList=trackerlist
    self.__resultList = []
    self.__searchKeywords = ""

 
  def __del__(self):
    "Destructor"
    # Resize the list if too big and save it
    pass

 
  def search(self, keywords):
    self.__searchKeywords = keywords
    self.reset()
    for tracker in self.__trackerList:
      self.__resultList += tracker.Search(keywords)
    sorted(self.__resultList, key=lambda entry: entry.seeds)
    return self.__resultList


  def getTrackerList(self):
    "Access the list of feeds"
    return self.__trackerList


  def getLastResults(self):
    "Access the list of feeds"
    return self.__resultList

  
  def getLastKeywords(self):
    "Access the list of feeds"
    return self.__searchKeywords

  
  def getTrackerNames(self):
    namelist=[]
    for entry in self.__trackerList: namelist.append(entry.description);
    return namelist

  
  def dumpTrackers(self):
    "Dump the list of trackers"
    log("-------------------")
    for entry in self.__trackerList: log("  Desc: %s\n   URL:  %s\n", entry.getDesc, entry.getUrl);
    log("--------%s-----------" % (len(self.__trackerList)))


  def dumpResults(self):
    "Dump the last results"
    log("-------------------")
    for entry in self.__resultList: log("-----\n%s-----\n" % entry.dump());
    log("--------%s-----------" % (len(self.__resultList)))


  def reset(self):
    "Cleqrs feed item list"
    del self.__resultList[:]
