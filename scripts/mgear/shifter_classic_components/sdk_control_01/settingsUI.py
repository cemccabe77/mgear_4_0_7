# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Justi\OneDrive\Documents\maya\mGear\scripts\mgear\shifter_classic_components\sdk_control_01\settingsUI.ui'
#
# Created: Sat Aug 24 10:20:58 2019
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(352, 505)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.joint_checkBox = QtWidgets.QCheckBox(self.groupBox)
        self.joint_checkBox.setObjectName("joint_checkBox")
        self.verticalLayout_4.addWidget(self.joint_checkBox)
        self.uniScale_checkBox = QtWidgets.QCheckBox(self.groupBox)
        self.uniScale_checkBox.setObjectName("uniScale_checkBox")
        self.verticalLayout_4.addWidget(self.uniScale_checkBox)
        self.neutralRotation_checkBox = QtWidgets.QCheckBox(self.groupBox)
        self.neutralRotation_checkBox.setObjectName("neutralRotation_checkBox")
        self.verticalLayout_4.addWidget(self.neutralRotation_checkBox)
        self.mirrorBehaviour_checkBox = QtWidgets.QCheckBox(self.groupBox)
        self.mirrorBehaviour_checkBox.setObjectName("mirrorBehaviour_checkBox")
        self.verticalLayout_4.addWidget(self.mirrorBehaviour_checkBox)
        self.customPivot_checkBox = QtWidgets.QCheckBox(self.groupBox)
        self.customPivot_checkBox.setObjectName("customPivot_checkBox")
        self.verticalLayout_4.addWidget(self.customPivot_checkBox)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.ctlSize_label = QtWidgets.QLabel(self.groupBox)
        self.ctlSize_label.setObjectName("ctlSize_label")
        self.horizontalLayout_3.addWidget(self.ctlSize_label)
        self.ctlSize_doubleSpinBox = QtWidgets.QDoubleSpinBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ctlSize_doubleSpinBox.sizePolicy().hasHeightForWidth())
        self.ctlSize_doubleSpinBox.setSizePolicy(sizePolicy)
        self.ctlSize_doubleSpinBox.setWrapping(False)
        self.ctlSize_doubleSpinBox.setAlignment(QtCore.Qt.AlignCenter)
        self.ctlSize_doubleSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.PlusMinus)
        self.ctlSize_doubleSpinBox.setMinimum(0.01)
        self.ctlSize_doubleSpinBox.setMaximum(20000.0)
        self.ctlSize_doubleSpinBox.setProperty("value", 1.0)
        self.ctlSize_doubleSpinBox.setObjectName("ctlSize_doubleSpinBox")
        self.horizontalLayout_3.addWidget(self.ctlSize_doubleSpinBox)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.controlShape_label = QtWidgets.QLabel(self.groupBox)
        self.controlShape_label.setText("Control Shape")
        self.controlShape_label.setObjectName("controlShape_label")
        self.horizontalLayout_2.addWidget(self.controlShape_label)
        self.controlShape_comboBox = QtWidgets.QComboBox(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.controlShape_comboBox.sizePolicy().hasHeightForWidth())
        self.controlShape_comboBox.setSizePolicy(sizePolicy)
        self.controlShape_comboBox.setObjectName("controlShape_comboBox")
        self.controlShape_comboBox.addItem("")
        self.controlShape_comboBox.addItem("")
        self.controlShape_comboBox.addItem("")
        self.controlShape_comboBox.addItem("")
        self.controlShape_comboBox.addItem("")
        self.controlShape_comboBox.addItem("")
        self.controlShape_comboBox.addItem("")
        self.controlShape_comboBox.addItem("")
        self.controlShape_comboBox.addItem("")
        self.controlShape_comboBox.addItem("")
        self.controlShape_comboBox.addItem("")
        self.controlShape_comboBox.addItem("")
        self.controlShape_comboBox.addItem("")
        self.controlShape_comboBox.addItem("")
        self.horizontalLayout_2.addWidget(self.controlShape_comboBox)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.gridLayout_2.addLayout(self.verticalLayout_4, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.keyable_groupBox = QtWidgets.QGroupBox(Form)
        self.keyable_groupBox.setObjectName("keyable_groupBox")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.keyable_groupBox)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.verticalLayout.setObjectName("verticalLayout")
        self.translate_pushButton = QtWidgets.QPushButton(self.keyable_groupBox)
        self.translate_pushButton.setObjectName("translate_pushButton")
        self.verticalLayout.addWidget(self.translate_pushButton)
        self.tx_checkBox = QtWidgets.QCheckBox(self.keyable_groupBox)
        self.tx_checkBox.setObjectName("tx_checkBox")
        self.verticalLayout.addWidget(self.tx_checkBox)
        self.ty_checkBox = QtWidgets.QCheckBox(self.keyable_groupBox)
        self.ty_checkBox.setObjectName("ty_checkBox")
        self.verticalLayout.addWidget(self.ty_checkBox)
        self.tz_checkBox = QtWidgets.QCheckBox(self.keyable_groupBox)
        self.tz_checkBox.setObjectName("tz_checkBox")
        self.verticalLayout.addWidget(self.tz_checkBox)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.rotate_pushButton = QtWidgets.QPushButton(self.keyable_groupBox)
        self.rotate_pushButton.setObjectName("rotate_pushButton")
        self.verticalLayout_2.addWidget(self.rotate_pushButton)
        self.rx_checkBox = QtWidgets.QCheckBox(self.keyable_groupBox)
        self.rx_checkBox.setObjectName("rx_checkBox")
        self.verticalLayout_2.addWidget(self.rx_checkBox)
        self.ry_checkBox = QtWidgets.QCheckBox(self.keyable_groupBox)
        self.ry_checkBox.setObjectName("ry_checkBox")
        self.verticalLayout_2.addWidget(self.ry_checkBox)
        self.rz_checkBox = QtWidgets.QCheckBox(self.keyable_groupBox)
        self.rz_checkBox.setObjectName("rz_checkBox")
        self.verticalLayout_2.addWidget(self.rz_checkBox)
        self.ro_checkBox = QtWidgets.QCheckBox(self.keyable_groupBox)
        self.ro_checkBox.setObjectName("ro_checkBox")
        self.verticalLayout_2.addWidget(self.ro_checkBox)
        self.ro_comboBox = QtWidgets.QComboBox(self.keyable_groupBox)
        self.ro_comboBox.setObjectName("ro_comboBox")
        self.ro_comboBox.addItem("")
        self.ro_comboBox.addItem("")
        self.ro_comboBox.addItem("")
        self.ro_comboBox.addItem("")
        self.ro_comboBox.addItem("")
        self.ro_comboBox.addItem("")
        self.verticalLayout_2.addWidget(self.ro_comboBox)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.scale_pushButton = QtWidgets.QPushButton(self.keyable_groupBox)
        self.scale_pushButton.setObjectName("scale_pushButton")
        self.verticalLayout_3.addWidget(self.scale_pushButton)
        self.sx_checkBox = QtWidgets.QCheckBox(self.keyable_groupBox)
        self.sx_checkBox.setObjectName("sx_checkBox")
        self.verticalLayout_3.addWidget(self.sx_checkBox)
        self.sy_checkBox = QtWidgets.QCheckBox(self.keyable_groupBox)
        self.sy_checkBox.setObjectName("sy_checkBox")
        self.verticalLayout_3.addWidget(self.sy_checkBox)
        self.sz_checkBox = QtWidgets.QCheckBox(self.keyable_groupBox)
        self.sz_checkBox.setObjectName("sz_checkBox")
        self.verticalLayout_3.addWidget(self.sz_checkBox)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_3.addItem(spacerItem1)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.gridLayout_4.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.keyable_groupBox, 1, 0, 1, 1)
        self.ikRefArray_groupBox = QtWidgets.QGroupBox(Form)
        self.ikRefArray_groupBox.setObjectName("ikRefArray_groupBox")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.ikRefArray_groupBox)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.ikRefArray_horizontalLayout = QtWidgets.QHBoxLayout()
        self.ikRefArray_horizontalLayout.setObjectName("ikRefArray_horizontalLayout")
        self.ikRefArray_verticalLayout_1 = QtWidgets.QVBoxLayout()
        self.ikRefArray_verticalLayout_1.setObjectName("ikRefArray_verticalLayout_1")
        self.ikRefArray_listWidget = QtWidgets.QListWidget(self.ikRefArray_groupBox)
        self.ikRefArray_listWidget.setDragDropOverwriteMode(True)
        self.ikRefArray_listWidget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.ikRefArray_listWidget.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.ikRefArray_listWidget.setAlternatingRowColors(True)
        self.ikRefArray_listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.ikRefArray_listWidget.setSelectionRectVisible(False)
        self.ikRefArray_listWidget.setObjectName("ikRefArray_listWidget")
        self.ikRefArray_verticalLayout_1.addWidget(self.ikRefArray_listWidget)
        self.ikRefArray_horizontalLayout.addLayout(self.ikRefArray_verticalLayout_1)
        self.ikRefArray_verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.ikRefArray_verticalLayout_2.setObjectName("ikRefArray_verticalLayout_2")
        self.ikRefArrayAdd_pushButton = QtWidgets.QPushButton(self.ikRefArray_groupBox)
        self.ikRefArrayAdd_pushButton.setObjectName("ikRefArrayAdd_pushButton")
        self.ikRefArray_verticalLayout_2.addWidget(self.ikRefArrayAdd_pushButton)
        self.ikRefArrayRemove_pushButton = QtWidgets.QPushButton(self.ikRefArray_groupBox)
        self.ikRefArrayRemove_pushButton.setObjectName("ikRefArrayRemove_pushButton")
        self.ikRefArray_verticalLayout_2.addWidget(self.ikRefArrayRemove_pushButton)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.ikRefArray_verticalLayout_2.addItem(spacerItem2)
        self.ikRefArray_horizontalLayout.addLayout(self.ikRefArray_verticalLayout_2)
        self.gridLayout_3.addLayout(self.ikRefArray_horizontalLayout, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.ikRefArray_groupBox, 2, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.translate_pushButton, QtCore.SIGNAL("clicked()"), self.tx_checkBox.toggle)
        QtCore.QObject.connect(self.translate_pushButton, QtCore.SIGNAL("clicked()"), self.ty_checkBox.toggle)
        QtCore.QObject.connect(self.translate_pushButton, QtCore.SIGNAL("clicked()"), self.tz_checkBox.toggle)
        QtCore.QObject.connect(self.rotate_pushButton, QtCore.SIGNAL("clicked()"), self.rx_checkBox.toggle)
        QtCore.QObject.connect(self.rotate_pushButton, QtCore.SIGNAL("clicked()"), self.ry_checkBox.toggle)
        QtCore.QObject.connect(self.rotate_pushButton, QtCore.SIGNAL("clicked()"), self.rz_checkBox.toggle)
        QtCore.QObject.connect(self.rotate_pushButton, QtCore.SIGNAL("clicked()"), self.ro_checkBox.toggle)
        QtCore.QObject.connect(self.scale_pushButton, QtCore.SIGNAL("clicked()"), self.sx_checkBox.toggle)
        QtCore.QObject.connect(self.scale_pushButton, QtCore.SIGNAL("clicked()"), self.sy_checkBox.toggle)
        QtCore.QObject.connect(self.scale_pushButton, QtCore.SIGNAL("clicked()"), self.sz_checkBox.toggle)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtWidgets.QApplication.translate("Form", "Form", None, -1))
        self.joint_checkBox.setText(QtWidgets.QApplication.translate("Form", "Joint", None, -1))
        self.uniScale_checkBox.setText(QtWidgets.QApplication.translate("Form", "Uniform Scale", None, -1))
        self.neutralRotation_checkBox.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>If is active, it will align the control with world space</p></body></html>", None, -1))
        self.neutralRotation_checkBox.setText(QtWidgets.QApplication.translate("Form", "World Space Orientation Align", None, -1))
        self.mirrorBehaviour_checkBox.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>If is active, the control will have symmetrical behaviour on Left and Right side.</p><p><br/></p><p>WARNING: There is a bug in Maya 2018 and 2018.1 that will result in an incorrect behaviour, because this option will negate one of the axis. Other Maya version should be ok.</p></body></html>", None, -1))
        self.mirrorBehaviour_checkBox.setText(QtWidgets.QApplication.translate("Form", "Mirror Behaviour L and R", None, -1))
        self.customPivot_checkBox.setText(QtWidgets.QApplication.translate("Form", "Custom Pivot", None, -1))
        self.ctlSize_label.setText(QtWidgets.QApplication.translate("Form", "Ctl Size", None, -1))
        self.controlShape_comboBox.setItemText(0, QtWidgets.QApplication.translate("Form", "Arrow", None, -1))
        self.controlShape_comboBox.setItemText(1, QtWidgets.QApplication.translate("Form", "Circle", None, -1))
        self.controlShape_comboBox.setItemText(2, QtWidgets.QApplication.translate("Form", "Compas", None, -1))
        self.controlShape_comboBox.setItemText(3, QtWidgets.QApplication.translate("Form", "Cross", None, -1))
        self.controlShape_comboBox.setItemText(4, QtWidgets.QApplication.translate("Form", "Crossarrow", None, -1))
        self.controlShape_comboBox.setItemText(5, QtWidgets.QApplication.translate("Form", "Cube", None, -1))
        self.controlShape_comboBox.setItemText(6, QtWidgets.QApplication.translate("Form", "Cubewithpeak", None, -1))
        self.controlShape_comboBox.setItemText(7, QtWidgets.QApplication.translate("Form", "Cylinder", None, -1))
        self.controlShape_comboBox.setItemText(8, QtWidgets.QApplication.translate("Form", "Diamond", None, -1))
        self.controlShape_comboBox.setItemText(9, QtWidgets.QApplication.translate("Form", "Flower", None, -1))
        self.controlShape_comboBox.setItemText(10, QtWidgets.QApplication.translate("Form", "Null", None, -1))
        self.controlShape_comboBox.setItemText(11, QtWidgets.QApplication.translate("Form", "Pyramid", None, -1))
        self.controlShape_comboBox.setItemText(12, QtWidgets.QApplication.translate("Form", "Sphere", None, -1))
        self.controlShape_comboBox.setItemText(13, QtWidgets.QApplication.translate("Form", "Square", None, -1))
        self.keyable_groupBox.setTitle(QtWidgets.QApplication.translate("Form", "Keyable", None, -1))
        self.translate_pushButton.setText(QtWidgets.QApplication.translate("Form", "Translate", None, -1))
        self.tx_checkBox.setText(QtWidgets.QApplication.translate("Form", "tx", None, -1))
        self.ty_checkBox.setText(QtWidgets.QApplication.translate("Form", "ty", None, -1))
        self.tz_checkBox.setText(QtWidgets.QApplication.translate("Form", "tz", None, -1))
        self.rotate_pushButton.setText(QtWidgets.QApplication.translate("Form", "Rotate", None, -1))
        self.rx_checkBox.setText(QtWidgets.QApplication.translate("Form", "rx", None, -1))
        self.ry_checkBox.setText(QtWidgets.QApplication.translate("Form", "ry", None, -1))
        self.rz_checkBox.setText(QtWidgets.QApplication.translate("Form", "rz", None, -1))
        self.ro_checkBox.setText(QtWidgets.QApplication.translate("Form", "ro", None, -1))
        self.ro_comboBox.setItemText(0, QtWidgets.QApplication.translate("Form", "XYZ", None, -1))
        self.ro_comboBox.setItemText(1, QtWidgets.QApplication.translate("Form", "YZX", None, -1))
        self.ro_comboBox.setItemText(2, QtWidgets.QApplication.translate("Form", "ZXY", None, -1))
        self.ro_comboBox.setItemText(3, QtWidgets.QApplication.translate("Form", "XZY", None, -1))
        self.ro_comboBox.setItemText(4, QtWidgets.QApplication.translate("Form", "YXZ", None, -1))
        self.ro_comboBox.setItemText(5, QtWidgets.QApplication.translate("Form", "ZYX", None, -1))
        self.scale_pushButton.setText(QtWidgets.QApplication.translate("Form", "Scale", None, -1))
        self.sx_checkBox.setText(QtWidgets.QApplication.translate("Form", "sx", None, -1))
        self.sy_checkBox.setText(QtWidgets.QApplication.translate("Form", "sy", None, -1))
        self.sz_checkBox.setText(QtWidgets.QApplication.translate("Form", "sz", None, -1))
        self.ikRefArray_groupBox.setTitle(QtWidgets.QApplication.translate("Form", "IK Reference Array", None, -1))
        self.ikRefArrayAdd_pushButton.setText(QtWidgets.QApplication.translate("Form", "<<", None, -1))
        self.ikRefArrayRemove_pushButton.setText(QtWidgets.QApplication.translate("Form", ">>", None, -1))

