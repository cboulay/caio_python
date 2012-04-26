import numpy as np
from Caio import Caio_ctype
import time
import Queue
import threading

class NMESThread(threading.Thread):
    def __init__(self, nmes):
        threading.Thread.__init__(self)
        self.nmes = nmes
        
    def run(self):
        my_fs = self.nmes._caio.fs
        #Set some initial sampling data
        self.nmes._caio.buffer = self.nmes.data
        #Enable and start
        self.nmes._caio.start()
        status = self.nmes._caio.status
        while status>=1:
            status = self.nmes._caio.status
            if status>1:
                self.nmes._caio.reset_memory()
                self.nmes._caio.reset_status()
                self.nmes._caio.buffer = self.nmes.data
                self.nmes._caio.start()
            if self.nmes._caio.sampling_times <= ((self.nmes.block_dur/1000) * my_fs):
                #Add another template*amplitude to the buffer
                self.nmes._caio.buffer = self.nmes.data
            #Probably need to wait for some msec here so the thread does not kill the processor.
            #time.sleep(self.nmes.block_dur/5000) #check each block 5 times 
            
class NMES(object):
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
        
        #Initialize hidden properties used by getters and setters
        self._block_dur = float(block_dur)
        self._width = float(width)
        self._frequency = float(frequency)
        self._channel = int(channel)
        self._amplitude = float(amplitude)
        self._caio = None
        self._template = None
        self.V2mA = float(5) #10V:50mA
        
        #Initialize the caio device
        caio = Caio_ctype.Caio(devname=devname)
        caio.n_channels=2
        caio.memory_type='FIFO'
        caio.clock_type='Internal'
        caio.fs=10000.0 #Hz
        caio.start_trigger='Software'
        caio.stop_trigger='Times' #Converting has completed for the specified times
        self._caio=caio
        
        #Generate the template using the default width, freq, and channel
        self._new_template()
        #Start the thread
        self.thread = NMESThread(self)
        self.thread.setDaemon(True)
        self.thread.start()
        
    def __del__(self):
        #TODO: kill the thread
        self._caio.stop()
    
    def _new_template(self):
        #Generate a block_dur pulse train using _width, _frequency, _channel and an amp of 1
        
        #Make a single cycle (depends on _frequency)
        n_per_cycle = np.ceil(self._caio.fs / self._frequency)
        data = np.zeros((n_per_cycle, self._caio.n_channels))
        
        #Make a single pulse at the beginning
        n_per_pulse = np.ceil((self._width/float(1000)) * self._caio.fs)
        data[0:n_per_pulse,self._channel-1] = 1.0
        
        #Repeat cycles to fill a block
        n_per_block = (self._block_dur/float(1000)) * self._caio.fs #float
        cyc_per_block = np.ceil(float(n_per_block) / n_per_cycle)
        data = np.tile(data, (cyc_per_block,1)) #Repeat data to fill a block
        data = data[0:n_per_block,:] #cutoff the excess
        
        self._template = data
    
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
    
    def _get_block_dur(self): return self._block_dur
    def _set_block_dur(self, value):
        self._block_dur = float(value)
        self._new_template()
    block_dur = property(_get_block_dur, _set_block_dur)
    
    def _get_amplitude(self): return self._amplitude * self.V2mA
    def _set_amplitude(self, value): self._amplitude = float(value) / self.V2mA
    amplitude = property(_get_amplitude, _set_amplitude)
    
    def _get_data(self):
        #print self._template.shape, self.amplitude, (self._template * self.amplitude).shape
        return self._template * self._amplitude
    def _set_data(self): pass #read-only
    data = property(_get_data, _set_data)