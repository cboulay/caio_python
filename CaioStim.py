import Caio_ctype
class TriggerBox(object):
##################################
# Uses Contec DAIO to send a TTL #
##################################
#Eventually I will take more of the logic from Caio_ctype into here
#and make Caio_ctype more general.
	
	def __init__(self):
		"""
		A GenericStimulator object allows interaction with a stimulator (e.g. Magstim or analog...??)
		Methods:
			stim_instance.trigger()
				This sends a bipolar pulse to the soundcard.
				
		Properties:
			stim_ready - True if the stimulator reports ready, False otherwise.
		"""
		self.caio = Caio_ctype.Caio(devname='AIO000', amplitude=1)
		
	def trigger(self):
		self.caio.stimulate()