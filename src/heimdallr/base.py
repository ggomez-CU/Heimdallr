import pyvisa as pv
from pylogfile import *
import numpy as np
import time
import inspect
from abc import ABC, abstractmethod
from socket import getaddrinfo, gethostname
import ipaddress
import fnmatch

def get_ip(ip_addr_proto="ipv4", ignore_local_ips=True):
	# By default, this method only returns non-local IPv4 addresses
	# To return IPv6 only, call get_ip('ipv6')
	# To return both IPv4 and IPv6, call get_ip('both')
	# To return local IPs, call get_ip(None, False)
	# Can combine options like so get_ip('both', False)
	#
	# Thanks 'Geruta' from Stack Overflow: https://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-from-a-nic-network-interface-controller-in-python

	af_inet = 2
	if ip_addr_proto == "ipv6":
		af_inet = 30
	elif ip_addr_proto == "both":
		af_inet = 0

	system_ip_list = getaddrinfo(gethostname(), None, af_inet, 1, 0)
	ip_list = []

	for ip in system_ip_list:
		ip = ip[4][0]

		try:
			ipaddress.ip_address(str(ip))
			ip_address_valid = True
		except ValueError:
			ip_address_valid = False
		else:
			if ipaddress.ip_address(ip).is_loopback and ignore_local_ips or ipaddress.ip_address(ip).is_link_local and ignore_local_ips:
				pass
			elif ip_address_valid:
				ip_list.append(ip)

	return ip_list

def wildcard(test:str, pattern:str):
	return len(fnmatch.filter([test], pattern)) > 0

class HostID:
	''' Contains the IP address and host-name for the host. Primarily used
	so drivers can quickly identify the host's IP address.'''
	
	def __init__(self, target_ip:str="192.168.1.*"):
		''' Identifies the ipv4 address and host-name of the host.'''
		self.ip_address = ""
		self.host_name = ""
		
		# Get list of IP address for each network adapter
		ip_list = get_ip()
		
		# Scan over list and check each
		for ipl in ip_list:
			
			# Check for match
			if wildcard(ipl, target_ip):
				self.ip_address = ipl
		
		self.host_name = gethostname()

class Identifier:
	
	def __init__(self):
		self.idn_model = "" # Identifier provided by instrument itself (*IDN?)
		self.ctg = "" # Category class of driver
		self.dvr = "" # Driver class
		
		self.remote_id = "" # Rich name authenticated by the server and used to lookup the remote address
		self.remote_addr = ("", "") # Tuple of IP address of driver host, then instrument VISA address.
		
	def __str__(self):
		
		# Get remote address length
		ra_str = self.remote_addr[0] + "|" + self.remote_addr[1]
		if len(ra_str) < 3:
			ra_str = "?"
		
		return f"idn_model: {self.idn_model}\ncategory: {self.ctg}\ndriver-class: {self.dvr}\nremote-id: {self.remote_id}\nremote-addr: {ra_str}"
	
class DriverManager:
	''' Accepts a number of driver instances and allows them to be interacted with
	over a network.
	'''
	
	def __init__(self):
		self.drivers = []
	
	def route_command(self, remote_id:str, command:str):
		''' Accepts a command and remote-id and '''
		pass
		
		#TODO: Find if remote_id is in driver list, and route command
		
	
class ClientAgent:
	
	def __init__(self):
		pass

class RemoteInstrument:
	''' Class to represent an instrument driven by another host on this network. This
	class allows remote clients to control the instrument, despite not having a 
	connection or driver locally.
	'''
	
	def __init__(self, ca:ClientAgent, remote_id:str=None, remote_address:str=None):
		
		# Save values
		self.remote_id = remote_id
		self.remote_address = remote_address
		self.client_agent = None
		
		# Register with server - this will populate
		self.register_instrument(remote_id=self.remote_id, remote_address=self.remote_address)
	
	def register_instrument(remote_id:str=None, remote_address:str=None):
		pass
	
		#TODO:  Ask server for instrument info
		
		#TODO: Update id and address
		# self.remote_id = 
		# self.remote_address = 
	
	def remote_call(self, func_name:str, *args, **kwargs):
		''' Calls the function 'func_name' of a remote instrument '''
		
		arg_str = ""
		for a in args:
			arg_str = arg_str + f"{a} "
		for key, value in kwargs.items():
			arg_str = arg_str + f"{key}:{value} "
		
		print(f"Initializing remote call: function = {func_name}, arguments = {arg_str} ")

def RemoteFunction(func):
	'''Decorator to allow empty functions to call
	their remote counterparts'''
	
	def wrapper(self, *args, **kwargs):
		self.remote_call(func.__name__, *args, **kwargs)
		func(self, *args, **kwargs)
	return wrapper

