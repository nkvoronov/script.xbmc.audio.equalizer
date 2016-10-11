import sys
import os
import xbmc
import xbmcaddon

__addon__      = xbmcaddon.Addon('script.xbmc.audio.equalizer')

# Script constants
__scriptname__ = __addon__.getAddonInfo('name')
__id__ = __addon__.getAddonInfo('id')
__author__ = __addon__.getAddonInfo('author')
__version__ = __addon__.getAddonInfo('version')
__path__ = __addon__.getAddonInfo('path')
__cwd__        = __addon__.getAddonInfo('path')
__profile__    = xbmc.translatePath(__addon__.getAddonInfo('profile'))
__resource__   = xbmc.translatePath(os.path.join( __cwd__, 'resources', 'lib' ))
__language__   = __addon__.getLocalizedString

sys.path.append (__resource__)

xbmc.log('##### [%s] - Version: %s' % (__scriptname__,__version__,),level=xbmc.LOGDEBUG )

if (__name__ == "__main__"):
    import gui
    ui = gui.GUI('%s.xml' % __id__.replace('.','-') , __cwd__, 'default')
    ui.doModal()
    del ui

sys.modules.clear()
