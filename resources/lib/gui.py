# -*- coding: utf-8 -*-

import os, sys
import xbmc
import xbmcgui
import PulseAudioEqualizerCore

_ = sys.modules['__main__'].__language__
__scriptname__ = sys.modules[ '__main__' ].__scriptname__
__addon__      = sys.modules[ '__main__' ].__addon__

class GUI(xbmcgui.WindowXMLDialog):
    controlId = 0
    control_state = {}
    counter = 1
    change_preset = 0

    gDebugMode = 0

    def __init__(self, *args, **kwargs): 
        if __addon__.getSetting('debug') == 'true':
            self.gDebugMode = 1			
        xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)

    def onInit(self):
        self.EqualizerCore = PulseAudioEqualizerCore.PulseAudioEqualizerCore(self.gDebugMode)
        
        self.getControl(1).setLabel(_(49999))
        
        self.getControl(201).setLabel(_(50000))
        self.getControl(202).setLabel(_(50001))
        self.getControl(203).setLabel(_(50002))   
        self.getControl(204).setLabel(_(50003))
        self.getControl(205).setLabel(_(50004))
        self.getControl(206).setLabel(_(50005))    
        self.getControl(207).setLabel(_(50006))
        self.getControl(208).setLabel(_(50007))            
           
        self.getControl(201).setSelected(self.EqualizerCore.status)
        self.getControl(202).setSelected(self.EqualizerCore.persistence)

        self.set_gui_values()
        
    def CreateBand(self,X,Y,bCaption,bVal):
        pass

    def onAction(self, action):
        if action in [10, 13]:
            self.closeDialog()

    def set_gui_values(self):
        self.change_preset = 0

        if self.EqualizerCore.preset != '':
            self.getControl(205).setEnabled(False)
        else:
            self.getControl(205).setEnabled(True)

        if len(self.EqualizerCore.userpreset)>0:
            self.getControl(204).setEnabled(True)
        else:
            self.getControl(204).setEnabled(False)

        self.getControl(203).setLabel(_(50002)+self.EqualizerCore.preset)

        for i in range(self.EqualizerCore.num_ladspa_controls):
        # dinamic !? CreateBand ???
        # num_ladspa_controls - const = 15 bands
        
           if i<15:
                current_input = int(self.EqualizerCore.ladspa_inputs[i])
                if current_input < 99:
                    a = current_input
                    suffix = _(50008)
                if current_input > 99 and current_input < 999:
                    a = current_input
                    suffix = _(50008)
                if current_input > 999 and current_input < 9999:
                    a = float(current_input)/1000
                    suffix = _(50009)
                if current_input > 9999:
                    a = float(current_input)/1000
                    suffix = _(50009)
                b=str(a)
                if b[-2:] == '.0':
                    c = b[:-2]
                else:
                    c = b
                self.getControl(1000*(i+1)+1).setLabel(c+' '+suffix)
                self.control_state[i] = self.dBToProcent(float(self.EqualizerCore.ladspa_controls[i]))
                self.getControl(1000*(i+1)+2).setPercent(self.control_state[i])
                self.getControl(1000*(i+1)+3).setLabel(str(float(self.EqualizerCore.ladspa_controls[i]))+' '+_(50010))
                self.counter += 1

    def dBToProcent(self, aValue):
        pVal = abs(self.EqualizerCore.minVal)+aValue
        return (pVal/self.EqualizerCore.rgVal)*100
        
    def ProcentTodB(self,aValue):
        pVal = (aValue/100)*self.EqualizerCore.rgVal
        return self.EqualizerCore.minVal+pVal

    def onFocus( self, controlId ):
        self.log('Focused: [%i] Previous [%s]' % (controlId,self.controlId,))
        if self.controlId == 0: self.controlId = controlId     
        if ( self.controlId >= 1000 ):
            self.slider_onfocus(controlId)
        self.controlId = controlId

    def onClick(self, controlId):
        if controlId == 201:
            self.EqualizerCore.status = self.getControl(201).isSelected()
            self.doApplySettings()
        elif controlId == 202:
            self.EqualizerCore.persistence = self.getControl(202).isSelected()
            self.doApplySettings()
        elif controlId == 203:
            self.doListPerset()
        elif controlId == 204: 
            self.doRemovePreset()            
        elif controlId == 205:
            self.doSavePreset()
        elif controlId == 206: 
            self.doResetSettings()            
        elif controlId == 207:
            self.doApplySettings()
        elif controlId == 208:
            self.closeDialog()
        elif controlId >= 1000:
            self.set_slider_value(controlId)

    def doListPerset(self):
        dialog = xbmcgui.Dialog()
        ret = dialog.select(_(50011), self.EqualizerCore.rawpresets)
        preset = self.EqualizerCore.rawpresets[ret]
        ret = dialog.yesno(_(49999), _(50016)+preset+' ?', nolabel=_(50014), yeslabel=_(50015))
        if ret == 1:
            self.getControl(203).setLabel(_(50002)+preset)
            self.getControl(205).setEnabled(False)
            self.EqualizerCore.preset = preset
            self.change_preset = 0
            self.EqualizerCore.LoadPreset()
            self.set_gui_values()

    def doSavePreset(self):
        keyboard = xbmc.Keyboard( '',_(50012), False)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            if keyboard.getText() != '':
                self.EqualizerCore.preset = keyboard.getText()
                self.EqualizerCore.SavePreset()
                self.set_gui_values()

    def doApplySettings(self):
        self.EqualizerCore.ApplySettings()

    def doResetSettings(self):
        self.EqualizerCore.ResetSettings()

    def doRemovePreset(self):
        dialog = xbmcgui.Dialog()
        ret = dialog.select(_(50003), self.EqualizerCore.userpreset)
        preset = self.EqualizerCore.userpreset[ret]
        ret = dialog.yesno(_(49999), _(50013)+preset+' ?', nolabel=_(50014), yeslabel=_(50015))
        if ret == 1:
            self.EqualizerCore.RemovePerset(preset)
            self.set_gui_values()

    def set_slider_value( self, controlId ):      
        i = int(controlId/1000)
        pvalue = self.getControl((i*1000)+2).getPercent()
        if self.control_state[i-1] != pvalue:
            if self.change_preset == 0:
                self.change_preset = 1
                self.EqualizerCore.preset = ''
                self.getControl(205).setEnabled(True)
                self.getControl(203).setLabel(_(50002))        
            slider_value = self.ProcentTodB(pvalue)
            self.EqualizerCore.ladspa_controls[i-1] = slider_value
            self.getControl(controlId+1).setLabel(str(float(slider_value))+' '+_(50010))
            self.EqualizerCore.ApplySettings()
        

    def slider_onfocus(self, controlId):
        i = int(controlId/1000)

    def log(self, msg):
        if self.gDebugMode>0:
            xbmc.log('##### [%s] - Debug msg: %s' % (__scriptname__,msg,),level=xbmc.LOGDEBUG )

    def closeDialog(self):
        self.close()
