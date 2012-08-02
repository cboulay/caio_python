import numpy as np
from Caio import Caio_ctype
import time
class TTL(object):
##################################
# Uses Contec DAIO to send a TTL #
##################################
	
	def __init__(self, devname=None, channel=1, amplitude=5, width=5, offset=0):
		"""
		Loads up a Caio device with the sole purpose of sending TTLs.
		TTLs are sent with instance.trigger()
		Optionally can be instantiated with some attributes for 1 channel.
		
		Methods:
			instance.trigger()
			instance.set_TTL(channel=1, amplitude=None, width=None, offset=None)
				Modifies the buffer for the given channel.
				Magstim uses defaults and never requires them to change.
		
		Properties:
			instance.data - R/W the data we think are in the Caio buffer
				Use this setter if you want to use something other than a TTL
				or if you want to use multiple channels for output.
				
		The TTL can be further refined by modifying instance._caio 
		"""
		
		#Hidden properties
		self._data = None
		self._attributes = [{},{}]
		self._attributes[0] = {'amplitude':0.0, 'width':0.0, 'offset':0.0}
		self._attributes[1] = {'amplitude':0.0, 'width':0.0, 'offset':0.0}
		
		#Initialize the device with the appropriate settings
		caio = Caio_ctype.Caio(devname=devname)
		caio.n_channels=2
		caio.memory_type='RING'#FIFO is default
		caio.clock_type='Internal'
		caio.fs=10000 #Hz
		caio.start_trigger='Software'
		caio.stop_trigger='Times' #Converting has completed for the specified times
		caio.repeat_times=1 #0=Infinite
		caio.reset_memory()
		self._caio=caio
		
		#Initialize the buffer to 0 and trigger
		self.data = np.zeros((1, self._caio.n_channels))
		self.trigger()
		
		#Design the data using stored settings.
		self.set_TTL(channel=channel, amplitude=amplitude, width=width, offset=offset)
	
	def set_TTL(self, channel=1, amplitude=None, width=None, offset=None):
		if amplitude: self._attributes[channel-1]['amplitude'] = amplitude
		if width: self._attributes[channel-1]['width'] = width
		if offset: self._attributes[channel-1]['offset'] = offset
		
		#Determine how many samples we need and create a 0 buffer.
		max_time = np.max([a['width']+a['offset'] for a in self._attributes])
		n_samples = np.ceil((float(max_time)/1000) * self._caio.fs)
		data = np.zeros((n_samples+1, self._caio.n_channels))
		
		#Adjust the buffer for each channel.
		for cc in range(self._caio.n_channels):
			offset_samples = np.ceil((float(self._attributes[cc]['offset'])/1000) * self._caio.fs)
			pulse_samples = np.ceil((float(self._attributes[cc]['width'])/1000) * self._caio.fs)
			data[offset_samples:offset_samples+pulse_samples,cc-1] = self._attributes[cc]['amplitude']
		self.data = data
		
	def _get_data(self):
		return self._data
	def _set_data(self, value):
		self._caio.reset_memory()
		self._caio.buffer = value
		self._data = value
	data = property(_get_data, _set_data)
	
	def trigger(self):
		self._caio.start()