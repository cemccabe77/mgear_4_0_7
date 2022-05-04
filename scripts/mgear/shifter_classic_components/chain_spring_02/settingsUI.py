# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:/Working/cmlib/cmMayaWorkgroup2020/mGear/scripts/mgear/shifter_classic_components/chain_spring_02/settingsUI.ui',
# licensing of 'D:/Working/cmlib/cmMayaWorkgroup2020/mGear/scripts/mgear/shifter_classic_components/chain_spring_02/settingsUI.ui' applies.
#
# Created: Tue Jun 15 13:48:41 2021
#      by: pyside2-uic  running on PySide2 5.12.5
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(260, 173)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.mirrorBehaviour_checkBox = QtWidgets.QCheckBox(Form)
        self.mirrorBehaviour_checkBox.setObjectName("mirrorBehaviour_checkBox")
        self.gridLayout.addWidget(self.mirrorBehaviour_checkBox, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtWidgets.QApplication.translate("Form", "Form", None, -1))
        self.mirrorBehaviour_checkBox.setText(QtWidgets.QApplication.translate("Form", "Mirror Behaviour L and R", None, -1))

