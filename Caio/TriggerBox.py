import numpy as np
from Caio import Caio_ctype
class TTL(object):
##################################
# Uses Contec DAIO to send a TTL #
##################################
	
	def __init__(self, devname=None):
		"""
		Loads up a Caio device with the sole purpose of sending TTLs.
		TTLs are sent with instance.trigger()
		TTL amplitude, width, channel are modifiable.
		
		Methods:
			instance.trigger()
			instance.set_TTL(amplitude=5, width=50, channel=1)
				Generates a numpy.array based on the input variables
				and passes them off to the contec device.
				Magstim uses defaults and never requires them to change
		
		Properties:
			instance.data - R/W the data we think are in the Caio buffer
				Use this setter if you want to use something other than a TTL
				or if you want to use multiple channels for output.
				
		The TTL can be further refined by modifying instance._caio 
		"""
		
		#Hidden properties used by getters and setters
		self._amplitude=5
		self._width=50
		self._channel=1
		self._caio = None
		self._data = None
		
		#Initialize the trigger box then set some defaults
		caio = Caio_ctype.Caio(devname=devname)
		caio.n_channels=2
		caio.memory_type='RING'#FIFO is default
		caio.clock_type='Internal'
		caio.fs=1000 #Hz
		caio.start_trigger='Software'
		caio.stop_trigger='Times' #Converting has completed for the specified times
		caio.repeat_times=1 #0=Infinite
		caio.reset_memory()
		self._caio=caio
		
		self.amplitude=0
		self.trigger() #Necessary to make sure the output is at 0
		#Create default output data, i.e. 5V 50ms TTL on channel 1
		self.amplitude=5
		
		
	def _get_amplitude(self): return self._amplitude
	def _set_amplitude(self, value): self.set_TTL(amplitude=value)
	amplitude = property(_get_amplitude, _set_amplitude)
	
	def set_TTL(self, amplitude=None, width=None, channel=None):
		#amplitude in V, width in ms, channel in base 1 (first = 1)
		if amplitude: self._amplitude = amplitude
		if width: self._width = width
		if channel: self._channel = channel
		n_samples = np.ceil((float(self._width)/1000) * self._caio.fs)
		data=np.zeros((n_samples+1, self._caio.n_channels))
		data[:-1,self._channel-1]=self._amplitude
		self.data=data
		
	def _get_data(self):
		return self._data
	def _set_data(self, value):
		self._caio.reset_memory()
		self._caio.buffer = value
		self._data = value
	data = property(_get_data, _set_data)
	
	def trigger(self):
		self._caio.start()