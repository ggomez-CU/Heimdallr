from heimdallr.base import *
from heimdallr.networking.net_client import *

from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QMainWindow, QGridLayout, QPushButton, QSlider, QGroupBox, QWidget, QTabWidget

class HeimdallrWindow(QMainWindow):
	
	def __init__(self, log:LogPile):
		
		self.log = log
		
		grid = QTabWidget.QGridLayout()

class CtgWidget(QWidget):
	
	def __init__(self, inst:Driver, log:LogPile):
		
		# Local variables
		self.log = log
		self.inst = inst # This can be a local driver, or a remoteinstrument object
		
		# Automatically check if a local driver or remoteinstrument was provided
		self.is_remote = issubclass(type(self), RemoteInstrument)