''' Driver for PNA E8364B VNA

* Only supports a single window

Manual: https://www.testworld.com/wp-content/uploads/user-guide-help-agilent-e8362b-e8363b-e8364b-e8361a-n5230a-n5242a-pna-series-microwave-network-analyzers.pdf
'''

import array
from heimdallr.base import *
from heimdallr.instrument_control.categories.spectrum_analyzer_ctg import *

class SiglentSSA3000X(SpectrumAnalyzerCtg):
	
	SWEEP_CONTINUOUS = "sweep-continuous"
	SWEEP_SINGLE = "sweep-single"
	SWEEP_OFF = "sweep-off"
	
	def __init__(self, address:str, log:LogPile):
		super().__init__(address, log)
		
		self.trace_lookup = {}
	
	def set_freq_start(self, f_Hz:float):
		self.write(f"SENS:FREQ:STAR {f_Hz} Hz")
	def get_freq_start(self):
		return float(self.query(f"SENS:FREQ:STAR?"))
	
	def set_freq_end(self, f_Hz:float):
		self.write(f"SENS:FREQ:STOP {f_Hz}")
	def get_freq_end(self,):
		return float(self.query(f"SENS:FREQ:STOP?"))
	
	def set_ref_level(self, ref_dBm:float):
		ref_dBm = max(-100, min(ref_dBm, 30))
		if ref_dBm != ref_dBm:
			self.log.error(f"Did not apply command. Instrument limits values from -100 to 30 dBm and this range was violated.")
			return
		self.write(f"DISP:WIND:TRAC:Y:RLEV {ref_dBm} DBM")
	def get_ref_level(self):
		return float(self.query("DISP:WIND:TRAC:Y:RLEV?"))
	
	def set_y_div(self, step_dB:float):
		
		step_dB = max(1, min(step_dB, 20))
		if step_dB != step_dB:
			self.log.error(f"Did not apply command. Instrument limits values from 1 to 20 dB and this range was violated.")
			return
		self.write(f":DISP:WIND:TRAC:Y:SCAL:PDIV {step_dB} DB")
	def get_y_div(self):
		return float(self.query(f":DISP:WIND:TRAC:Y:SCAL:PDIV?"))
	
	def set_res_bandwidth(self, rbw_Hz:float, channel:int=1):
		self.write(f"SENS:BWID:RES {rbw_Hz}")
	def get_res_bandwidth(self, channel:int=1):
		return float(self.query(f"SENS:BWID:RES?"))
	
	# def set_num_points(self, points:int, channel:int=1):
	# 	self.write(f"SENS{channel}:SWEEP:POIN {points}")
	# def get_num_points(self, channel:int=1):
	# 	return int(self.query(f"SENS{channel}:SWEEP:POIN?"))
	
	# def get_sweep_time(self):
	# 	return float(self.query(f"SENS:ACQ:TIME?"))
	
	def set_continuous_trigger(self, enable:bool):
		self.write(f"INIT:CONT {bool_to_ONFOFF(enable)}")
	def get_continuous_trigger(self):
		return str_to_bool(self.query(f"INIT:CONT?"))
	
	def send_manual_trigger(self):
		self.write(f"INIT:IMM")
	
	# def send_pause_trigger(self):
	# 	self.write(f"INIT:PAUSE")
	# def send_resume_trigger(self):
	# 	self.write(f":INIT:RESUME")
	
	# def clear_traces(self):
	# 	self.write(f"CALC:PAR:DEL:ALL")
	
	# def add_trace(self, channel:int, trace:int, measurement:str):
		
	# 	# Get measurement code
	# 	try:
	# 		meas_code = self.measurement_codes[measurement]
	# 	except:
	# 		self.log.error(f"Unrecognized measurement!")
	# 		return
		
	# 	# Check that trace doesn't already exist
	# 	if trace in self.trace_lookup.keys():
	# 		self.log.error(f"Cannot add trace. Trace number {trace} already exists.")
		
	# 	# Create name and save
	# 	trace_name = f"trace{trace}"
	# 	self.trace_lookup[trace] = trace_name
		
	# 	# Create measurement - will not display yet
	# 	self.write(f"CALC{channel}:PAR:DEF '{trace_name}', {meas_code}")
		
	# 	# Create a trace and assoc. with measurement
	# 	self.write(f"DISP:WIND:TRAC{trace}:FEED '{trace_name}'")
	
	def get_trace_data(self, trace:int, use_ascii_transfer:bool=False):
		
		# Make sure trace is in range
		count = int(max(1, min(trace, 3)))
		if count != count:
			self.log.error(f"Did not apply command. Instrument limits values to integers 1-3 and this range was violated.")
			return
		
		# Get Y-unit
		
		
		# Run ASCII transfer if requested
		if use_ascii_transfer:
			
			self.write(f"FORMAT:TRACE:DATA ASCII") # Set format to ASCII
			data_raw = self.query(f"TRACE:DATA? {trace}") # Get raw data
			str_list = data_raw.split(",") # Split at each comma
			del str_list[-1] # Remove last element (newline)
			float_data = [float(x) for x in str_list] # Convert to float
			
		else:
		
			# Set data format - Real 64 binary data - in current Y unit
			self.write(f"FORMAT:TRACE:DATA REAL")
			
			# Read data - ask for data
			self.write(f"TRACE:DATA? {trace}")
			data_raw = []
			while True:
				try:
					byte = self.inst.read_bytes(1)
					data_raw.append(byte)
				except:
					break
			data_raw = data_raw[0]
			
			# Skip first 4 bytes (number of elements) and last byte (newline)
			float_data = list(array.array('f', data_raw[4:-1]))
		
		
		# Convert Y-unit to dBm
		return float_data
		
		trace_name = self.trace_lookup[trace]
		
		# Select the specified measurement/trace
		self.write(f"CALC{channel}:PAR:SEL {trace_name}")
		
		# Set data format
		self.write(f"FORM:DATA REAL,64")
		
		# Query data
		return self.query(f"CALC{channel}:DATA? SDATA")
		
	
		
	# def set_averaging_enable(self, enable:bool, channel:int=1):
	# 	self.write(f"SENS{channel}:AVER {bool_to_ONFOFF(enable)}")
	# def get_averaging_enable(self, channel:int=1):
	# 	return str_to_bool(self.write(f"SENS{channel}:AVER?"))
	
	# def set_averaging_count(self, count:int, channel:int=1):
	# 	count = int(max(1, min(count, 65536)))
	# 	if count != count:
	# 		self.log.error(f"Did not apply command. Instrument limits values to integers 1-65536 and this range was violated.")
	# 		return
	# 	self.write(f"SENS{channel}:AVER:COUN {count}")
	# def get_averaging_count(self, channel:int=1):
	# 	return int(self.query(f"SENS{channel}:AVER:COUN?"))
	
	# def send_clear_averaging(self, channel:int=1):
	# 	self.write(f"SENS{channel}:AVER:CLE")
	
	# def send_preset(self):
	# 	self.write("SYST:PRES")