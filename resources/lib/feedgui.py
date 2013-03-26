import sys
import xbmc, xbmcgui
import feeditem, trackergui, torrentclient

#enable localization
getLS   = sys.modules[ "__main__" ].__language__
__cwd__ = sys.modules[ "__main__" ].__cwd__

# Actions ids
ACTION_PARENT_DIR = 9
ACTION_PREVIOUS_MENU = 10
ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_UP = 3
ACTION_MOVE_DOWN = 4
ACTION_NAV_BACK = 92

SORT_BY_DATE = 0
SORT_BY_TITLE= 1
SORT_BY_FEED = 2
SORT_BY_COUNT= 3


def log(txt):
  xbmc.log(msg = "[SCRIPT] 'torrentrss.feedgui': %s" % (txt, ), level=xbmc.LOGDEBUG)


##########################################
class FeedGUI(xbmcgui.WindowXML):
  "GUI for feed articles listing"  
  
  # Declare this to handle events before control init
  control_list_id=-1
  
  def __init__(self, *args, **kwargs):
    # Init window
    xbmcgui.WindowXML.__init__(self, *args, **kwargs)
    
    #Init data
    self.feedMgr = kwargs['feedMgr']
    self.torrentClient = kwargs['torrentClient']
    #self.feedMgr.dumpFeed()
    self.orderby=SORT_BY_DATE
    self.filterlist = []
    self.loaded = 0
    self.selecteditem = 0
    
    # Create aux dialogs and windows
    self.busyWindow = xbmcgui.WindowXMLDialog("DialogBusy.xml", __cwd__, "default")
    self.selectWindow = FeedGUISelect("script-torrentrss-select.xml", __cwd__, "default", itemlist=())
    self.trackerui = trackergui.TrackerGUI("script-torrentrss-trackergui.xml", __cwd__, "default", trackerMgr=kwargs['trackerMgr'])
    #self.trackerui = xbmcgui.WindowXML("script-torrentrss-trackergui.xml", __cwd__, "default")


  def __del__(self):
    "Destructor"
    del self.selectWindow
    del self.trackerui


  def onInit(self):
    "Secondary constructor called each time after window xml is loaded"
    # Show busy dialog
    self.showBusyWindow()
            
    # Init gui
    self.defineControls()
    
    # Only refresh feeds and init selection at first load, when the window is reopen don't do it
    if (self.loaded == 0):
      # Fetch feed update
      self.feedMgr.update()
      #self.feedMgr.dumpFeed()
      
      # Feed name/id link list
      self.feedmap = {}
      self.feedmap['31010'] = getLS(50102)
      self.feedmap['31011'] = getLS(55001)
      self.feedmap['31012'] = getLS(55002)
      self.feedmap['31013'] = getLS(55003)
      self.feedmap['31014'] = getLS(55004)
      self.feedmap['31015'] = getLS(55005)
      self.feedmap['31016'] = getLS(55006)
      self.getControl(self.control_leftFrame_liststart_id).setSelected(True)
      self.filterlist.append(self.feedmap['31010'])
    
    # Refresh gui list
    self.refreshListItem(self.filterlist)
    self.list.selectItem(self.selecteditem)

    # Close busy dialog
    self.closeBusyWindow()
    self.loaded = 1


  def defineControls(self):
    "Initialize controls and link to gui widgets"
    # actions
    self.action_cancel_dialog = (ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_NAV_BACK)
    self.action_up_down = (ACTION_MOVE_UP, ACTION_MOVE_DOWN)
    
    # Control ids
    self.control_list_id =              504
    self.control_rightFrame_title_id =  30001
    self.control_rightFrame_info_id =   30002
    self.control_rightFrame_txtbox_id = 30004
    self.control_rightFrame_list_id =   30010
    self.control_rightFrame_imgbox_id = 30005
    self.control_rightFrame_trailer_id =30006
    self.control_rightFrame_samples_id =30007
    self.control_leftFrame_sortorder_id = 4
    self.control_leftFrame_filter_id =  19
    self.control_leftFrame_clear_id =   31001
    self.control_leftFrame_refresh_id = 31004
    self.control_leftFrame_sortby_id = 31005
    self.control_leftFrame_liststart_id = 31010
    self.control_leftFrame_listend_id = 31016
    
    # Controls
    self.list = self.getControl(self.control_list_id)
    self.rightFrame_title = self.getControl(self.control_rightFrame_title_id)
    self.rightFrame_info = self.getControl(self.control_rightFrame_info_id)
    self.rightFrame_txtbox = self.getControl(self.control_rightFrame_txtbox_id)
    self.rightFrame_list = self.getControl(self.control_rightFrame_list_id)
    self.rightFrame_imgbox = self.getControl(self.control_rightFrame_imgbox_id)
    self.rightFrame_trailer = self.getControl(self.control_rightFrame_trailer_id)
    self.rightFrame_samples = self.getControl(self.control_rightFrame_samples_id)
    self.leftFrame_clear = self.getControl(self.control_leftFrame_clear_id)
    self.leftFrame_refresh = self.getControl(self.control_leftFrame_refresh_id)
    self.leftFrame_sortby = self.getControl(self.control_leftFrame_sortby_id)
    #self.leftFrame_sortorder = self.getControl(self.control_leftFrame_sortorder_id)
    #self.leftFrame_filter = self.getControl(self.control_leftFrame_filter_id)    


  def showBusyWindow(self):
    " Display a 'working' window"
    self.busyWindow.show()

  def closeBusyWindow(self):
    " Close the 'working' window"
    self.busyWindow.close()

  def refreshListItem(self, filterfeed=None):
    "Refresh GUI content"
    # Update feed list
    self.list.reset()
    log("PIPO: list reset")
    i=0
    alltxt=getLS(50102)
    for entry in self.feedMgr.getFeedList():
      #log(entry)
      if (filterfeed == None) or (alltxt in filterfeed) or (entry.feed in filterfeed):
        item = xbmcgui.ListItem(entry.title, entry.datestr)
        item.setProperty('feed', entry.feed)
        item.setProperty('status', str(entry.statusflag))
        item.setProperty('pos', str(i))
        self.list.addItem(item)
      i=i+1
      
    # Update flags and right frame with default selected item
    self.onSelected(self.list.getSelectedItem())


  def clear(self):
    "Clear the all feed items after user confirmation"
    if (xbmcgui.Dialog().yesno(" Delete all articles", " Are you sure ?", "All stored articles will be deleted")):
      log("PIPO: list reset 2")
      self.list.reset()
      self.feedMgr.reset()


  def onClick(self, controlId):
    "React on mouse clicks/select key"
    if controlId == self.control_list_id:
      item = self.list.getSelectedItem()
      srcfeed = self.feedMgr.getFeedList()[int(item.getProperty('pos'))]
      if (len(srcfeed.releaseName) > 0):
        if (len(srcfeed.releaseName) == 1): rlsname = srcfeed.releaseName[0]
        else: rlsname = self.selectWindow.SelectItem(srcfeed.releaseName)
      if (rlsname != None):
        log("selected: " + rlsname)
        # Save selected item pos since the gui is gonna be freed and reinit after tracker gui is closed
        self.selecteditem = self.list.getSelectedPosition()
        if (self.torrentClient == None):
          xbmcgui.Dialog().ok(getLS(50003), getLS(50004), getLS(50005))
        else:
          dllink = self.trackerui.doModalSearch(rlsname)
          log("to download: %s" % dllink)
          if (dllink != None): 
            try:
              self.showBusyWindow()
              self.torrentClient.addLink(dllink)
              self.closeBusyWindow()
              xbmcgui.Dialog().ok(getLS(50205), getLS(50206), " ",  " -->    "+rlsname+"    <--")
              self.updateItemFlag(self.list.getSelectedItem(), feeditem.FeedItem.STATUS_DOWNLOADED)
            except torrentclient.TorrentClientError:
              log("Client error: (%s = %s)" % (sys.exc_info()[0], sys.exc_info()[1]))
              self.closeBusyWindow()
              xbmcgui.Dialog().ok(getLS(50207), getLS(50208), getLS(50209),  " -->    "+rlsname+"    <--")
            except torrentclient.TorrentConnectionError as ex2:
              log("Connection error: %s (%s = %s)" % (ex2.__str__(), sys.exc_info()[0], sys.exc_info()[1]))
              self.closeBusyWindow()
              xbmcgui.Dialog().ok(getLS(50207), getLS(50210), ex2.__str__(), getLS(50211))
    elif controlId == self.control_leftFrame_clear_id:
      self.clear()
      self.clearRightFrame()
    elif controlId == self.control_leftFrame_refresh_id:
      self.showBusyWindow()
      self.feedMgr.update()
      self.refreshListItem(self.filterlist)
      self.closeBusyWindow()
    elif controlId == self.control_leftFrame_sortby_id:
      self.orderby = (self.orderby+1)%SORT_BY_COUNT
      self.leftFrame_sortby.setLabel(getLS(50150) + getLS(50150+self.orderby+1))
      if (self.orderby == SORT_BY_DATE): sorted(self.feedMgr.getFeedList(), key=lambda entry: entry.date)
      elif (self.orderby == SORT_BY_TITLE): sorted(self.feedMgr.getFeedList(), key=lambda entry: entry.title)
      elif (self.orderby == SORT_BY_FEED): sorted(self.feedMgr.getFeedList(), key=lambda entry: entry.feed)
      self.refreshListItem(self.filterlist)
    elif controlId == self.control_rightFrame_trailer_id:
      item = self.list.getSelectedItem()
      srcfeed = self.feedMgr.getFeedList()[int(item.getProperty('pos'))]
      if ("trailer" in srcfeed.getLinkKeys()):
        #xbmc.Player().play(srcfeed.getLink("trailer"))
        log("play: " + srcfeed.getLink("trailer"))
        #TODO: extract video link from page
    elif controlId >= self.control_leftFrame_liststart_id and controlId <= self.control_leftFrame_listend_id:
      item = self.getControl(controlId)
      label = self.feedmap[str(controlId)]
      if item.isSelected(): self.filterlist.append(label)
      else: self.filterlist.remove(label)
      self.refreshListItem(self.filterlist)

  
  def onAction(self, action):
    "React on actions"
    if (action in self.action_cancel_dialog):
      self.close()
    elif (self.getFocusId() == self.control_list_id) and (action in self.action_up_down):
      item = self.list.getSelectedItem()
      self.onSelected(item)
    elif action.getButtonCode() == 0xf200:  # Key 'd' to display debug info
      log("------ DEBUG INFO ------")
      log("  ListItems: %d " % (self.list.size()))
      for index in range(self.list.size()): log("    %s " % (self.list.getListItem(index).getLabel()))
      self.list
      log("-- END OF DEBUG INFO ---")
    #else: log("action %s - %s" % (action.getId(), action.getButtonCode()))


  def onFocus(self, controlId):
    "React on focus"
    if controlId == self.control_list_id:
      item = self.list.getSelectedItem()
      self.onSelected(item)


  def onControl(self, controlId):
    "React on focus"
    if controlId == self.control_list_id:
      item = self.list.getSelectedItem()
      self.updateItemFlag(item, feeditem.FeedItem.STATUS_READ)


  def onSelected(self, item):
    "Action when a new list item is selected (custom)"
    if (item):
      self.updateRightFrame(item)
      self.updateItemFlag(item, feeditem.FeedItem.STATUS_READ)


  def updateItemFlag(self, item, status, force=False):
    "Update the status flag of an item in both internal list and gui"
    pos = int(item.getProperty('pos'))
    feedlist = self.feedMgr.getFeedList()
    if (force) or (feedlist[pos].statusflag < status):
      feedlist[pos].statusflag = status
      item.setProperty('status', str(feedlist[pos].statusflag))


  def updateRightFrame(self, item):
    "Update the right frame of the gui with given feed info"
    srcfeed = self.feedMgr.getFeedList()[int(item.getProperty('pos'))]
    self.rightFrame_title.setLabel(srcfeed.title)
    self.rightFrame_info.setLabel(getLS(50201) % (srcfeed.feed, srcfeed.datestr))
    if srcfeed.summary != None: self.rightFrame_txtbox.setText(srcfeed.summary)
    else: self.rightFrame_txtbox.setText(xbmc.getLocalizedString(416))
    if srcfeed.thumbUrl != None: self.rightFrame_imgbox.setImage(srcfeed.thumbUrl)
    else: self.rightFrame_imgbox.setImage("Fanart_Fallback_Small.jpg")

    # Display properties
    self.rightFrame_list.reset()
    keys = srcfeed.getPropertyKeys()
    for key in keys:
      self.rightFrame_list.addItem(xbmcgui.ListItem(key, srcfeed.getProperty(key)))
    if ("trailer" in srcfeed.getLinkKeys()):
      self.rightFrame_trailer.setVisible(True)
      self.rightFrame_samples.setVisible(True)
    #else: log(keys)


  def clearRightFrame(self):
    "Clear right frame with default values"
    self.rightFrame_title.setLabel(xbmc.getLocalizedString(416))
    self.rightFrame_info.setLabel(xbmc.getLocalizedString(416))
    self.rightFrame_txtbox.setText(xbmc.getLocalizedString(416))
    self.rightFrame_list.reset()
    self.rightFrame_imgbox.setImage("Fanart_Fallback_Small.jpg")
    self.rightFrame_trailer.setVisible(False)
    self.rightFrame_samples.setVisible(False)