#TODO: Move this to the Ctg file. This style of class is recommended but not required. Can use REmoteInstrument for everything if you prefer.
class SpectrumAnalyzerRemote(RemoteInstrument):
	
	def __init__(self):
		super().__init__()
	
	# Without the decorator, it looks like this
	def set_freq_start(self, f_Hz:float, channel:int=1):
		self.remote_call('set_freq_start', f_Hz, channel)
	
	# With the decorator, it looks like this
	@RemoteFunction
	def set_freq_end(self, f_Hz:float, channel:int=1):
		pass

class Driver(ABC):
	
	#TODO: Modify all category and drivers to pass kwargs to super
	def __init__(self, address:str, log:LogPile, expected_idn:str="", is_scpi:bool=True, remote_id:str=None, host_id:HostID=None):
		
		self.address = address
		self.log = log
		self.is_scpi = is_scpi
		
		self.id = Identifier()
		self.expected_idn = expected_idn
		self.verified_hardware = False
		
		self.online = False
		self.rm = pv.ResourceManager()
		self.isnt = None
		
		# Populate id
		if host_id is not None:
			self.id.remote_addr = (host_id.ip_address, self.address)
		if remote_id is not None:
			self.id.remote_id = remote_id
			
		# Get category
		inheritance_list = inspect.getmro(self.__class__)
		dvr_o = inheritance_list[0]
		ctg_o = inheritance_list[1]
		self.id.ctg = f"{ctg_o}"
		self.id.dvr = f"{dvr_o}"
		
		#TODO: Automatically reconnect
		# Connect instrument
		self.connect()
	
	def connect(self, check_id:bool=True):
		
		# Abort if not an SCPI instrument
		if not self.is_scpi:
			self.log.error(f"Cannot use default connect() function, instrument does recognize SCPI commands.")
			return
		
		# Attempt to connect
		try:
			self.inst = self.rm.open_resource(self.address)
			self.online = True
			
			if check_id:
				self.query_id()
			
		except Exception as e:
			self.log.error(f"Failed to connect to address: {self.address}. ({e})")
			self.online = False
	
	def preset(self):
		
		# Abort if not an SCPI instrument
		if not self.is_scpi:
			self.log.error(f"Cannot use default preset() function, instrument does recognize SCPI commands.")
			return
		
		self.write("*RST")
	
	def query_id(self):
		''' Checks the IDN of the instrument, and makes sure it matches up.'''
		
		# Abort if not an SCPI instrument
		if not self.is_scpi:
			self.log.error(f"Cannot use default query_id() function, instrument does recognize SCPI commands.")
			return
		
		# Query IDN model
		self.id.idn_model = self.query("*IDN?").strip()
		
		if self.id.idn_model is not None:
			self.online = True
			self.log.debug(f"Instrument connection state: >ONLINE<")
			
			if self.expected_idn is None or self.expected_idn == "":
				self.log.debug("Cannot verify hardware. No verification string provided.")
				return
			
			# Check if model is right
			if self.expected_idn.upper() in self.id.idn_model.upper():
				self.verified_hardware = True
				self.log.debug(f"Hardware verification >PASSED<", detail=f"Received string: {self.id.idn_model}")
			else:
				self.verified_hardware = False
				self.log.debug(f"Hardware verification >FAILED<", detail=f"Received string: {self.id.idn_model}")
		else:
			self.log.debug(f"Instrument connection state: >OFFLINE<")
			self.online = False
		
	def close(self):
		
		# Abort if not an SCPI instrument
		if not self.is_scpi:
			self.log.error(f"Cannot use default close() function, instrument does recognize SCPI commands.")
			return
		
		self.inst.close()
	
	def wait_ready(self, check_period:float=0.1, timeout_s:float=None):
		''' Waits until all previous SCPI commands have completed. *CLS 
		must have been sent prior to the commands in question.
		
		Set timeout to None for no timeout.
		
		Returns true if operation completed, returns False if timeout occured.'''
		
		# Abort if not an SCPI instrument
		if not self.is_scpi:
			self.log.error(f"Cannot use default wait_ready() function, instrument does recognize SCPI commands.")
			return
		
		self.write(f"*OPC")
		
		# Check ESR
		esr_buffer = int(self.query(f"*ESR?"))
		
		t0 = time.time()
		
		# Loop while ESR bit one is not set
		while esr_buffer == 0:
			
			# Check register state
			esr_buffer = int(self.query(f"*ESR?"))
			
			# Wait prescribed time
			time.sleep(check_period)
			
			# Timeout handling
			if (timeout_s is not None) and (time.time() - t0 >= timeout_s):
				break
		
		# Return
		if esr_buffer > 0:
			return True
		else:
			return False
		
	def write(self, cmd:str):
		''' Sends a SCPI command via PyVISA'''
		
		# Abort if not an SCPI instrument
		if not self.is_scpi:
			self.log.error(f"Cannot use default write() function, instrument does recognize SCPI commands.")
			return
		
		if not self.online:
			self.log.warning(f"Cannot write when offline. ()")
			return
			
		try:
			self.inst.write(cmd)
		except Exception as e:
			self.log.error(f"Failed to write to instrument {self.address}. ({e})")
			self.online = False
		
	def id_str(self):
		pass
	
	def read(self):
		''' Reads via PyVISA'''
		
		# Abort if not an SCPI instrument
		if not self.is_scpi:
			self.log.error(f"Cannot use default read() function, instrument does recognize SCPI commands.")
			return
		
		if not self.online:
			self.log.warning(f"Cannot write when offline. ()")
		
		try:
			return self.inst.write()
		except Exception as e:
			self.log.error(f"Failed to read from instrument {self.address}. ({e})")
			self.online = False
			return None
	
	def query(self, cmd:str):
		''' Querys a command via PyVISA'''
		
		# Abort if not an SCPI instrument
		if not self.is_scpi:
			self.log.error(f"Cannot use default query() function, instrument does recognize SCPI commands.")
			return
		
		if not self.online:
			self.log.warning(f"Cannot write when offline. ()")
		
		try:
			return self.inst.query(cmd)
		except Exception as e:
			self.log.error(f"Failed to query instrument {self.address}. ({e})")
			self.online = False
			return None

