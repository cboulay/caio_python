from Caio import Caio_ctype
class TriggerBox(object):
##################################
# Uses Contec DAIO to send a TTL #
##################################
	
	def __init__(self, devname='AIO000', data=None):
		"""
		A GenericStimulator object allows interaction with a stimulator (e.g. Magstim or analog...??)
		Methods:
			stim_instance.trigger()
				This sends a bipolar pulse to the soundcard.
				
		Properties:
			stim_ready - True if the stimulator reports ready, False otherwise.
		"""
		caio = Caio_ctype.Caio(devname=devname)
		
		caio.n_channels=2
		caio.memory_type='RING'#FIFO is default
		caio.clock_type='Internal'
		caio.fs=1000 #Hz
		caio.start_trigger='Software'
		caio.stop_trigger='Times' #Converting has completed for the specified times
		caio.repeat_times=1 #0=Infinite
		caio.reset_memory()
		
		#Create default output data if none provided.
		if not data:
			import numpy as np
			#Default to 50ms 5V pulse.
			n_samples = ceil(0.05 * caio.fs)
			data=5*np.ones((n_samples+1, caio.n_channels))
			data[-1,:]=0
		caio.buffer=data
		self.caio=caio
		
	def trigger(self):
		self.caio.start()