class FeedGUISelect(xbmcgui.WindowXMLDialog):
  "GUI for selection dialog"
  
  list = None

  def __init__(self, *args, **kwargs):
    xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)
    self.itemlist = kwargs['itemlist']
    self.selection = ""

  def onInit(self):
    self.defineControls()
    self.updateList()


  def defineControls(self):
    #actions
    self.action_cancel_dialog = (9, 10)
    
    #control ids
    self.control_heading_label_id       = 2
    self.control_list_id                = 10
    self.control_cancel_button_id       = 19

    #controls
    self.list               = self.getControl(self.control_list_id)
    self.cancel_button      = self.getControl(self.control_cancel_button_id)


  def SelectItem(self, itemlist=()):
    self.itemlist = itemlist
    self.selection = None
    self.updateList()
    self.doModal()
    return self.selection


  def updateList(self):
    if (self.list):
      self.list.reset()
      for item in self.itemlist: self.list.addItem(item)
      self.list.selectItem(0)
      self.setFocusId(self.control_list_id)


  def onClick(self, controlId):
    #select an item
    if controlId == self.control_list_id:
      self.selection = self.list.getSelectedItem().getLabel()
      self.close()
    #cancel dialog
    elif controlId == self.control_cancel_button_id:
      self.close()


  def onAction(self, action):
    if action in self.action_cancel_dialog:
      self.close()

  
  def onFocus(self, controlId):
    pass
