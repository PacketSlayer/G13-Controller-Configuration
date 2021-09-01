#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QSize, QRect
from PyQt5.QtCore import QCoreApplication, QMetaObject, QThread
from PyQt5.QtGui import  QFont, QColor
from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication, QSizePolicy
from PyQt5.QtWidgets import QWidget, QPushButton, QTextEdit, QFrame, QColorDialog
from PyQt5.QtWidgets import QMessageBox
from pynput.keyboard import Key, Listener, Controller
import os
from pathlib import Path

#==========================================  EVENTS  ===============================================

class Ui_Configuration(object):
    def __init__(self):
        self.GKEY = {}
        self.KEYBIND = {}
        self.KEYACTION = {}
        self.SELKEY = ""
        self.FILE = str(Path.home()) + "/.g13/key.bind"
        self.r = 0
        self.g = 0
        self.b = 0
        self.rgb="FFFFFF"
        self.c = "999999"
        self.setupUi(self)

    def EVENT_GKEY_CLICK(self):
        if self.SELKEY == "":
            self.CLEAR.show()
            sender = self.sender()
            sendername = sender.objectName()
            for key, control in self.GKEY.items():
                if len(self.KEYBIND[key]) > 0:
                    self.setforegroundcolor()
                    control.setStyleSheet(f"QPushButton{{background:#111111; "\
                            f"color:#{self.rgb}; border-radius: 4px}}")
                else:
                    control.setStyleSheet("QPushButton{background:#111111; "\
                            "color:white; border-radius: 4px}")
            sender.setStyleSheet(f"QPushButton{{background: #{self.rgb}; "\
                    f"color:#101010; border-radius: 4px}}")
            self.SELKEY = sendername
            self.labelStatus.setText(self.translate("MainWindow", f"Press a key"\
                     f" to map to {sendername} *OR* click {sendername} "\
                     f"again to cancel"))
        else:
            self.SELKEY = ""
            self.resetkeystyle()

    def EVENT_CLEAR_CLICK(self):
        if self.SELKEY != "":
            self.bindkey(self.SELKEY,"")
            self.resetkeystyle()
            self.pushconfig()

    def EVENT_CLEARALL_CLICK(self):
        buttonReply = QMessageBox.question(self, 'G13 Config', "Do you want to "\
                "reset all buttons?", QMessageBox.No | QMessageBox.Yes, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            for key, control in self.GKEY.items():
                sendername = control.objectName()
                self.bindkey(key,"")
            self.resetkeystyle()
            self.pushconfig()
        else:
            pass

    def EVENT_PICKCOLOR_CLICK(self):
        color = QColorDialog.getColor()
        if QColor.isValid(color):
            self.LCD.setStyleSheet(f"QTextEdit{{background:{str(color.name())}; "\
                    f"color:{str(color.name())};}}")
            color = self.hex_to_rgb(color.name())
            self.r = color[0]
            self.g = color[1]
            self.b = color[2]
            self.LCDchange(self.r, self.g, self.b)
            self.colorpicker.setText(self.translate("MainWindow", f"Pick Color "\
                    f"({str(self.r)},{str(self.g)},{str(self.b)})" ))
            self.pushconfig()

    def EVENT_KEY_PRESS(self,x):
        x = x.upper()
        x.replace("'","")
        self.labelTestKey.setText(self.translate("MainWindow",x))
        self.bindkey(self.SELKEY,x)

    def EVENT_KEY_RELEASE(self, x):
        self.resetkeystyle()
        self.labelTestKey.setText(self.translate("MainWindow",x))
        self.pushconfig()

#===================================  FUNCTIONS  ===========================================

    def hex_to_rgb(self, hex):
        hex = hex.lstrip('#')
        hlen = len(hex)
        return tuple(int(hex[i:i+hlen//3], 16) for i in range(0, hlen, hlen//3))

    def pushconfig(self):
        self.f = open(self.FILE, "w")
        for key, control in self.GKEY.items():
            if len(self.KEYBIND[key]) > 0:
                a = self.KEYACTION[key]
                b = self.KEYBIND[key]
                a = a.replace("%a",b)
                a = a.replace("%g",key)
                self.writefile(a)
        self.writefile("rgb " + str(self.r) + " " + str(self.g) + " " + str(self.b))
        self.f.close()

    def readfile(self):
        self.f = open(self.FILE, "r")
        for l in self.f:
            ar = l.split(" ")
            if ar[0] == "bind":
                self.bindkey(ar[1], ar[2])
            if ar[0] == "rgb":
                self.r = int(ar[1])
                self.g = int(ar[2])
                self.b = int(ar[3])
                self.LCDchange(self.r, self.g, self.b)
                self.colorpicker.setText(self.translate("MainWindow",f"Pick "\
                        f"Color ({str(self.r)},{str(self.g)},{str(self.b)})" ))
        self.f.close()
        self.resetkeystyle()

    def writefile(self, stdout):
        try:
            os.system(f"echo {stdout} > /tmp/g13-0")
            self.f.write(f"{stdout}\n")
        except:
            pass

    def bindkey(self,skey,x):
    	if skey != "":
            control = self.GKEY[skey]
            if len(x) > 0:
                self.KEYBIND[skey] = x.rstrip("\n")
                control.setText(self.translate("MainWindow",x.rstrip("\n")))
            else:
                self.KEYBIND[skey] = ""
                control.setText(self.translate("MainWindow",skey))
            self.SELKEY = ""

    def LCDchange(self, RED, GREEN, BLUE):
        try:
            ra = (RED + 255) / 2
            ga = (GREEN + 255) / 2
            ba = (BLUE + 255) / 2
            self.c = ((hex(int(ra))[2:]).zfill(2) + (hex(int(ga))[2:]).zfill(2) \
                    + (hex(int(ba))[2:]).zfill(2))
            self.rgb = (hex(RED)[2:]).zfill(2) + (hex(GREEN)[2:]).zfill(2) + \
                    (hex(BLUE)[2:]).zfill(2)
            self.LCD.setStyleSheet(f"QTextEdit{{background:#{self.rgb}; "\
                                    f"color:#{self.c};}}")
            self.resetkeystyle()
        except:
            pass

    def resetkeystyle(self):
        for key, control in self.GKEY.items():
            if len(self.KEYBIND[key]) > 0:
                self.setforegroundcolor()
                control.setStyleSheet(f"QPushButton{{background:#222222;"\
                                    f"color:#{self.rgb}; border-radius:"\
                                    f"4px; border: 1px solid #333333;}}"\
                                    f"QPushButton::hover{{border-color:#{self.c};}}")
            else:
                control.setStyleSheet(f"QPushButton{{background:#222222; "\
                                    f"color:white; border-radius: 4px; border:"\
                                    f"1px solid #333333;}} "\
                                    f"QPushButton::hover{{border-color:#{self.c};}}")
        self.SELKEY = ""
        self.labelStatus.setText(self.translate("MainWindow","Click a G-key to assign"))
        self.CLEAR.hide()

    def setforegroundcolor(self):
        r = int((self.r + 255) / 2)
        g = int((self.g + 255) / 2)
        b = int((self.b + 255) / 2)
        self.rgb = (hex(r)[2:]).zfill(2) + (hex(g)[2:]).zfill(2) + (hex(b)[2:]).zfill(2)

#================================  UI COMPONENTS BELOW  ============================

    def setupbutton(self,x,y,w,h,kact,kname,kbind):
        tmp = self.createButton(x, y, w, h, kname)
        tmp.clicked.connect(self.EVENT_GKEY_CLICK)
        self.GKEY[kname] = tmp
        self.KEYACTION[kname] = kact
        self.KEYBIND[kname] = kbind

    def createButton(self, x, y, w, h, name):
        self.button = QPushButton(self.centralwidget)
        self.button.setGeometry(QRect(x,y,w,h))
        font = QFont()
        font.setFamily("Ubuntu Condensed")
        font.setWeight(50)
        self.button.setFont(font)
        self.button.setAutoFillBackground(False)
        self.button.setStyleSheet("QPushButton{background-color:#222222; \
                                color:white; border: 1px solid #333333;}")
        self.button.setText(self.translate("MainWindow", name))
        self.button.setObjectName(name)
        return self.button

    def setupUi(self, MainWindow):
        w = 495
        h = 575
        self.translate = QCoreApplication.translate
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(w, h)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(w, h))
        MainWindow.setMaximumSize(QSize(w, h))
        MainWindow.setStyleSheet("QMainWindow{background:#000000;}")
        MainWindow.setWindowTitle(self.translate("MainWindow", "Linux G13 "\
                "Controller Configuration"))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.setupbutton(15, 195, 50, 40, "bind %g %a","G1","")
        self.setupbutton(75, 195, 50, 40, "bind %g %a","G2","")
        self.setupbutton(135, 195, 50, 40, "bind %g %a","G3","")
        self.setupbutton(195, 195, 50, 40, "bind %g %a","G4","")
        self.setupbutton(255, 195, 50, 40, "bind %g %a","G5","")
        self.setupbutton(315, 195, 50, 40, "bind %g %a","G6","")
        self.setupbutton(375, 195, 50, 40, "bind %g %a","G7","")
        self.setupbutton(15, 245, 50, 40, "bind %g %a","G8","")
        self.setupbutton(75, 245, 50, 40, "bind %g %a","G9","")
        self.setupbutton(135, 245, 50, 40, "bind %g %a","G10","")
        self.setupbutton(195, 245, 50, 40, "bind %g %a","G11","")
        self.setupbutton(255, 245, 50, 40, "bind %g %a","G12","")
        self.setupbutton(315, 245, 50, 40, "bind %g %a","G13","")
        self.setupbutton(375, 245, 50, 40, "bind %g %a","G14","")
        self.setupbutton(75, 295, 50, 40, "bind %g %a","G15","")
        self.setupbutton(135, 295, 50, 40, "bind %g %a","G16","")
        self.setupbutton(195, 295, 50, 40, "bind %g %a","G17","")
        self.setupbutton(255, 295, 50, 40, "bind %g %a","G18","")
        self.setupbutton(315, 295, 50, 40, "bind %g %a","G19","")
        self.setupbutton(135, 345, 50, 40, "bind %g %a","G20","")
        self.setupbutton(195, 345, 50, 40, "bind %g %a","G21","")
        self.setupbutton(255, 345, 50, 40, "bind %g %a","G22","")
        self.setupbutton(315, 405, 50, 40, "bind %g %a","S_LEFT","")
        self.setupbutton(425, 405, 50, 40, "bind %g %a","S_RIGHT","")
        self.setupbutton(370, 360, 50, 40, "bind %g %a","S_UP","")
        self.setupbutton(370, 450, 50, 40, "bind %g %a","S_DOWN","")
        self.setupbutton(370, 405, 50, 40, "bind %g %a","TOP","")
        self.setupbutton(315, 500, 105, 40, "bind %g %a","TD","")
        self.setupbutton(265, 405, 40, 85, "bind %g %a","TL","")
        self.setupbutton(95, 160, 60, 25, "bind %g %a","M1","")
        self.setupbutton(160, 160, 60, 25, "bind %g %a","M2","")
        self.setupbutton(225, 160, 60, 25, "bind %g %a","M3","")
        self.setupbutton(290, 160, 60, 25, "bind %g %a","MR","")
        self.setupbutton(95, 130, 60, 25, "bind %g %a","L1","")
        self.setupbutton(160, 130, 60, 25, "bind %g %a","L2","")
        self.setupbutton(225, 130, 60, 25, "bind %g %a","L3","")
        self.setupbutton(290, 130, 60, 25, "bind %g %a","L4","")
        self.LCD = QTextEdit(self.centralwidget)
        self.LCD.setGeometry(QRect(100, 20, 246, 100))
        self.LCD.setStyleSheet("QTextEdit{background:#000000; color:#888888;}")
        self.LCD.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.LCD.setLineWrapColumnOrWidth(20)
        self.LCD.setObjectName("LCD")
        self.LCD.setFrameStyle(QFrame.Box)
        self.LCD.setHtml(self.translate("MainWindow",""))
        self.CLEARALL = QPushButton(self.centralwidget)
        self.CLEARALL.setGeometry(QRect(375, 20, 90, 25))
        self.CLEARALL.setObjectName("CLEAR")
        self.CLEARALL.setText(self.translate("MainWindow", "Reset All"))
        self.CLEAR = QPushButton(self.centralwidget)
        self.CLEAR.setGeometry(QRect(375, 95, 90, 25))
        self.CLEAR.setObjectName("BIND")
        self.CLEAR.setText(self.translate("MainWindow", "Clear Key"))
        self.labelStatus = QLabel(self.centralwidget)
        self.labelStatus.setGeometry(QRect(1, 550, 382, 25))
        self.labelStatus.setStyleSheet("QLabel{color:#AAAAAA; background:#444444; padding:2px;}")
        self.labelStatus.setObjectName("labelStatus")
        self.labelTestKey = QLabel(self.centralwidget)
        self.labelTestKey.setGeometry(QRect(385, 550, 110, 25))
        self.labelTestKey.setObjectName("labelTestKey")
        self.labelTestKey.setAlignment(QtCore.Qt.AlignCenter)
        self.labelTestKey.setStyleSheet("QLabel{color:#AAAAAA; background:#444444; padding:2px;}")
        self.colorpicker = QPushButton(self.centralwidget)
        self.colorpicker.setGeometry(QRect(100, 20, 200, 25))
        self.colorpicker.setObjectName("ColorPicker")
        self.colorpicker.setText(self.translate("MainWindow", "Pick Color"))
        for key, control in self.GKEY.items():
            control.raise_()
            control.setToolTip(key)
        self.LCD.raise_()
        self.colorpicker.raise_()
        self.labelTestKey.raise_()
        self.CLEARALL.raise_()
        self.CLEAR.raise_()
        self.CLEAR.hide()
        self.labelStatus.raise_()
        QMetaObject.connectSlotsByName(MainWindow)
        self.CLEAR.clicked.connect(self.EVENT_CLEAR_CLICK)
        self.CLEARALL.clicked.connect(self.EVENT_CLEARALL_CLICK)
        self.colorpicker.clicked.connect(self.EVENT_PICKCOLOR_CLICK)
        self.readfile()
        self.resetkeystyle()

    def createText(self, x, y, w, h, c, n):
        self.text = QLineEdit(self.centralwidget)
        self.text.setGeometry(QRect(x, y, w, h))
        self.text.setObjectName(n)
        self.text.setReadOnly(False)
        self.text.setInputMethodHints(Qt.ImhNone)
        self.text.setValidator(QIntValidator(0, 255))
        self.text.setText(self.translate("MainWindow", str(c)))
        return self.text

#===================================  CALL UI INIT  ===================================

class MainWindow(QMainWindow, Ui_Configuration):

#================================  SIGNALS AND SLOTS  ===================================

    EVENT_KEYPRESS = pyqtSignal(str)
    EVENT_KEYRELEASE = pyqtSignal(str)
    def EVENT_ON_PRESS(self, key):
        try:
            x = key.char
            self.EVENT_KEYPRESS.emit(x)
        except:
            x = str('{}'.format(key))
            self.EVENT_KEYPRESS.emit(x[4:])

    def EVENT_ON_RELEASE(self, key):
        self.EVENT_KEYRELEASE.emit("")

#========================================= INIT  ===================================

    def __init__(self):
        QMainWindow.__init__(self)
        Ui_Configuration.__init__(self)
        QThread.__init__(self)
        self.EVENT_KEYPRESS.connect(self.EVENT_KEY_PRESS)
        self.EVENT_KEYRELEASE.connect(self.EVENT_KEY_RELEASE)
        keyboard=Controller()
        listener=Listener(on_press=self.EVENT_ON_PRESS,on_release=self.EVENT_ON_RELEASE)
        listener.start()

#========================================= MAIN Function ===================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
