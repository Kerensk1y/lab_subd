from PyQt6 import uic, QtWidgets
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtSql import *

from MainForm import *

Form, Window = uic.loadUiType("MainMenu.ui")

def data_click(self):
    return 0

def analytics_click():
    return 0

app = QApplication([])
window = Window()
form = Form()
form.setupUi(window)