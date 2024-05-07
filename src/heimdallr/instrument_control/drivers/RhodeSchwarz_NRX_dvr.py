''' Driver for Rhode & Schwarz NRX Power Meter 

Manual: https://scdn.rohde-schwarz.com/ur/pws/dl_downloads/pdm/cl_manuals/user_manual/1178_5566_01/NRX_UserManual_en_10.pdf
'''

import array
from heimdallr.base import *
from heimdallr.instrument_control.categories.spectrum_analyzer_ctg import *

class RhodeSchwarzNRX(SpectrumAnalyzerCtg):
	
	def __init__(self, address:str, log:LogPile):
		super().__init__(address, log, expected_idn="Siglent Technologies,SSA30")
		
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
	
	def set_continuous_trigger(self, enable:bool):
		self.write(f"INIT:CONT {bool_to_ONFOFF(enable)}")
	def get_continuous_trigger(self):
		return str_to_bool(self.query(f"INIT:CONT?"))
	
	def send_manual_trigger(self):
		self.write(f"INIT:IMM")
	
# # Measure Output Attenuation
# # Using SMW and Power Sensor
# def NRX_connect():

#     import pyvisa
#     rm=pyvisa.ResourceManager()
#     NRX = rm.open_resource('TCPIP::192.168.0.10::INSTR')
#     NRX.query('*idn?')
#     NRX.write('*RST') # reset ZNA
#     return NRX


# # -----------------------
# # ---- Commands ---------
# # -----------------------
# # NRX = NRX_connect()
# # NRX.write(f"SENSe:FREQuency:CW {tmpFreq}") 


# # Read power from NRX power meter
# import time

# def readPower_NRX(NRX):
#     try:
#         NRX.write(":SENSe:POWer:RANGE:AUTO ON")
#         NRX.write(":SENSe:AVERage:COUNt 10")  # Set averaging count to 10
#         NRX.write(":INITiate:CONTinuous ON")  # Continuous measurement mode
#         NRX.write(f":INITiate:IMMediate") # Read marker value
#         time.sleep(20)
#         measVal = float(NRX.query(f'FETCH?'))
#         #print(f'power = {measVal} dBm')
#         return measVal # return marker value
#     except:
#          print("Error: reading power")



