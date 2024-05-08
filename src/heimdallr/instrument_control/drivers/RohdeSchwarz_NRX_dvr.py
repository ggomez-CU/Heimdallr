''' Driver for Rohde & Schwarz NRX Power Meter 

Manual: https://scdn.rohde-schwarz.com/ur/pws/dl_downloads/pdm/cl_manuals/user_manual/1178_5566_01/NRX_UserManual_en_10.pdf
'''

from heimdallr.base import *
from heimdallr.instrument_control.categories.spectrum_analyzer_ctg import *

class RohdeSchwarzNRX(RFPowerSensor):
	
	def __init__(self, address:str, log:LogPile):
		super().__init__(address, log, expected_idn="")
		
	def set_meas_frequency():
		pass
	
	def send_autoscale(self):
		print("Should this be send or enable? Is it one time?")
		self.write(f":SENS:POW:RANGE:AUTO ON")
	
	def set_averaging_count(self, counts:int, meas_no:int=1):
		
		step_dB = max(1, min(meas_no, 8))
		if step_dB != step_dB:
			self.log.error(f"Did not apply command. Instrument limits values from 1 to 20 dB and this range was violated.")
			return
		
		# Legacy version, works for R&S but deprecated
		#  [SENSe<Sensor>:]AVERage:COUNt[:VALue]
		
		self.write(f"CALC{meas_no}:CHAN1:AVER:COUN:VAL {counts}")
		
	def send_trigger(self):
		self.write(f":INIT:IMM")
	
	def get_measurement(self):
		
		# FRom the documentation:
		#   The FETCh? and READ? commands send without parameters have a special meaning.
		#   FETCh? returns the current measured value if it is valid. If a measured value is not yet
		#    available, processing is suspended until a valid result is available.
		return float(self.query(f"FETCH?"))


# # Measure Output Attenuation
# # Using SMW and Power Sensor
# def NRX_connect():

# 	import pyvisa
# 	rm=pyvisa.ResourceManager()
# 	NRX = rm.open_resource('TCPIP::192.168.0.10::INSTR')
# 	NRX.query('*idn?')
# 	NRX.write('*RST') # reset ZNA
# 	return NRX


# # -----------------------
# # ---- Commands ---------
# # -----------------------
# # NRX = NRX_connect()
# # NRX.write(f"SENSe:FREQuency:CW {tmpFreq}") 


# # Read power from NRX power meter
# import time

# def readPower_NRX(NRX):
# 	try:
# 		NRX.write(":SENSe:POWer:RANGE:AUTO ON")
# 		NRX.write(":SENSe:AVERage:COUNt 10")  # Set averaging count to 10
# 		NRX.write(":INITiate:CONTinuous ON")  # Continuous measurement mode
# 		NRX.write(f":INITiate:IMMediate") # Read marker value
# 		time.sleep(20)
# 		measVal = float(NRX.query(f'FETCH?'))
# 		#print(f'power = {measVal} dBm')
# 		return measVal # return marker value
# 	except:
# 		 print("Error: reading power")



