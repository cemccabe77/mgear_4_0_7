# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:/Working/cmlib/cmMayaWorkgroup2020/mGear/scripts/mgear/shifter_classic_components/foot_bk_02/settingsUI.ui',
# licensing of 'D:/Working/cmlib/cmMayaWorkgroup2020/mGear/scripts/mgear/shifter_classic_components/foot_bk_02/settingsUI.ui' applies.
#
# Created: Tue Jun 15 09:11:21 2021
#      by: pyside2-uic  running on PySide2 5.12.5
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(269, 148)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.useRollCtl_checkBox = QtWidgets.QCheckBox(self.groupBox)
        self.useRollCtl_checkBox.setObjectName("useRollCtl_checkBox")
        self.gridLayout_2.addWidget(self.useRollCtl_checkBox, 0, 0, 1, 1)
        self.angle0_label = QtWidgets.QLabel(self.groupBox)
        self.angle0_label.setObjectName("angle0_label")
        self.gridLayout_2.addWidget(self.angle0_label, 1, 0, 1, 1)
        self.ang0_spinBox = QtWidgets.QSpinBox(self.groupBox)
        self.ang0_spinBox.setMinimum(-180)
        self.ang0_spinBox.setMaximum(180)
        self.ang0_spinBox.setProperty("value", -20)
        self.ang0_spinBox.setObjectName("ang0_spinBox")
        self.gridLayout_2.addWidget(self.ang0_spinBox, 1, 1, 1, 1)
        self.angle1_label = QtWidgets.QLabel(self.groupBox)
        self.angle1_label.setObjectName("angle1_label")
        self.gridLayout_2.addWidget(self.angle1_label, 2, 0, 1, 1)
        self.ang1_spinBox = QtWidgets.QSpinBox(self.groupBox)
        self.ang1_spinBox.setMinimum(-180)
        self.ang1_spinBox.setMaximum(180)
        self.ang1_spinBox.setProperty("value", -20)
        self.ang1_spinBox.setObjectName("ang1_spinBox")
        self.gridLayout_2.addWidget(self.ang1_spinBox, 2, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtWidgets.QApplication.translate("Form", "Form", None, -1))
        self.useRollCtl_checkBox.setText(QtWidgets.QApplication.translate("Form", "Use Roll Ctl", None, -1))
        self.angle0_label.setText(QtWidgets.QApplication.translate("Form", "Angle 0", None, -1))
        self.angle1_label.setText(QtWidgets.QApplication.translate("Form", "Angle 1", None, -1))

