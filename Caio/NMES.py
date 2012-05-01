import numpy as np
from Caio import Caio_ctype
import time
import Queue
import threading

class NMES(object):
#####################################################
# Uses Contec DAIO to send a continuous pulse train #
#####################################################
    
    def __init__(self, devname=None, width=1.0, frequency=100.0, channel=2, amplitude=0.0):
        """
        Loads up a Caio device with the sole purpose of sending
        a continuous pulse train.
        Pulse train amplitude, width, frequency, and channel are modifiable.
        
        Methods:
            
        Properties:
        """
        
        #Initialize hidden properties used by getters and setters
        self._width = float(width)
        self._frequency = float(frequency)
        self._channel = int(channel)
        self._amplitude = float(amplitude)
        self._caio = None
        self._template = None
        #self.V2mA = lambda x: float(5*x) #10V:50mA
        self.V2mA = float(5.0)
        
        #Initialize the caio device
        caio = Caio_ctype.Caio(devname=devname)
        caio.n_channels=2
        #caio.memory_type='FIFO'
        caio.clock_type='Internal'
        caio.fs=10000.0 #Hz
        caio.start_trigger='Software'
        caio.stop_trigger='Times' #Converting has completed for the specified times
        caio.reset_memory()
        self._caio=caio
        
    def __del__(self):
        self.amplitude = 0
        self._caio.stop()
        
    def _new_template(self):
        #Generate a pulse using _width, _frequency, _channel and an amp of 1
        
        #Make a single cycle (depends on _frequency)
        n_per_cycle = np.ceil(self._caio.fs / self._frequency)
        data = np.zeros((n_per_cycle, self._caio.n_channels))
        
        #Make a single pulse at the beginning
        n_per_pulse = np.ceil((self._width/float(1000)) * self._caio.fs)
        data[0:n_per_pulse,self._channel-1] = 1.0
        self._template = data
        return self._template #This will be sub-classed and data will be used.
        
    def _get_width(self): return self._width
    def _set_width(self, value):
        self._width = float(value)
        self._new_template()
    width = property(_get_width, _set_width)
    
    def _get_freq(self): return self._frequency
    def _set_freq(self, value):
        self._frequency = float(value)
        self._new_template()
    frequency = property(_get_freq, _set_freq)
    
    def _get_channel(self): return self._channel
    def _set_channel(self, value):
        self._channel = int(value)
        self._new_template()
    channel = property(_get_channel, _set_channel)
    
    def _get_amplitude(self): return self._amplitude * self.V2mA
    def _set_amplitude(self, value): self._amplitude = float(min(value,15.0)) / self.V2mA #Hard cap of 15 mA
    amplitude = property(_get_amplitude, _set_amplitude)
    
    def _get_data(self):
        #print self._template.shape, self.amplitude, (self._template * self.amplitude).shape
        return self._template * self._amplitude
    def _set_data(self): pass #read-only
    data = property(_get_data, _set_data)

class NMESThread(threading.Thread):
    def __init__(self, nmes):
        threading.Thread.__init__(self)
        self.nmes = nmes
        self.running = False
        
    def run(self):
        my_fs = self.nmes._caio.fs
        #Set some initial sampling data
        self.nmes._caio.buffer = self.nmes.data
        #Enable and start
        self.nmes._caio.start()
        self.running = True
        status = self.nmes._caio.status
        while self.running:
            status = self.nmes._caio.status
            if not status==1:
                self.nmes._caio.reset_memory()
                self.nmes._caio.reset_status()
                self.nmes._caio.buffer = self.nmes.data
                self.nmes._caio.start()
            if self.nmes._caio.sampling_times <= 1.5 * ((self.nmes.block_dur/1000.0) * my_fs):
                #Add another template*amplitude to the buffer
                self.nmes._caio.buffer = self.nmes.data
            #Probably need to wait for some msec here so the thread does not kill the processor.
        self.nmes._caio.stop()
            
class NMESFIFO(NMES):
#####################################################
# Uses Contec DAIO to send a continuous pulse train #
#####################################################
    def __init__(self, devname=None, block_dur=100.0, width=1.0, frequency=100.0, channel=2, amplitude=0.0):
        """
        Loads up a Caio device with the sole purpose of sending
        a continuous pulse train.
        Pulse train amplitude, width, frequency, and channel are modifiable.
        
        Methods:
            
        Properties:
        """
        NMES.__init__(self, devname=devname, width=width, frequency=frequency, channel=channel, amplitude=amplitude)#Call the super init
        
        #Initialize hidden properties used by getters and setters
        self._block_dur = float(block_dur)
        self._caio.memory_type='FIFO'
        
        #Generate the template using the default width, freq, and channel
        self._new_template()
        #Start the thread
        self.thread = NMESThread(self)
        self.thread.setDaemon(True)
        #self.thread.start()
        
    def __del__(self):
        self.thread.running = False
        NMES.__del__(self)
        
    def _get_running(self):
        return self.thread.running
    def _set_running(self, value):
        if value: self.thread.start()
        else: self.thread.running = False
    running = property(_get_running, _set_running)
        
    
    def _new_template(self):
        #Generate a block_dur pulse train using _width, _frequency, _channel and an amp of 1
        data = NMES._new_template(self)
        
        #Repeat cycles to fill a block
        n_per_cycle = np.ceil(self._caio.fs / self._frequency)
        n_per_block = (self._block_dur/float(1000)) * self._caio.fs #float
        cyc_per_block = np.ceil(float(n_per_block) / n_per_cycle)
        data = np.tile(data, (cyc_per_block,1)) #Repeat data to fill a block
        data = data[0:n_per_block,:] #cutoff the excess
        self._template = data
          
    def _get_block_dur(self): return self._block_dur
    def _set_block_dur(self, value):
        self._block_dur = float(value)
        self._new_template()
    block_dur = property(_get_block_dur, _set_block_dur)
    
class NMESRING(NMES):
#####################################################
# Uses Contec DAIO to send a continuous pulse train #
#####################################################
    def __init__(self, devname=None, width=1.0, frequency=100.0, channel=2, amplitude=0.0):
        """
        Loads up a Caio device with the sole purpose of sending
        a continuous pulse train.
        Pulse train amplitude, width, frequency, and channel are modifiable.
        
        Methods:
            
        Properties:
        """
        NMES.__init__(self, devname=devname, width=width, frequency=frequency, channel=channel, amplitude=amplitude)#Call the super init
        self._caio.memory_type='RING'
        self._caio.repeat_times = 0
        #Generate the template using the default width, freq, and channel
        self._new_template()
        
    def __del__(self):
        self.thread.running = False
        NMES.__del__(self)
        
    def _get_running(self): return self._caio.status
    def _set_running(self, value):
        if value:
            #Make sure the current data are in the buffer
            self._caio.buffer = self.data
            self._caio.start()
        else:
            self._caio.stop()
    running = property(_get_running, _set_running)
    
    def _get_amplitude(self): return self._amplitude * self.V2mA
    def _set_amplitude(self, value):
        self.running = False
        self._amplitude = float(min(value,10.0)) / self.V2mA #Hard cap of 10 mA
        self.running = True
        
    amplitude = property(_get_amplitude, _set_amplitude)