# MGEAR is under the terms of the MIT License

# Copyright (c) 2016 Jeremie Passerin, Miquel Campos
'''
    Component Foot Banking 02 module.
    Added toePivot loc to build tip ctl flat on ground,
    and orient heel ctl to tip.
'''

from functools import partial
import pymel.core as pm

from mgear.shifter.component import guide
from mgear.core import transform, pyqt
from mgear.vendor.Qt import QtWidgets, QtCore

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.app.general.mayaMixin import MayaQDockWidget

from . import settingsUI as sui

# guide info
AUTHOR = "C.M."
URL = ""
EMAIL = ""
VERSION = [1, 0, 0]
TYPE = "foot_bk_02"
NAME = "foot"
DESCRIPTION = "Foot with reversed controllers to control foot roll." \
                " Added toepivot guide to this version." \
                " Connects to leg_2jnt_freeTangents only"

##########################################################
# CLASS
##########################################################


class Guide(guide.ComponentGuide):
    """Component Guide Class"""

    compType = TYPE
    compName = NAME
    description = DESCRIPTION

    author = AUTHOR
    url = URL
    email = EMAIL
    version = VERSION

    connectors = ["leg_2jnt_01", "leg_ms_2jnt_01", "leg_2jntOffset_01", "leg_3jnt_01"]

    def postInit(self):
        """Initialize the position for the guide"""
        self.save_transform = ["root", "0_loc", "1_loc", "2_loc", "heel", "outpivot", "inpivot", "toepivot"]

    def addObjects(self):
        """Add the Guide Root, blade and locators"""

        self.root = self.addRoot()
        self.loc0 = self.addLoc("0_loc", self.root, position=[0, -0.5, 1])
        self.loc1 = self.addLoc("1_loc", self.loc0, position=[0, -0.5, 2])
        self.loc2 = self.addLoc("2_loc", self.loc1, position=[0, -0.5, 3])
        self.locs = [self.loc0, self.loc1, self.loc2]

        centers = [self.root]
        centers.extend(self.locs)
        self.dispcrv = self.addDispCurve("crv", centers)

        # Heel and pivots
        vTemp = transform.getOffsetPosition(self.root, [0, -1, -1])
        self.heel = self.addLoc("heel", self.root, vTemp)
        vTemp = transform.getOffsetPosition(self.root, [1, -1, -1])
        self.outpivot = self.addLoc("outpivot", self.root, vTemp)
        vTemp = transform.getOffsetPosition(self.root, [-1, -1, -1])
        self.inpivot = self.addLoc("inpivot", self.root, vTemp)
        vTemp = transform.getOffsetPosition(self.root, [-2, -1, -1])
        self.toepivot = self.addLoc("toepivot", self.root, vTemp)

        cnt = [self.root, self.heel, self.outpivot, self.heel, self.inpivot, self.heel, self.toepivot]
        self.dispcrv = self.addDispCurve("1", cnt)

    def addParameters(self):
        """Add the configurations settings"""

        self.pRoll = self.addParam("useRollCtl", "bool", True)
        self.pUseIndex = self.addParam("useIndex", "bool", False)
        self.pParentJointIndex = self.addParam(
            "parentJointIndex", "long", -1, None, None)
        self.angle0 = self.addParam('angle0', "long", -20, None, None)
        self.angle1 = self.addParam('angle1', "long", -20, None, None)


##########################################################
# Setting Page
##########################################################

class settingsTab(QtWidgets.QDialog, sui.Ui_Form):
    """The Component settings UI"""

    def __init__(self, parent=None):
        super(settingsTab, self).__init__(parent)
        self.setupUi(self)


class componentSettings(MayaQWidgetDockableMixin, guide.componentMainSettings):
    """Create the component setting window"""

    def __init__(self, parent=None):
        self.toolName = TYPE
        # Delete old instances of the componet settings window.
        pyqt.deleteInstances(self, MayaQDockWidget)

        super(self.__class__, self).__init__(parent=parent)
        self.settingsTab = settingsTab()

        self.setup_componentSettingWindow()
        self.create_componentControls()
        self.populate_componentControls()
        self.create_componentLayout()
        self.create_componentConnections()

    def setup_componentSettingWindow(self):
        self.mayaMainWindow = pyqt.maya_main_window()

        self.setObjectName(self.toolName)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(TYPE)
        self.resize(280, 350)

    def create_componentControls(self):
        return

    def populate_componentControls(self):
        """Populate Controls

        Populate the controls values from the custom attributes of the
        component.

        """
        # populate tab
        self.tabs.insertTab(1, self.settingsTab, "Component Settings")

        # populate component settings
        self.populateCheck(self.settingsTab.useRollCtl_checkBox, "useRollCtl")

        # populate connections in main settings
        for cnx in Guide.connectors:
            self.mainSettingsTab.connector_comboBox.addItem(cnx)
        cBox = self.mainSettingsTab.connector_comboBox
        self.connector_items = [cBox.itemText(i) for i in range(cBox.count())]
        currentConnector = self.root.attr("connector").get()
        if currentConnector not in self.connector_items:
            self.mainSettingsTab.connector_comboBox.addItem(currentConnector)
            self.connector_items.append(currentConnector)
            pm.displayWarning("The current connector: %s, is not a valid "
                              "connector for this component. "
                              "Build will Fail!!")
        comboIndex = self.connector_items.index(currentConnector)
        self.mainSettingsTab.connector_comboBox.setCurrentIndex(comboIndex)

    def create_componentLayout(self):

        self.settings_layout = QtWidgets.QVBoxLayout()
        self.settings_layout.addWidget(self.tabs)
        self.settings_layout.addWidget(self.close_button)

        self.setLayout(self.settings_layout)

    def create_componentConnections(self):

        self.settingsTab.useRollCtl_checkBox.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.useRollCtl_checkBox,
                    "useRollCtl"))
        self.mainSettingsTab.connector_comboBox.currentIndexChanged.connect(
            partial(self.updateConnector,
                    self.mainSettingsTab.connector_comboBox,
                    self.connector_items))
        self.settingsTab.ang0_spinBox.valueChanged.connect(
            partial(self.updateSpinBox, self.settingsTab.ang0_spinBox, "angle0"))
        self.settingsTab.ang1_spinBox.valueChanged.connect(
            partial(self.updateSpinBox, self.settingsTab.ang1_spinBox, "angle1"))
    def dockCloseEventTriggered(self):
        pyqt.deleteInstances(self, MayaQDockWidget)
