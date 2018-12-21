## Deamon that compile GraphViz script into image and display it automatically when the script file is modified
# @author David Dorchies
# @date 07/07/2016

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QToolTip, QPushButton)
from PyQt5.QtGui import QFont
from interface import Example
import os
import sys


## Read a section in an .ini file and return a dictionnary
#  @param sIniFile Path to the .ini file to read
#  @param sSection Section name to read in the .ini file
#  @return Dictionnary of strings made from couples (key, value)
def GetItemsIniFile(sIniFile, sSection):
    import configparser as cp
    CfgPrm = cp.ConfigParser()
    CfgPrm.read(sIniFile)
    # initialisation de dPrm : dictionnaire des paramètres généraux de la compilation
    dPrm = {}
    if not CfgPrm.has_section(sSection):
        return {}
    for item in CfgPrm.items(sSection):
        dPrm[item[0]] = item[1]
    return dPrm


## Class that add the daemon to the QLabel object


class myLabel(QtWidgets.QLabel):

    def __init__(self, parent=None):
        super(myLabel, self).__init__(parent)
        # Load parameters in dotd.ini
        self.secondWin = None
        self.dDOT = GetItemsIniFile("dotd.ini", "DOT")
        self.mTime = 0  # Last modified file time

    ## Daemon that run the GraphViz dot tool and display the image in a QLabel window
    def daemon(self):
        from subprocess import call
        from PyQt5 import QtGui
        import datetime
        from buildgraph import update_graphic

        dot = "pydot.dot"

        QToolTip.setFont(QFont('SansSerif', 10))

        self.setToolTip('This is a <b>QWidget</b> widget')

        btn = QPushButton('Button', self)
        btn.setToolTip('This is a <b>QPushButton</b> widget')
        btn.resize(btn.sizeHint())
        btn.move(0, 0)
        btn.clicked.connect(self.openWin)
        """
        btn_start = QPushButton('Старт', self)
        btn_start.resize(btn_start.sizeHint())
        btn_start.move(70, 0)
        btn_start.clicked.connect(update_graphic)
        """
        if self.mTime != os.path.getmtime(dot):
            # Run DOT     
            tRunDOT = "{0} -T{1} \"{2}\" -o \"{2}.{1}\"".format(self.dDOT["exe"], self.dDOT["format"], dot)
            call(tRunDOT)
            self.setWindowTitle("GraphViz {}.{} {}".format(dot, self.dDOT["format"], datetime.datetime.fromtimestamp(
                os.path.getmtime(dot)).strftime('%Y-%m-%d %H:%M:%S')))
            pixmap = QtGui.QPixmap("{}.{}".format(dot, self.dDOT["format"]))
            self.setPixmap(pixmap)
            self.setStyleSheet("""background-color: #ffffff""")
            self.setFixedSize(pixmap.width(), pixmap.height() + 45)
            self.show()
            self.mTime = os.path.getmtime(dot)

    def openWin(self):
        if not self.secondWin:
            self.secondWin = Example(self)
        self.secondWin.show()


## Main program
def draw():
    from PyQt5 import QtCore
    from interface import Example
    # Define script path (Cf. http://diveintopython.adrahon.org/functional_programming/finding_the_path.html)
    sCurrentPath = os.path.abspath(os.path.dirname(sys.argv[0]))
    os.chdir(sCurrentPath)

    # Bootstraping QT GUI
    app = QtWidgets.QApplication(sys.argv)
    label = myLabel()

    # Defining loop timer for the daemon
    timer = QtCore.QTimer()
    timer.timeout.connect(label.daemon)
    dDaemon = GetItemsIniFile("dotd.ini", "DAEMON")
    timer.start(int(dDaemon["sleep"]))

    # Exit script when the window is closed
    sys.exit(app.exec_())


if __name__ == '__main__':
    draw()
