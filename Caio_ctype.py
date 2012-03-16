from ctypes import *
class Caio(object):
	def __init__(self, devname='AIO000',nchans=1, amplitude=5):
		#TODO: Create a few variables to be exposed, e.g. fs, data, devname, memType
		#TODO: Control these variables through getters and setters.
		#TODO: Hide other instance variables. e.g., _aio, _Id
		self.aio=windll.LoadLibrary("caio.dll")
		self.devname=devname
		self.Id=c_short()
		RET = self.aio.AioInit(self.devname,byref(self.Id))
		#check that RET===0
				
		#Clock #Default is 1000
		#Start Condition #Default is software
		#Stop Condition
		#Event
		
		#Default data is a 50ms TTL in a RING buffer.
		#RET=aio.AioSetAoTransferMode(self.Id, 0)# [0]:device or 1:user buffer; We will use Device buffer mode so nothing needs to be done here.
		RET=self.aio.AioSetAoMemoryType(self.Id, 1)# [0]: FIFO, 1:RING
		n_samples=51
		self.data = (c_float*n_samples)()
		for i in range(len(self.data)):
			self.data[i]=amplitude
		self.data[n_samples-1]=0
		self.data[0]=5
		RET = self.aio.AioSetAoSamplingDataEx(self.Id, len(self.data), byref(self.data))
				
		#Channel
		AoMaxChannels=c_short()
		RET=self.aio.AioGetAoMaxChannels(self.Id,byref(AoMaxChannels))
		nchans=min(nchans,AoMaxChannels.value)
		setchans=c_short(nchans)
		RET=self.aio.AioSetAoChannels(self.Id,setchans)

	def _fill_data_(self):
		#Put the data in the buffer.
		RET = self.aio.AioSetAoSamplingDataEx(self.Id, len(self.data), byref(self.data))
		#RING type buffer always returns 0 samplingtimes ??
		#buf_samples=c_long()
		#RET = self.aio.AioGetAoSamplingTimes (self.Id, byref(buf_samples))
		#check that buf_samples.value==n_samples
		
	def __del__(self):
		RET=self.aio.AioStopAo(self.Id)
		RET = self.aio.AioExit(self.Id)
		
	def stimulate(self):
		RET=self.aio.AioStartAo(self.Id)
		#If FIFO, this will remove data from buffer.
	
	def reset(self):
		pass
		
	def getAoStatus(self):# long AioGetAoStatus(short Id, long * AoStatus);
		status=c_long()
		RET = self.aio.AioGetAoStatus(self.Id, byref(status))
		#Check that RET==0
		#If RET==7, then execute reset.