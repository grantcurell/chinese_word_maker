
from PyQt4 import QtCore, QtGui
from tarjetaui.tarjeta_ui import Ui_tarjeta_ui
import sys


#class Ui_tarjeta_ui(Ui_tarjeta_ui):




app = QtGui.QApplication(sys.argv)
tarjeta_ui = QtGui.QWidget()
ui = Ui_tarjeta_ui()
ui.setupUi(tarjeta_ui)
tarjeta_ui.show()
sys.exit(app.exec_())
