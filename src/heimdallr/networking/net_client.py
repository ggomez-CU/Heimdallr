import socket
import rsa
import tabulate
import threading
import hashlib
import sqlite3
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from pylogfile import *
from heimdallr.networking.network import *

# Initialize database access
db_mutex = threading.Lock() # Create a mutex for the database

ENC_FALSE = 100
ENC_AUTO = 101
ENC_TRUE = 102

