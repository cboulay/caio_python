from ctypes import *
import numpy as np

class Caio(object):
	def __init__(self, devname=None):
		#TODO: load the library in linux? (Linux drivers exist)
		self._aio=windll.LoadLibrary("caio.dll")
		
		if not devname: devname=self._dev_names()
		self.devname=devname 
		
		#Init device
		self._Id=c_short()
		RET = self._aio.AioInit(self.devname,byref(self._Id))
		self._handle_ret('AioInit', RET)
		
	def __del__(self):
		self.stop()
		RET = self._aio.AioExit(self._Id)
		
	#Resolution
	def _get_resolution(self):
		resolution = c_short()
		RET = self._aio.AioGetAoResolution(self._Id, byref(resolution))
		self._handle_ret('AioGetAoResolution', RET)
		return resolution.value
	def _set_resolution(self, value):
		pass #read-only
	n_bits = property(_get_resolution, _set_resolution)
	
	#Channel
	#setaochannels, getaochannels, getaomaxchannels
	def _get_ao_max_channels(self):
		maxchans = c_short()
		RET = self._aio.AioGetAoMaxChannels(self._Id, byref(maxchans))
		self._handle_ret('AioGetAoMaxChannels', RET)
		return maxchans.value
	def _set_ao_max_channels(self, value):
		pass #read-only
	max_chans = property(_get_ao_max_channels, _set_ao_max_channels)
	
	def _get_ao_channels(self):
		nchannels = c_short()
		RET = self._aio.AioGetAoChannels(self._Id, byref(nchannels))
		self._handle_ret('AioGetAoChannels', RET)
		return nchannels.value
	def _set_ao_channels(self, value):
		nchannels = c_short(np.min((value,self.max_chans)))
		RET = self._aio.AioSetAoChannels(self._Id, nchannels)
		self._handle_ret('AioSetAoChannels', RET)
	n_channels = property(_get_ao_channels, _set_ao_channels)
	
	#Range
	def get_ao_range_for_channel(self, channel_id=0):
		ao_channel = c_short(channel_id)
		ao_range = c_short()
		RET = self._aio.AioGetAoRange(self._Id, ao_channel, byref(ao_range))
		self._handle_ret('AioGetAoRange', RET)
		return ao_range.value
	def set_ao_range_for_channel(self, channel_id='all', AoRange='PM10'):
		#Range is fixed to PM10 on my device so I cannot test others.
		if AoRange=='PM10': ao_range=c_short(0)
		if channel_id=='all':
			RET = self._aio.AioSetAoRangeAll(self._Id, ao_range)
			self._handle_ret('AioSetAoRangeAll', RET)
		else:
			chan = c_short(channel_id)
			RET = self._aio.AioSetAoRange(self._Id, chan, ao_range)
			self._handle_ret('AioSetAoRange', RET)
	
	#Memory Type
	def _get_memory_type(self):#proxy for AioGetMemoryType
		mem_type=c_short()
		RET=self._aio.AioGetAoMemoryType(self._Id, byref(mem_type))
		self._handle_ret('AioGetAoMemoryType', RET)
		if mem_type.value==1: return 'RING'
		elif mem_type.value==0: return 'FIFO'
	def _set_memory_type(self, value='FIFO'):#proxy for AioSetAoMemoryType
		if value=='RING': mem_type=c_short(1)
		elif value=='FIFO': mem_type=c_short(0)
		RET = self._aio.AioSetAoMemoryType(self._Id, mem_type)
		self._handle_ret('AioSetAoMemoryType', RET)
	memory_type = property(_get_memory_type, _set_memory_type)
	
	#Repeat
	def _get_repeat_times(self):
		repeats = c_long()
		RET = self._aio.AioGetAoRepeatTimes(self._Id, byref(repeats))
		self._handle_ret('AioGetAoRepeatTimes', RET)
		return repeats.value
	def _set_repeat_times(self, value):#default is 0 = infinite
		repeats = c_long(value)
		RET = self._aio.AioSetAoRepeatTimes(self._Id, repeats)
		self._handle_ret('AioSetAoRepeatTimes', RET)
	repeat_times = property(_get_repeat_times, _set_repeat_times)
	
	#Clock
	def _get_clock_type(self):
		clock_type = c_short()
		RET = self._aio.AioGetAoClockType(self._Id, byref(clock_type))
		self._handle_ret('AioGetAoClockType', RET)
		#0 = Internal, 1=External, 10=Event controller
		return {0:'Internal', 1:'External', 10:'Event controller'}.get(clock_type.value)
	def _set_clock_type(self, value='Internal'):
		value = {'Internal':0, 'External':1, 'Event controller':10}.get(value)
		value = c_short(value)
		RET = self._aio.AioSetAoClockType(self._Id, value)
		self._handle_ret('AioGetAoClockType', RET)
	clock_type = property(_get_clock_type, _set_clock_type)
	
	def _get_sampling_clock(self):
		clock = c_float()
		RET = self._aio.AioGetAoSamplingClock(self._Id, byref(clock))
		self._handle_ret('AioGetAoSamplingClock', RET)
		return 1000000*(1/clock.value)
	def _set_sampling_clock(self, value):
		#Passed-in value in Hz. Function wants sample duration in usec.
		#e.g. 0.2kHz = 200 samples / sec = 5000 usec per sample
		#Usable AoSamplingClock is 10 to 107374182
		clock = c_float(1000000/value)
		RET = self._aio.AioSetAoSamplingClock(self._Id, clock)
		self._handle_ret('AioSetAoSamplingClock', RET)
	fs = property(_get_sampling_clock, _set_sampling_clock)
	
	#Setting Data
	def _get_ao_buffer(self):
		pass
	def _set_ao_buffer(self, data):
		n_samples, n_channels=data.shape
		data=data[:,0:self.max_chans]#trim excess channels
		data=np.reshape(data,(n_samples*n_channels,))
		temp_data = (c_float*(data.shape[0]))()
		for i in range(data.shape[0]): temp_data[i]=data[i]
		RET = self._aio.AioSetAoSamplingDataEx(self._Id, c_long(n_samples), temp_data)
		self._handle_ret('AioSetAoSamplingDataEx', RET)
	buffer = property(_get_ao_buffer, _set_ao_buffer)
		
	def _get_sampling_times(self):
		ao_sampling_time=c_long()
		RET = self._aio.AioGetSamplingTimes(self._Id, byref(ao_sampling_time))
		self._handle_ret('AioGetSamplingTimes', RET)
		return ao_sampling_time.value
	def _set_sampling_times(self, value):
		pass #read-only
	sampling_times = property(_get_sampling_times, _set_sampling_times)
	
	#StartCondition
	def _get_start_trigger(self):
		trigger=c_short()
		RET = self._aio.AioGetAoStartTrigger(self._Id, byref(trigger))
		self._handle_ret('AioGetAoStartTrigger', RET)
		return {0:'Software', 1:'External trigger rising edge', 2:'External trigger falling edge', 10:'Event controller output'}.get(trigger.value)
	def _set_start_trigger(self,value='Software'):
		value = {'Software':0, 'External trigger rising edge':1, 'External trigger falling edge':2, 'Event controller output':10}.get(value)
		value = c_short(value)
		RET = self._aio.AioSetAoStartTrigger(self._Id, value)
		self._handle_ret('AioSetAoStartTrigger', RET)
	start_trigger = property(_get_start_trigger, _set_start_trigger)
	
	#StopCondition
	def _get_stop_trigger(self):
		trigger=c_short()
		RET = self._aio.AioGetAoStopTrigger(self._Id, byref(trigger))
		self._handle_ret('AioGetAoStopTrigger', RET)
		return {0:'Times', 1:'External trigger rising edge', 2:'External trigger falling edge', 10:'Event controller output'}.get(trigger.value)
	def _set_stop_trigger(self,value='Times'):
		value = {'Times':0, 'External trigger rising edge':1, 'External trigger falling edge':2, 'Event controller output':10}.get(value)
		value = c_short(value)
		RET = self._aio.AioSetAoStopTrigger(self._Id, value)
		self._handle_ret('AioSetAoStopTrigger', RET)
	stop_trigger = property(_get_stop_trigger, _set_stop_trigger)
	
	#Action
	def start(self):
		RET=self._aio.AioStartAo(self._Id)
		self._handle_ret('AioStartAo', RET)
		#If FIFO, this will remove data from buffer.
	def stop(self):
		RET = self._aio.AioStopAo(self._Id)
		self._handle_ret('AioStopAo', RET)
		
	#Status
	def _get_status(self):# long AioGetAoStatus(short Id, long * AoStatus);
		status=c_long()
		RET = self._aio.AioGetAoStatus(self._Id, byref(status))
		self._handle_ret('AioGetAoStatus', RET)
		return status.value
		#Check that RET==0
		#If RET==7, then execute reset.
	def _set_status(self, value):
		pass #read-only
	status = property(_get_status, _set_status)
	
	def _get_repeat_count(self):
		count = c_long()
		RET = self._aio.AioGetAoRepeatCount(self._Id, byref(count))
		self._handle_ret('AioGetAoRepeatCount', RET)
		return count.value
	def _set_repeat_count(self, value):
		pass #Read-only
	repeat_count = property(_get_repeat_count, _set_repeat_count)
		
	#Reset
	def reset_status(self):
		RET = self._aio.AioResetAoStatus(self._Id)
		self._handle_ret('AioResetAoStatus', RET)
	def reset_memory(self):
		RET = self._aio.AioResetAoMemory(self._Id)
		self._handle_ret('AioResetAoMemory', RET)
	def reset_device(self):
		RET = self._aio.AioResetDevice(self._Id)
		self._handle_ret('AioResetDevice', RET)
		
	#Device names
	def _dev_names(self):
		devname = create_string_buffer(256)
		device = create_string_buffer(256)
		RET = self._aio.AioQueryDeviceName(c_short(0), byref(devname), byref(device))
		return devname.value
	
	#Error handler
	def _handle_ret(self, func_name, RET):
		if RET != 0:
			ErrorString = create_string_buffer(256)
			Ret2 = self._aio.AioGetErrorString(Ret, byref(ErrorString))
			print func_name + " = %d : %s\n\n" % RET, ErrorString.value
			RET = self._aio.AioExit(self._Id)