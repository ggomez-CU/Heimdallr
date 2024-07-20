''' Minimum example for setting up a server using Heimdallr.
'''

from pyfrost.pf_server import *
from pylogfile.base import *
import argparse
from heimdallr.base import *
from heimdallr.networking.net_server import *

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('-l', '--local', help="Use localhost instead of intranet address.", action='store_true')
args = parser.parse_args()

# Create socket - this is not protected by a mutex and should only ever be used by the main thread
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(SOCKET_TIMEOUT)
if args.local:
	sock.bind(("localhost", 5555))
else:
	sock.bind(("192.168.1.116", 5555))
sock.listen()

if __name__ == "__main__":
	
	# Run server main loop
	server_main(sock, query_func=server_callback_query, send_func=server_callback_send)