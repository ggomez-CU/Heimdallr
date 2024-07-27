from heimdallr.all import *
from heimdallr.networking.network import *

ip_address = "localhost"
	
log = LogPile()
# log.str_format.show_detail = args.detail

# Create client agent
ca = HeimdallrClientAgent(log)
ca.set_addr(ip_address, 5555)
ca.connect_socket()

# login to server with default admin password
ca.login("admin", "password")
ca.register_client_id("terminal_main")

# Create client options
copt = ClientOptions()

ca.get_network_instrument_list(print_ids=True)

# Create remote instruments from address
# rem_osc1 = RemoteInstrument(ca, log, remote_address="192.168.1.117|TCPIP0::192.168.1.20::INSTR")
rem_osc1 = RemoteOscilloscopeCtg1(ca, log, remote_id="Scope1")

# rem_osc1.locate_instrument(rem_osc1)

if rem_osc1.connected:
	log.info(f"Successfully connected rem_osc1 to remote instrument!")
	print(f"IDN provided by network server:")
	print(f"{Fore.YELLOW}{rem_osc1.id}{Style.RESET_ALL}")
else:
	log.error(f"Failed to connect rem_osc1 to remote instrument!")

# while True:
	
# 	print(f"{Fore.GREEN}Remote Call:{Style.RESET_ALL}")
# 	a = input(f"{Fore.CYAN}\tFunction: {Style.RESET_ALL}")
# 	a = input(f"{Fore.YELLOW}\t(kw)arg (help for help): {Style.RESET_ALL}")
	
# 	rem_osc1.remote_call("set_div_volt", 1, 1)
	
	