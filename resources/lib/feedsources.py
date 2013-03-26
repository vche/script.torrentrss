# -*- coding: utf-8 -*-
import feeditem
import feedparser
import HTMLParser
import re
#from BeautifulSoup import BeautifulSoup

try:
  import xbmc
except ImportError:  
  import resources.lib.stubs.xbmc as xbmc

def log(txt):
  xbmc.log(msg = "[SCRIPT] 'torrentrss.feedsources': %s" % (txt, ), level=xbmc.LOGDEBUG)


class FeedSource:
  "Base class of article source"
  
  def __init__(self, srcurl="", desc=""):
    self.sourceUrl=srcurl
    self.description=desc
    self.articleList=[]
    
  
  def getUrl(self):
    "Get the url to use to get the latest articles"
    return self.sourceUrl

    
  def getDesc(self):
    "Get the url to use to get the latest articles"
    return self.description


  def getArticles(self):
    "Get the stored articles list as a FeedItem array"
    return self.articleList
  
  
  def fetchArticles(self):
    "Fetch the latest articles list as a FeedItem array"
    del self.articleList[:]
    feed = feedparser.parse(self.sourceUrl)
      
    # Convert feed article
    for item in feed.entries:
      # Verify required attributes exist
      if (hasattr(item, 'title_detail') and hasattr(item, 'published_parsed') and hasattr(item, 'link')):
        
        # Create a new feed item
        feedEntry = feeditem.FeedItem(item.title_detail.value, item.published_parsed, item.link)
        feedEntry.feed = self.description
        
        # Extract information from article body
        self.parseArticle(feedEntry, item)
        
        # Only add the torrent links
        if (hasattr(item, 'links')):
          for extlink in item.links:
            if ('type' in extlink):
              if (extlink.type == u'application/x-bittorrent'): feedEntry.links["torrent"] = extlink

        # Append it to the list
        self.articleList.append(feedEntry)
    return self.articleList


  def parseArticle(self, feeditem, article):
    "Extract information from article and update feeditem"
    # Base class, don't know the content just pass it over
    feeditem.summary= article.summary_detail.value


  def extractProperty(self, reg, content):
    "Search given regular expression in content and returns first result or None"
    searchResults = reg.findall(content)
    #TODO: replace b .match to stop at first ?
    if (searchResults) and (len(searchResults)>0) and (searchResults[0] != None): 
      #TODO: remove this tweak: Replace known escape char that cause error
      result = searchResults[0].replace(u'\xd7', 'x')
      return result
    else: return None


  def extractProperties(self, reg, delim, content):
    "Search given regular expression in content and returns first result or None"
    properties = {}
    #TODO: remove this tweak: Replace known escape char that cause error
    content = content.replace(u'\xd7', 'x')
    searchResults = reg.findall(content)
    #log(content)
    if (searchResults):
      for result in searchResults:
        label,value = result.split(delim)
        properties[label.strip()] = value.strip()
    return properties


  def __str__(self):
    return self.descrption + ' (' + self.sourceUrl + ')'


class FeedSourceYifi(FeedSource):
  "Specialized class to process Yifi torrent rss feed"

  def __init__(self, desc=""):
    FeedSource.__init__(self, "http://yify-torrents.com/rss", desc)

    # Precompute regular expressions for info extraction    
    self.thumbUrlReg = re.compile('<img alt=["].*["] src=["](.*)["] [style].*>', re.IGNORECASE)
    self.propertiesReg = re.compile('\s{4,}(.*)<br', re.IGNORECASE)
    self.descReg = re.compile('<p>(.*)</p>', re.IGNORECASE)


  def parseArticle(self, feeditem, article):
    html = HTMLParser.HTMLParser()
    feeditem.releaseName.append(article.title_detail.value)
    feeditem.summary=html.unescape(self.extractProperty(self.descReg, article.summary_detail.value))
    feeditem.thumbUrl=self.extractProperty(self.thumbUrlReg, article.summary_detail.value)
    feeditem.properties = self.extractProperties(self.propertiesReg, ':', article.summary_detail.value)
    
    
