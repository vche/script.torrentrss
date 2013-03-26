import sys
import xbmc, xbmcgui
import torrentitem

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


def log(txt):
  xbmc.log(msg = "[SCRIPT] 'torrentrss.trackergui': %s" % (txt, ), level=xbmc.LOGDEBUG)


##########################################
class TrackerGUI(xbmcgui.WindowXML):
  "GUI for tracker search results listing"
  
  # Declare this to handle events before control init
  control_list_id=-1
  
  def __init__(self, *args, **kwargs):
    # Init window
    xbmcgui.WindowXML.__init__(self, *args, **kwargs)
    self.trackerMgr = kwargs['trackerMgr']
    self.filterlist = []
    self.loaded = 0
    self.results = []
    self.busyWindow = xbmcgui.WindowXMLDialog("DialogBusy.xml", __cwd__, "default")

  def __del__(self):
    "Destructor"
    pass

  def onInit(self):
    "Secondary constructor called after window xml is loaded"
            
    # Init gui
    self.defineControls()

    if (self.loaded == 0):
      # Feed name/id link list
      self.feedmap = {}
      self.feedmap['41010'] = getLS(50102)
      self.feedmap['41011'] = getLS(55101)
      self.feedmap['41012'] = getLS(55102)
      self.getControl(self.control_leftFrame_liststart_id).setSelected(True)
      self.filterlist.append(self.feedmap['41010'])
    
    # Clear gui list
    self.refreshListItem(self.filterlist)
    self.loaded = 1


  def defineControls(self):
    "Initialize controls and link to gui widgets"
    # actions
    self.action_cancel_dialog = (ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_NAV_BACK)
    self.action_up_down = (ACTION_MOVE_UP, ACTION_MOVE_DOWN)
    
    # Control ids
    self.control_list_id =              504
    self.control_rightFrame_title_id =  40001
    self.control_rightFrame_info_id =   40002
    self.control_rightFrame_list_id =   40010
    self.control_rightFrame_imgbox_id = 40005
    self.control_leftFrame_sortorder_id = 4
    self.control_leftFrame_filter_id =  19
    self.control_leftFrame_refresh_id = 41004
    self.control_leftFrame_sortby_id = 41005
    self.control_leftFrame_liststart_id = 41010
    self.control_leftFrame_listend_id = 41012
    
    # Controls
    self.list = self.getControl(self.control_list_id)
    self.rightFrame_title = self.getControl(self.control_rightFrame_title_id)
    self.rightFrame_info = self.getControl(self.control_rightFrame_info_id)
    self.rightFrame_list = self.getControl(self.control_rightFrame_list_id)
    self.rightFrame_imgbox = self.getControl(self.control_rightFrame_imgbox_id)
    self.leftFrame_refresh = self.getControl(self.control_leftFrame_refresh_id)
    self.leftFrame_sortby = self.getControl(self.control_leftFrame_sortby_id)
    #self.leftFrame_sortorder = self.getControl(self.control_leftFrame_sortorder_id)
    #self.leftFrame_filter = self.getControl(self.control_leftFrame_filter_id)    


  def showBusyWindow(self):
    " Display a 'working' window"
    self.busyWindow = xbmcgui.WindowXMLDialog("DialogBusy.xml", __cwd__, "default")
    self.busyWindow.show()


  def closeBusyWindow(self):
    " Close the 'working' window"
    self.busyWindow.close()


  def doModalSearch(self, keywords):
    
    # Show busy dialog
    self.showBusyWindow()
    
    # Run a sequential search on all trackers
    self.results = self.trackerMgr.search(keywords)
    
    # Close busy dialog
    self.closeBusyWindow()

    # Display results or error    
    self.selectedlink = None
    if (len(self.results) > 0): self.doModal()
    else: xbmcgui.Dialog().ok(getLS(56001), getLS(56002), getLS(56003))
    return self.selectedlink
    
    
  def refreshListItem(self, filterfeed=None):
    "Refresh GUI content"
    # Update feed list
    self.list.reset()
    i=0
    alltxt=getLS(50102)
    for entry in self.results:
      #log(entry)
      if (filterfeed == None) or (alltxt in filterfeed) or (entry.tracker in filterfeed):
        item = xbmcgui.ListItem(entry.seeds, entry.title)
        item.setProperty('size', entry.size)
        item.setProperty('peers', entry.peers)
        item.setProperty('vip', 'p'+entry.vip)
        item.setProperty('pos', str(i))
        self.list.addItem(item)
      i=i+1
    self.list.selectItem(0)
    self.onSelected(self.list.getSelectedItem())


  def clear(self):
    "Clear the all feed items after user confirmation"
    self.list.reset()
    self.trackerMgr.reset()


  def onClick(self, controlId):
    "React on mouse clicks/select key"
    if controlId == self.control_list_id:
      item = self.list.getSelectedItem()
      torrent = self.results[int(item.getProperty('pos'))]
      self.selectedlink = None
      if (xbmcgui.Dialog().yesno(torrent.title, getLS(56011))):
        if (len(torrent.magnet) > 0): self.selectedlink = torrent.magnet
        elif (len(torrent.torrent) > 0): self.selectedlink = torrent.torrent
        self.close()
    elif controlId == self.control_leftFrame_refresh_id:
      self.showBusyWindow()
      self.list.reset()
      self.clearRightFrame()
      self.results = self.trackerMgr.search(self.trackerMgr.getLastKeywords())
      self.refreshListItem(self.filterlist)
      self.closeBusyWindow()
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


  def onFocus(self, controlId):
    "React on focus"
    if controlId == self.control_list_id:
      item = self.list.getSelectedItem()
      self.onSelected(item)


  def onSelected(self, item):
    "Action when a new list item is selected (custom)"
    if (item):
      self.updateRightFrame(item)


  def updateRightFrame(self, item):
    "Update the right frame of the gui with given feed info"
    self.rightFrame_list.reset()
    srcfeed = self.results[int(item.getProperty('pos'))]
    self.rightFrame_info.setLabel(srcfeed.title)
    if srcfeed.trackerlogo != None: self.rightFrame_imgbox.setImage(srcfeed.trackerlogo)
    else: self.rightFrame_imgbox.setImage("Fanart_Fallback_Small.jpg")

    self.rightFrame_list.addItem(xbmcgui.ListItem(getLS(56202), srcfeed.seeds))
    self.rightFrame_list.addItem(xbmcgui.ListItem(getLS(56203), srcfeed.peers))
    self.rightFrame_list.addItem(xbmcgui.ListItem(getLS(56204), srcfeed.size))
    self.rightFrame_list.addItem(xbmcgui.ListItem(getLS(56205), srcfeed.date))
    self.rightFrame_list.addItem(xbmcgui.ListItem(getLS(56206), srcfeed.srcurl))
    if (srcfeed.vip == "true"): self.rightFrame_list.addItem(xbmcgui.ListItem(getLS(56207), "Yes"))
    else: self.rightFrame_list.addItem(xbmcgui.ListItem(getLS(56207), "No"))
    if (len(srcfeed.magnet) >0): self.rightFrame_list.addItem(xbmcgui.ListItem(getLS(56208), "Yes"))
    else: self.rightFrame_list.addItem(xbmcgui.ListItem(getLS(56208), "No"))
    if (len(srcfeed.torrent) >0): self.rightFrame_list.addItem(xbmcgui.ListItem(getLS(56209), "Yes"))
    else: self.rightFrame_list.addItem(xbmcgui.ListItem(getLS(56209), "No"))


  def clearRightFrame(self):
    "Clear right frame with default values"
    self.rightFrame_info.setLabel(xbmc.getLocalizedString(416))
    self.rightFrame_list.reset()
    self.rightFrame_imgbox.setImage("Fanart_Fallback_Small.jpg")
