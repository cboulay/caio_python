import numpy as np
from Caio import Caio_ctype
class TriggerBox(object):
##################################
# Uses Contec DAIO to send a TTL #
##################################
	
	def __init__(self, devname=None, data=None):
		"""
		A GenericStimulator object allows interaction with a stimulator (e.g. Magstim or analog...??)
		Methods:
			stim_instance.trigger()
				This sends a bipolar pulse to the soundcard.
				
		Properties:
			stim_ready - True if the stimulator reports ready, False otherwise.
		"""
		caio = Caio_ctype.Caio(devname=devname)
		
		#Initialize with some defaults
		caio.n_channels=2
		caio.memory_type='RING'#FIFO is default
		caio.clock_type='Internal'
		caio.fs=1000 #Hz
		caio.start_trigger='Software'
		caio.stop_trigger='Times' #Converting has completed for the specified times
		caio.repeat_times=1 #0=Infinite
		caio.reset_memory()
		self.caio=caio
		
		#Create default output data if none provided.
		if not data: self.set_TTL()#using defaults
		else: self.caio.buffer=data
		
	def trigger(self):
		self.caio.start()
		
	def set_TTL(self, amplitude=5, width=50, channel=1):
		#amplitude in V, width in ms, channel in base 1 (first = 1)
		n_samples = np.ceil((float(width)/1000) * self.caio.fs)
		data=np.zeros((n_samples+1, self.caio.n_channels))
		data[:-1,channel-1]=amplitude
		self.caio.buffer=data