class FeedSourceRlsLogMovies(FeedSource):
  "Specialized class to process RlsLog.net movies torrent rss feed"

  def __init__(self, desc=""):
    FeedSource.__init__(self, "http://www.rlslog.net/category/movies/feed/", desc)

    # Precompute regular expressions for info extraction    
    self.thumbUrlReg = re.compile('<p><img.*src=["](.*?)"', re.IGNORECASE)
    self.commentReg = re.compile('<p><img.*/>(.*)</p>', re.IGNORECASE)
    self.descReg = re.compile('<strong>Plot[:]*[\s]*</strong>(.*?)</p>', re.IGNORECASE|re.DOTALL)
    self.infosectionReg = re.compile('<strong>Plot:[\s]*</strong>.*?</p>(.*)Links[:]*', re.IGNORECASE|re.DOTALL)
    self.descReg2 = re.compile('<strong>Description:[\s]*</strong>(.*)</p>', re.IGNORECASE|re.DOTALL)
    self.infosectionReg2 = re.compile('<strong>Description:[\s]*</strong>.*?</p>(.*)Links[:]*', re.IGNORECASE|re.DOTALL)
    self.propertiesReg = re.compile('<strong>(.*?)<br />', re.IGNORECASE)
    self.linksReg = re.compile('<a href=["](.*?)["]>', re.IGNORECASE)
    self.linksdescReg = re.compile('<a.*?>(.*?)</a>')


  def parseArticle(self, feeditem, article):
    html = HTMLParser.HTMLParser()
    #log(article.content[0].value)
    
    # Extract thumb url and comment and set default release name
    feeditem.thumbUrl=self.extractProperty(self.thumbUrlReg, article.content[0].value)
    feeditem.releaseName.append(article.title_detail.value)
    
    # Extract summary from plot tag or description if no plot tag
    feeditem.summary=self.extractProperty(self.commentReg, article.content[0].value)
    if (feeditem.summary != None): html.unescape(feeditem.summary).replace(u'\xd7', 'x')
    temp=self.extractProperty(self.descReg, article.content[0].value)
    if (temp == None): 
      temp=self.extractProperty(self.descReg2, article.content[0].value)
      temp2=self.extractProperty(self.infosectionReg2, article.content[0].value);
    else: temp2=self.extractProperty(self.infosectionReg, article.content[0].value);
    
    # Convert summary and concatenate to comment
    if (temp != None): 
      feeditem.summary += "\n\n" + html.unescape(temp).replace(u'\xd7', 'x')
      #log(feeditem.summary.encode('ascii','ignore'))
    
    # If additional info are found
    if (temp2 != None):
      feeditem.properties = self.extractProperties(self.propertiesReg, '</strong>', html.unescape(temp2))
      if "Release Name" in feeditem.properties: feeditem.releaseName[0] = feeditem.properties["Release Name"]
      
    # Get the links
    links = self.linksReg.findall(article.content[0].value)
    linkdescs = self.linksdescReg.findall(article.content[0].value)
    for urls, desc in zip(links,linkdescs):
      desc = desc.strip().lower()
      if desc == "imdb": feeditem.links['imdb'] = urls
      elif desc == "trailer": feeditem.links['trailer'] = urls      
    #TODO: for rlslog, also scan rls name from tag update


class FeedSourceRlsLogShows(FeedSource):
  "Specialized class to process RlsLog.net tv shows torrent rss feed"

  def __init__(self, desc=""):
    FeedSource.__init__(self, "http://www.rlslog.net/category/tv-shows/feed/", desc)

    # Precompute regular expressions for info extraction    
    self.thumbUrlReg = re.compile('<p><img.*src=["](.*?)"', re.IGNORECASE)
    self.commentReg = re.compile('<p>.*?<a.*?</a>.*?<p>(.*?)</p>', re.IGNORECASE|re.DOTALL)
    
    self.infosectionReg = re.compile('<img.*?</p>(.*)', re.IGNORECASE|re.DOTALL)
    self.infoitemReg = re.compile('<p.*?>(.*?)</p>', re.IGNORECASE|re.DOTALL)
    self.infolabel = re.compile('<strong>(.*?)</strong>')
    self.linkreg = re.compile('<a href=["](.*?)["]>(.*?)</a>', re.IGNORECASE|re.DOTALL)


  def parseArticle(self, feeditem, article):
    html = HTMLParser.HTMLParser()
    #log(article.content[0].value)
    
    # Extract thumb url and comment and set default release name
    feeditem.thumbUrl=self.extractProperty(self.thumbUrlReg, article.content[0].value)
    feeditem.releaseName.append(article.title_detail.value)
    
    # Extract summary description
    feeditem.summary=self.extractProperty(self.commentReg, article.content[0].value)
    if (feeditem.summary != None): html.unescape(feeditem.summary).replace(u'\xd7', 'x')

    info = self.infosectionReg.findall(article.content[0].value)
    if (len(info) > 0):
      infoitemlist = self.infoitemReg.findall(info[0])
      foundlinks = False
      for  infoitem in infoitemlist:
        if foundlinks == False:
          if 'Links' in infoitem:
            linklist = self.linkreg.findall(infoitem)
            for (link, linkdesc) in linklist: feeditem.links[linkdesc] = link
            foundlinks = True
          else:
            feeditem.summary += '\n' + html.unescape(infoitem).replace(u'\xd7', 'x')
        else:
          labels = self.infolabel.findall(infoitem)
          if (labels) and (len(labels)>0):
            feeditem.releaseName.append(html.unescape(labels[0]))

