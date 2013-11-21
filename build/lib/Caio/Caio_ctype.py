from ctypes import *
import numpy as np

class Caio(object):
	#Error handler
	def _handle_ret(self, func_name, RET, critical = True):
		if RET != 0:
			ErrorString = create_string_buffer(256)
			Ret2 = self._aio.AioGetErrorString(RET, byref(ErrorString))
			print '%(fname)s = %(err_num)s : %(err_str)s' %\
				{"fname": func_name, "err_num": RET, "err_str": ErrorString.value}
			if critical:
				RET = self._aio.AioExit(self._Id)
			
	def __init__(self, DeviceName=None):
		#TODO: load the library in linux? (Linux drivers exist)
		try: 
			self._aio=windll.LoadLibrary("caio.dll")
		except:
			self._aio=windll.LoadLibrary("caio32.dll")
		
		if DeviceName:
			self._DeviceName = create_string_buffer(DeviceName)
		
		self.DeviceName #Gets the device name
		self.Id #Initializes the device.
		
		#Reset device
		self.reset_device()
		
		#Defaults
		#range: PM10, not configurable on my device
		#n_channels: 1
		#memory_type: FIFO
		#clock_type: 'Internal' or 0
		#fs: 1000
		#start_trigger: 'Software'
		#stop_trigger: 'Times'
		self._max_channels = self.max_chans
		
		#Reset memory
		self.reset_memory()
		
		
	def __del__(self):
		self.stop()
		RET = self._aio.AioExit(self._Id)
	
	#DeviceName
	@property
	def DeviceName(self):
		if not hasattr(self, '_DeviceName') or not self._DeviceName:
			self._DeviceName = create_string_buffer(256)
			self._Device = create_string_buffer(256)
			RET = self._aio.AioQueryDeviceName( c_short(0), byref(self._DeviceName), byref(self._Device) )
			self._handle_ret('AioQueryDeviceName', RET)
		return self._DeviceName.value
	@DeviceName.setter
	def DeviceName(self, value):
		pass #Not settable
		
	#Device or BoardName
	@property
	def Device(self):
		if self.DeviceName and (not hasattr(self, '_Device') or not self._Device):
			#We have a _DeviceName but not a _Device
			DeviceName = create_string_buffer(256)
			self._Device = create_string_buffer(256)
			ix = -1
			while DeviceName.value != self.DeviceName:
				ix += 1
				RET = self._aio.AioQueryDeviceName( c_short(ix), byref(DeviceName), byref(self._Device) )
				self._handle_ret('AioQueryDeviceName', RET, critical = False)
		return self._Device.value
	@Device.setter
	def Device(self, value):
		pass #Not settable.

	#DeviceType
	@property
	def DeviceType(self):
		if not hasattr(self, '_DeviceType') or not self._DeviceType:
			self._DeviceType = c_short()
			RET = self._aio.AioGetDeviceType( byref(self._Device), byref(self._DeviceType) )
			self._handle_ret('AioGetDeviceType', RET)
		return self._DeviceType.value
	@DeviceType.setter
	def DeviceType(self, value):
		pass #Not settable.

	#Id
	@property
	def Id(self):
		if not hasattr(self, '_Id') or not self._Id:
			self._Id = c_short()
			RET = self._aio.AioInit( self._DeviceName, byref(self._Id) )
			self._handle_ret('AioInit', RET)
		return self._Id.value

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

	#Resolution
	@property
	def n_bits(self):
		resolution = c_short()
		RET = self._aio.AioGetAoResolution( self._Id, byref(resolution) )
		self._handle_ret('AioGetAoResolution', RET)
		return resolution.value
	@n_bits.setter
	def n_bits(self, value):
		pass #read-only

	#Channel
	#setaochannels, getaochannels, getaomaxchannels
	@property
	def max_chans(self):
		maxchans = c_short()
		RET = self._aio.AioGetAoMaxChannels(self._Id, byref(maxchans))
		self._handle_ret('AioGetAoMaxChannels', RET)
		return maxchans.value
	@max_chans.setter
	def max_chans(self, value):
		pass #read-only

	@property
	def n_channels(self):
		nchannels = c_short()
		RET = self._aio.AioGetAoChannels(self._Id, byref(nchannels))
		self._handle_ret('AioGetAoChannels', RET)
		return nchannels.value
	@n_channels.setter
	def n_channels(self, value):
		nchannels = c_short(np.min((value,self.max_chans)))
		RET = self._aio.AioSetAoChannels(self._Id, nchannels)
		self._handle_ret('AioSetAoChannels', RET)

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
	@property
	def memory_type(self):#proxy for AioGetMemoryType
		mem_type=c_short()
		RET=self._aio.AioGetAoMemoryType(self._Id, byref(mem_type))
		self._handle_ret('AioGetAoMemoryType', RET)
		if mem_type.value==1: return 'RING'
		elif mem_type.value==0: return 'FIFO'
	@memory_type.setter
	def memory_type(self, value='FIFO'):#proxy for AioSetAoMemoryType
		if value=='RING': mem_type=c_short(1)
		elif value=='FIFO': mem_type=c_short(0)
		RET = self._aio.AioSetAoMemoryType(self._Id, mem_type)
		self._handle_ret('AioSetAoMemoryType', RET)

	#Repeat
	@property
	def repeat_times(self):
		repeats = c_long()
		RET = self._aio.AioGetAoRepeatTimes(self._Id, byref(repeats))
		self._handle_ret('AioGetAoRepeatTimes', RET)
		return repeats.value
	@repeat_times.setter
	def repeat_times(self, value):#default is 0 = infinite
		repeats = c_long(value)
		RET = self._aio.AioSetAoRepeatTimes(self._Id, repeats)
		self._handle_ret('AioSetAoRepeatTimes', RET)

	#Clock
	@property
	def clock_type(self):
		clock_type = c_short()
		RET = self._aio.AioGetAoClockType(self._Id, byref(clock_type))
		self._handle_ret('AioGetAoClockType', RET)
		#0 = Internal, 1=External, 10=Event controller
		return {0:'Internal', 1:'External', 10:'Event controller'}.get(clock_type.value)
	@clock_type.setter
	def clock_type(self, value='Internal'):
		value = {'Internal':0, 'External':1, 'Event controller':10}.get(value)
		value = c_short(value)
		RET = self._aio.AioSetAoClockType(self._Id, value)
		self._handle_ret('AioGetAoClockType', RET)

	@property
	def fs(self):
		clock = c_float()
		RET = self._aio.AioGetAoSamplingClock(self._Id, byref(clock))
		self._handle_ret('AioGetAoSamplingClock', RET)
		return 1000000.0*(1.0/clock.value)
	@fs.setter
	def fs(self, value):
		#Passed-in value in Hz. Function wants sample duration in usec.
		#e.g. 0.2kHz = 200 samples / sec = 5000 usec per sample
		#Usable AoSamplingClock is 10 to 107374182
		clock = c_float(1000000.0/value)
		RET = self._aio.AioSetAoSamplingClock(self._Id, clock)
		self._handle_ret('AioSetAoSamplingClock', RET)

	#Setting Data
	@property
	def buffer(self):
		pass
	@buffer.setter
	def buffer(self, data):
		data=data[:,0:self._max_channels]#trim excess channels
		n_samples, n_channels=data.shape
		data=np.reshape(data,(n_samples*n_channels,))
		temp_data = (c_float*(data.shape[0]))()
		for i in range(data.shape[0]): temp_data[i]=data[i]
		RET = self._aio.AioSetAoSamplingDataEx(self._Id, c_long(n_samples), temp_data)
		self._handle_ret('AioSetAoSamplingDataEx', RET)

	@property
	def sampling_times(self):
		ao_sampling_time=c_long()
		RET = self._aio.AioGetAoSamplingTimes(self._Id, byref(ao_sampling_time))
		self._handle_ret('AioGetAoSamplingTimes', RET)
		return ao_sampling_time.value
	@sampling_times.setter
	def sampling_times(self, value):
		pass #read-only

	@property
	def sampling_count(self):
		ao_sampling_count=c_long()
		RET = self._aio.AioGetAoSamplingCount(self._Id, byref(ao_sampling_count))
		self._handle_ret('AioGetAoSamplingCount', RET)
		return ao_sampling_count.value
	@sampling_count.setter
	def sampling_count(self, value):
		pass #read-only

	#StartCondition
	@property
	def start_trigger(self):
		trigger=c_short()
		RET = self._aio.AioGetAoStartTrigger(self._Id, byref(trigger))
		self._handle_ret('AioGetAoStartTrigger', RET)
		return {0:'Software', 1:'External trigger rising edge', 2:'External trigger falling edge', 10:'Event controller output'}.get(trigger.value)
	@start_trigger.setter
	def start_trigger(self,value='Software'):
		value = {'Software':0, 'External trigger rising edge':1, 'External trigger falling edge':2, 'Event controller output':10}.get(value)
		value = c_short(value)
		RET = self._aio.AioSetAoStartTrigger(self._Id, value)
		self._handle_ret('AioSetAoStartTrigger', RET)

	#StopCondition
	@property
	def stop_trigger(self):
		trigger=c_short()
		RET = self._aio.AioGetAoStopTrigger(self._Id, byref(trigger))
		self._handle_ret('AioGetAoStopTrigger', RET)
		return {0:'Times', 1:'External trigger rising edge', 2:'External trigger falling edge', 10:'Event controller output'}.get(trigger.value)
	@stop_trigger.setter
	def stop_trigger(self,value='Times'):
		value = {'Times':0, 'External trigger rising edge':1, 'External trigger falling edge':2, 'Event controller output':10}.get(value)
		value = c_short(value)
		RET = self._aio.AioSetAoStopTrigger(self._Id, value)
		self._handle_ret('AioSetAoStopTrigger', RET)

	#Action
	def start(self):
		RET=self._aio.AioStartAo(self._Id)
		self._handle_ret('AioStartAo', RET)
		#If FIFO, this will remove data from buffer.
	def stop(self):
		RET = self._aio.AioStopAo(self._Id)
		self._handle_ret('AioStopAo', RET)

	#Status
	@property
	def status(self):# long AioGetAoStatus(short Id, long * AoStatus);
		status=c_long()
		RET = self._aio.AioGetAoStatus(self._Id, byref(status))
		self._handle_ret('AioGetAoStatus', RET)
		return status.value
		#Check that RET==0
		#If RET==7, then execute reset.
	@status.setter
	def status(self, value):
		pass #read-only

	@property
	def repeat_count(self):
		count = c_long()
		RET = self._aio.AioGetAoRepeatCount(self._Id, byref(count))
		self._handle_ret('AioGetAoRepeatCount', RET)
		return count.value
	@repeat_count.setter
	def repeat_count(self, value):
		pass #Read-only