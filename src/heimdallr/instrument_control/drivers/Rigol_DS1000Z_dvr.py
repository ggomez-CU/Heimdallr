"""RIGOL’s 1000Z Series Digital Oscilloscope

https://beyondmeasure.rigoltech.com/acton/attachment/1579/f-0386/1/-/-/-/-/DS1000Z_Programming%20Guide_EN.pdf
"""

from heimdallr.instrument_control.categories.all_ctgs import *

class RigolDS1000Z(Oscilloscope2Ctg):

	def __init__(self, address:str, log:LogPile):
		super().__init__(address, log, expected_idn='RIGOL TECHNOLOGIES,DS10')
		
		self.meas_table = {Oscilloscope2Ctg.MEAS_VMAX:'VMAX', Oscilloscope2Ctg.MEAS_VMIN:'VMIN', Oscilloscope2Ctg.MEAS_VAVG:'VAVG', Oscilloscope2Ctg.MEAS_VPP:'VPP', Oscilloscope2Ctg.MEAS_FREQ:'FREQ'}
		
		self.stat_table = {Oscilloscope2Ctg.STAT_AVG:'AVER', Oscilloscope2Ctg.STAT_MAX:'MAX', Oscilloscope2Ctg.STAT_MIN:'MIN', Oscilloscope2Ctg.STAT_CURR:'CURR', Oscilloscope2Ctg.STAT_STD:'DEV'}
		
	def set_div_time(self, time_s:float):
		self.write(f":TIM:MAIN:SCAL {time_s}")
	def get_div_time(self):
		return self.query(f":TIM:MAIN:SCAL?")
	
	def set_offset_time(self, channel:int, time_s:float):
		self.write(f":TIM:MAIN:OFFS {time_s}")
	def get_offset_time(self, channel:int, time_s:float):
		return self.query(f":TIM:MAIN:OFFS?")
	
	def set_div_volt(self, channel:int, volt_V:float):
		self.write(f":CHAN{channel}:SCAL {volt_V}")
	def get_div_volt(self, channel:int, volt_V:float):
		return self.query(f":CHAN{channel}:SCAL?")
	
	def set_offset_volt(self, channel:int, volt_V:float):
		self.write(f":CHAN{channel}:OFFS {volt_V}")
	def get_offset_volt(self, channel:int, volt_V:float):
		return self.query(f":CHAN{channel}:OFFS?")
	
	def set_chan_enable(self, channel:int, enable:bool):
		self.write(f":CHAN{channel}:DISP {bool_to_str01(enable)}")
	def get_chan_enable(self, channel:int):
		val_str = self.query(f":CHAN{channel}:DISP?")
		return str01_to_bool(val_str)
	
	def get_waveform(self, channel:int):
		
		self.write(f"WAV:SOUR CHAN{channel}")  # Specify channel to read
		self.write("WAV:MODE NORM")  # Specify to read data displayed on screen
		self.write("WAV:FORM ASCII")  # Specify data format to ASCII
		data = self.query("WAV:DATA?")  # Request data
		
		if data is None:
			return {"time_s":[], "volt_V":[]}
		
		# Split string into ASCII voltage values
		volts = data[11:].split(",")
		
		volts = [float(v) for v in volts]
		
		# Get timing data
		xorigin = float(self.query("WAV:XOR?"))
		xincr = float(self.query("WAV:XINC?"))
		
		# Get time values
		t = list(xorigin + np.linspace(0, xincr * (len(volts) - 1), len(volts)))
		
		return {"time_s":t, "volt_V":volts}
	
	def add_measurement(self, meas_type:int, channel:int=1):
		
		# Find measurement string
		if meas_type not in self.meas_table:
			self.log.error(f"Cannot add measurement >{meas_type}<. Measurement not recognized.")
			return
		item_str = self.meas_table[meas_type]
		
		# Get channel string
		channel = max(1, min(channel, 1000))
		if channel != channel:
			self.log.error("Channel must be between 1 and 4.")
			return
		src_str = f"CHAN{channel}"
		
		# Send message
		self.write(f":MEASURE:ITEM {item_str},{src_str}")
	
	def get_measurement(self, meas_type:int, channel:int=1, stat_mode:int=0) -> float:
		
		# FInd measurement string
		if meas_type not in self.meas_table:
			self.log.error(f"Cannot add measurement >{meas_type}<. Measurement not recognized.")
			return
		item_str = self.meas_table[meas_type]
		
		# Get channel string
		channel = max(1, min(channel, 1000))
		if channel != channel:
			self.log.error("Channel must be between 1 and 4.")
			return
		src_str = f"CHAN{channel}"
		
		
		
		# Query result
		if stat_mode == 0:
			return self.query(f":MEASURE:ITEM? {item_str},{src_str}")
		else:
			
			# Get stat string
			if stat_mode not in self.stat_table:
				self.log.error(f"Cannot use statistic option >{meas_type}<. Option not recognized.")
				return
			stat_str = self.stat_table[stat_mode]
			
			return self.query(f":MEASURE:STAT:ITEM? {stat_str},{item_str},{src_str}")
	
	def clear_measurements(self):
		
		self.write(f":MEASURE:CLEAR ALL")
	
	def set_measurement_stat_display(self, enable:bool):
		'''
		Turns display statistical values on/off for the Rigol DS1000Z series scopes. Not
		part of the OscilloscopeCtg, but local to this driver.
		
		Args:
			enable (bool): Turns displayed stats on/off
		
		Returns:
			None
		'''
		
		self.write(f":MEASure:STATistic:DISPlay {bool_to_ONFOFF(enable)}")