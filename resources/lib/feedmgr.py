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

FEED_DB_FILE="/resources/data/feedDb.db"
FEED_MAX_ITEMS=200

def log(txt):
  xbmc.log(msg = "[SCRIPT] 'torrentrss.feedmgr': %s" % (txt, ), level=xbmc.LOGDEBUG)
##########################################


##########################################
class FeedMgr:
  "Manage a collection of feeds"

  def __init__(self, addonpath, sourcelist):
    "Class constructor"
    self.__feedSourceList=sourcelist
    self.__feedList = []
    self.__datapath  = addonpath + FEED_DB_FILE
        
    # Load and update previous list
    self.load()
    #self.dumpFeed()    

 
  def __del__(self):
    "Destructor"
    # Resize the list if too big and save it
    self.save()

 
  def load(self):
    "Load cached feed items list"
    log("Loading feeds items from " + self.__datapath)
    del self.__feedList[:]
    if os.path.exists(self.__datapath):
      try:
        outfile=open(self.__datapath, 'r')
        self.__feedList = pickle.load(outfile)
        outfile.close()
      except:
        log("Feed list loading failed: " +traceback.format_exc())     


  def save(self):
    "Cache feed items list"
    log("Saving feeds items to " + self.__datapath)
    try:
      self.__strip()
      outfile=open(self.__datapath, 'w')
      pickle.dump(self.__feedList, outfile)
      outfile.close()
    except:
      log("Feed list saving failed: " +traceback.format_exc())


  def getFeedList(self):
    "Access the list of feeds"
    return self.__feedList


  def getFeedNames(self):
    namelist=[]
    for entry in self.__feedSourceList: namelist.append(entry.description);
    return namelist

  
  def dumpFeed(self):
    "Dump the list of feeds"
    log("-------------------")
    for entry in self.__feedList:
      log(entry.title + '  [' + entry.feed + '] [' + entry.datestr + ' ]')
    log("--------%s-----------" % (len(self.__feedList)))


  def update(self):
    " Update the feed list with latest url feeds "
    
    # Append new article to the list    
    self.__fetch()
    # Remove duplicates
    self.__cleanup()


  def reset(self):
    "Cleqrs feed item list"
    del self.__feedList[:]


  def __strip(self):
    " Strip the feed list not to exceed the maximal items number"
    if (len(self.__feedList) > FEED_MAX_ITEMS):
      # sort by date
      self.__feedList = sorted(self.__feedList, key=lambda entry: entry.date)
    
      # remove first (len - max_items items) to resize the list
      self.__feedList = self.__feedList[len(self.__feedList) - FEED_MAX_ITEMS:]


  def __fetch(self):
    "Fetch new articles from feeds and append them to the list"
    #For each feed get articles
    for feedsource in self.__feedSourceList:
      log("Fetching feed %s" % feedsource.getUrl())
      sys.stdout.flush()
      self.__feedList.extend(feedsource.fetchArticles())
    #self.dumpFeed()
      
    
  def __cleanup(self): 
    "Sort list and remove duplicates"
    # sort by title
    self.__feedList = sorted(self.__feedList, key=lambda entry: entry.title)
    
    # remove item when the same than the previous
    item = None
    i=len(self.__feedList)-1
    while (i>=0):
      entry = self.__feedList[i]
      if (item != None):
        if item.title == entry.title and item.srcurl == entry.srcurl and item.date == entry.date:
          self.__feedList.remove(item)
      item = entry
      i=i-1
