from heimdallr.base import *

class OscilloscopeCtg0(Driver):
	
	def __init__(self, address:str, log:LogPile, expected_idn="", **kwargs):
		super().__init__(address, log, expected_idn=expected_idn, **kwargs)

class OscilloscopeCtg1(OscilloscopeCtg0):
	
	def __init__(self, address:str, log:LogPile, expected_idn="", **kwargs):
		super().__init__(address, log, expected_idn=expected_idn, **kwargs)
	
	@abstractmethod
	def set_div_time(self, time_s:float):
		pass
	
	@abstractmethod
	def get_div_time(self, channel:int):
		pass
	
	@abstractmethod
	def set_offset_time(self, channel:int, time_s:float):
		pass
	
	@abstractmethod
	def set_div_volt(self, channel:int, volt_V:float):
		pass
	
	@abstractmethod
	def set_offset_volt(self, channel:int, volt_V:float):
		pass
	
	@abstractmethod
	def set_chan_enable(self, channel:int, enable:bool):
		pass
	
	@abstractmethod
	def get_waveform(self, channel:int):
		pass

class OscilloscopeCtg2(OscilloscopeCtg1):
	
	# Measurement options
	MEAS_VMAX = 0
	MEAS_VMIN = 1
	MEAS_VAVG = 2
	MEAS_VPP  = 3
	MEAS_FREQ = 4
	
	# Statistics options for measurement options
	STAT_NONE = 0
	STAT_AVG = 1
	STAT_MAX = 2
	STAT_MIN = 3
	STAT_CURR = 4
	STAT_STD = 5
	
	def __init__(self, address:str, log:LogPile, expected_idn="", **kwargs):
		super().__init__(address, log, expected_idn=expected_idn, **kwargs)
	
	@abstractmethod
	def add_measurement(self):
		pass
	
	@abstractmethod
	def get_measurement(self):
		pass