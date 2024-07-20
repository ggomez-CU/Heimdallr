from heimdallr.all import *
from heimdallr.networking.network import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--local', help="Use localhost instead of intranet address.", action='store_true')
args = parser.parse_args()

# Create socket - this is not protected by a mutex and should only ever be used by the main thread
if args.local:
	ip_address = "localhost"
else:
	ip_address = "192.168.1.116"

if __name__ == '__main__':
	
	log = LogPile()
	
	# Create client agent
	ca = ClientAgent(log)
	ca.set_addr(ip_address, 5555)
	ca.connect_socket()
	
	# Create client options
	copt = ClientOptions()
	
	# Create remote instruments from address
	rem_osc1 = RemoteInstrument(ca, remote_inst_address="192.168.0.14|TCPIP0::192.168.2.11::INSTR")
	
	# TODO: Change current register_instrument to something like find instrument
	# TODO: Make register_instrument accept an Instrument object
	rem_osc1.locate_instrument(rem_osc1)
	
	#TODO: Do things with rem_osc1 like set the voltage or whatever