from heimdallr.base import *
from heimdallr.instrument_control.categories.vector_network_analyzer_ctg import *

class KeysightPNAE8364B(VectorNetworkAnalyzerCtg):
	
	SWEEP_CONTINUOUS = "sweep-continuous"
	SWEEP_SINGLE = "sweep-single"
	SWEEP_OFF = "sweep-off"
	
	def __init__(self):
		pass
	
	def set_freq_start(self, f_Hz:float, channel:int=1):
		self.write(f"SENS{channel}:FREQ:STAR {f_Hz}")
	def get_freq_start(self, channel:int=1):
		return self.query(f"SENS{channel}:FREQ:STAR?")
	
	def set_freq_end(self, f_Hz:float, channel:int=1):
		self.write(f"SENS{channel}:FREQ:STOP {f_Hz}")
	def get_freq_end(self, channel:int=1):
		return self.query(f"SENS{channel}:FREQ:STOP?")
	
	def set_power(self, p_dBm:float, channel:int=1, port:int=1):
		self.write(f"SOUR{channel}:POW{port}:LEV:IMM:AMPL {p_dBm}")
	def get_power(self, channel:int=1, port:int=1):
		return self.query(f"SOUR{channel}:POW{port}:LEV:IMM:AMPL?")
	
	def set_num_points(self, points:int, channel:int=1):
		self.write(f"SENS{channel}:SWEEP:POIN {points}")
	def get_num_points(self, channel:int=1):
		return self.query(f"SENS{channel}:SWEEP:POIN?")
	
	def set_res_bandwidth(self, rbw_Hz:float, channel:int=1):
		self.write(f"SENS{channel}:BAND:RES {rbw_Hz}")
	def get_res_bandwidth(self, channel:int=1):
		return self.query(f"SENS{channel}:BAND:RES?")
	
	def set_rf_enable(self, enable:bool):
		self.write(f"OUTP:STAT {bool_to_ONFOFF(enable)}")
	def get_rf_enable(self):
		return self.query(f"OUTP:STAT?")
	
	def clear_traces(self):
		pass
	
	def add_trace(self, channel:int, measurement:str):
		pass
	
	def get_trace_data(self, channel:int):
		pass
		
	def set_sweep(self, sweep):
		pass