def bool_to_str01(val:bool):
	''' Converts a boolean value to 0/1 as a string '''
	
	if val:
		return "1"
	else:
		return "0"

def str01_to_bool(val:str):
	''' Converts the string 0/1 to a boolean '''
	
	if '1' in val:
		return True
	else:
		return False

def bool_to_ONFOFF(val:bool):
	''' Converts a boolean value to 0/1 as a string '''
	
	if val:
		return "ON"
	else:
		return "OFF"

def str_to_bool(val:str):
	''' Converts the string 0/1 or ON/OFF or TRUE/FALSE to a boolean '''
	
	if ('1' in val) or ('ON' in val.upper()) or ('TRUE' in val.upper()):
		return True
	else:
		return False

def s2hms(seconds):
	''' Converts a value in seconds to a tuple of hours, minutes, seconds.'''
	
	# Convert seconds to minutes
	min = np.floor(seconds/60)
	seconds -= min*60
	
	# Convert minutes to hours
	hours = np.floor(min/60)
	min -= hours*60
	
	return (hours, min, seconds)


def interpret_range(rd:dict, print_err=False):
	''' Accepts a dictionary defining a sweep list/range, and returns a list of the values. Returns none
	if the format is invalid.
	
	* Dictionary must contain key 'type' specifying the string 'list' or 'range'.
	* Dictionary must contain a key 'unit' specifying a string with the unit.
	* If type=list, dictionary must contain key 'values' with a list of each value to include.
	* If type=range, dictionary must contain keys start, end, and step each with a float value
	  specifying the iteration conditions for the list.
	
	Example list dict (in JSON format):
		 {
			"type": "list",
			"unit": "dBm",
			"values": [0]
		}
		
	Example range dict (in JSON format):
		{
			"type": "range",
			"unit": "Hz",
			"start": 9.8e9,
			"step": 1e6,
			"end": 10.2e9
		}
	
	'''
	K = rd.keys()
	
	# Verify type parameter
	if "type" not in K:
		if print_err:
			print(f"    {Fore.RED}Key 'type' not present.{Style.RESET_ALL}")
		return None
	elif type(rd['type']) != str:
			if print_err:
				print(f"    {Fore.RED}Key 'type' wrong type.{Style.RESET_ALL}")
			return None
	elif rd['type'] not in ("list", "range"):
		if print_err:
			print(f"    {Fore.RED}Key 'type' corrupt.{Style.RESET_ALL}")
		return None
	
	# Verify unit parameter
	if "unit" not in K:
		if print_err:
			print(f"    {Fore.RED}Key 'unit' not present.{Style.RESET_ALL}")
		return None
	elif type(rd['unit']) != str:
		if print_err:
			print(f"    {Fore.RED}Key 'unit' wrong type.{Style.RESET_ALL}")
		return None
	elif rd['unit'] not in ("dBm", "V", "Hz", "mA"):
		if print_err:
			print(f"    {Fore.RED}Key 'unit' corrupt.{Style.RESET_ALL}")
		return None
	
	# Read list type
	if rd['type'] == 'list':
		try:
			vals = rd['values']
		except:
			if print_err:
				print(f"    {Fore.RED}Failed to read value list.{Style.RESET_ALL}")
			return None
	elif rd['type'] == 'range':
		try:
			
			start = int(rd['start']*1e6)
			end = int(rd['end']*1e6)+1
			step = int(rd['step']*1e6)
			
			vals = np.array(range(start, end, step))/1e6
			
			vals = list(vals)
			
		except Exception as e:
			if print_err:
				print(f"    {Fore.RED}Failed to process sweep values. ({e}){Style.RESET_ALL}")
			return None
	
	return vals