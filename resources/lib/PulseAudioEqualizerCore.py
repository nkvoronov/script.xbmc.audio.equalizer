# -*- coding: utf-8 -*-

import os, sys
import xbmc

__scriptname__ = sys.modules[ '__main__' ].__scriptname__

configdir1 = '/.config/pulse'
configdir2 = '/.pulse'
eqconfig = '/equalizerrc'
eqpresets = '.availablepresets'
presetusrdir = '/presets'
presetsysdir = '/usr/share/pulseaudio-equalizer/presets'

class PulseAudioEqualizerCore:
    rawdata = {}
    rawpresets = {}
    ladspa_filename = ''
    ladspa_name = ''
    ladspa_label = ''
    preamp = 1.0
    preset = ''
    status = 0
    persistence = 0
    ranges = {}
    num_ladspa_controls = 15
    ladspa_controls = {}
    ladspa_inputs = {}

    minVal = -30
    maxVal = 30
    rgVal = 60

    clearpreset = 1
    presetmatch = 0

    userpreset = {}

    configdir = ''
    gDebugMode = 0    

    def __init__(self, debugLevel):
        self.gDebugMode = debugLevel
        self.log('Init core')
        if self.checkPlatform()== 1:
            self.configdir = ''
        if os.path.isfile(os.getenv('HOME')+configdir1 + eqconfig):
            self.configdir = os.getenv('HOME')+configdir1
        elif os.path.isfile(os.getenv('HOME')+configdir2 + eqconfig):
            self.configdir = os.getenv('HOME')+configdir2
        else:
            self.log('No patch config')
        if self.configdir != '':
            self.GetSettings()

    def checkPlatform(self):
        if not sys.platform.startswith('linux'):
            self.log('Invalid platform: ' + sys.platform)
            return 0
        return 1

    def log(self, msg):
        if self.gDebugMode>0:
            xbmc.log('##### [%s] - Debug msg: %s' % (__scriptname__,msg,),level=xbmc.LOGDEBUG )

    def GetSettings(self):
        self.log('Getting settings...')      
        os.system('pulseaudio-equalizer interface.getsettings')
        f = open(self.configdir+eqconfig, 'r')
        self.rawdata=f.read().split('\n')
        f.close()
        self.rawpresets = {}
        f = open(self.configdir+eqconfig+eqpresets, 'r')
        self.rawpresets=f.read().split('\n')
        f.close()
        del self.rawpresets[len(self.rawpresets)-1]
        self.ladspa_filename = str(self.rawdata[0])
        self.ladspa_name = str(self.rawdata[1])
        self.ladspa_label = str(self.rawdata[2])
        self.preamp = (self.rawdata[3])
        self.preset = str(self.rawdata[4])
        self.status = int(self.rawdata[5])
        self.persistence = int(self.rawdata[6])
        self.ranges = self.rawdata[7:9]
        self.num_ladspa_controls = int(self.rawdata[9])
        self.ladspa_controls = self.rawdata[10:(10+self.num_ladspa_controls)]
        self.ladspa_inputs = self.rawdata[(10+self.num_ladspa_controls):(10+self.num_ladspa_controls)+(self.num_ladspa_controls)]
        self.clearpreset = 1
        self.presetmatch = 0
        for i in range(len(self.rawpresets)):
            if self.rawpresets[i] == self.preset:
                self.presetmatch = 1
                
        self.GetUserPresets()

        self.minVal = int(self.ranges[0])
        self.maxVal = int(self.ranges[1])

        if self.minVal>self.minVal:
            self.minVal = 0     

        self.rgVal = abs(self.minVal)+self.maxVal

    def ApplySettings(self):
        self.log('Applying settings...')
        f = open(self.configdir+eqconfig, 'w')
        del self.rawdata[:]
        self.rawdata.append(str(self.ladspa_filename))
        self.rawdata.append(str(self.ladspa_name))
        self.rawdata.append(str(self.ladspa_label))
        self.rawdata.append(str(self.preamp))
        self.rawdata.append(str(self.preset))
        self.rawdata.append(str(self.status))
        self.rawdata.append(str(self.persistence))
        for i in range(2):
            self.rawdata.append(str(self.ranges[i]))
        self.rawdata.append(str(self.num_ladspa_controls))
        for i in range(self.num_ladspa_controls):
            self.rawdata.append(str(self.ladspa_controls[i]))
        for i in range(self.num_ladspa_controls):
            self.rawdata.append(str(self.ladspa_inputs[i]))
        for i in self.rawdata:
            f.write(str(i)+'\n')
        f.close()
        os.system('pulseaudio-equalizer interface.applysettings')

    def LoadPreset(self):
        self.log('Load Preset')
        self.presetmatch = 0
        for i in range(len(self.rawpresets)):
            if self.rawpresets[i] == self.preset:
                self.presetmatch = 1
        if self.presetmatch == 1:
            if os.path.isfile(self.configdir+presetusrdir+'/'+self.preset+'.preset'):
                f = open(self.configdir+presetusrdir+'/'+self.preset+'.preset', 'r')
                self.rawdata=f.read().split('\n')
                f.close
            elif os.path.isfile(presetsysdir+'/'+self.preset+'.preset'):
                f = open(presetsysdir+'/'+self.preset+'.preset', 'r')
                self.rawdata=f.read().split('\n')
                f.close
            self.ladspa_filename = str(self.rawdata[0])
            self.ladspa_name = str(self.rawdata[1])
            self.ladspa_label = str(self.rawdata[2])
            #preamp = (rawdata[3])
            self.preset = str(self.rawdata[4])
            self.num_ladspa_controls = int(self.rawdata[5])
            self.ladspa_controls = self.rawdata[6:(6+self.num_ladspa_controls)]
            self.ladspa_inputs = self.rawdata[(6+self.num_ladspa_controls):(6+self.num_ladspa_controls)+(self.num_ladspa_controls)]
            # Set preset again due to interference from scale modifications
            self.preset = str(self.rawdata[4])
            self.clearpreset = 1
            # Apply settings (which will save new preset as default)
            self.ApplySettings()
            # Refresh (and therefore, sort) preset list
            self.GetSettings()

    def SavePreset(self):
        self.log('Save Preset')
        if self.preset == '':
            self.log('Invalid preset name')
        else:
            f = open(self.configdir+presetusrdir+'/'+self.preset+'.preset', 'w')
            del self.rawdata[:]
            self.rawdata.append(str(self.ladspa_filename))
            self.rawdata.append(str(self.ladspa_name))
            self.rawdata.append(str(self.ladspa_label))
            self.rawdata.append(str(self.preamp))
            self.rawdata.append(str(self.preset))
            self.rawdata.append(str(self.num_ladspa_controls))
            for i in range(self.num_ladspa_controls):
                self.rawdata.append(str(self.ladspa_controls[i]))
            for i in range(self.num_ladspa_controls):
                self.rawdata.append(str(self.ladspa_inputs[i]))
            for i in self.rawdata:
                f.write(str(i)+'\n')
            f.close()
            # Apply settings (which will save new preset as default)
            self.ApplySettings()
            # Refresh (and therefore, sort) preset list
            self.GetSettings()

    def ResetSettings(self):
        self.log('Resetting to defaults...')
        os.system('pulseaudio-equalizer interface.resetsettings')
        self.GetSettings()

    def GetUserPresets(self):
        self.userpreset = []
        files = os.listdir(self.configdir+presetusrdir)
        for file in files:
            if file.endswith('.preset'):
                 self.userpreset.append(file.split('.')[0])

    def RemovePerset(self, presetname):
        self.log('Remove Perset '+presetname)
        os.remove(self.configdir+presetusrdir+'/'+presetname+'.preset')
        self.GetSettings()
        if self.preset == presetname:
            self.preset = '';    
        self.ApplySettings()
