from functools import partial

from mgear.shifter.component import guide
from mgear.core import pyqt
from mgear.vendor.Qt import QtWidgets, QtCore

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.app.general.mayaMixin import MayaQDockWidget

from . import settingsUI as sui


# guide info
AUTHOR = "anima inc."
URL = "www.studioanima.co.jp"
EMAIL = ""
VERSION = [1, 0, 0]
TYPE = "chain_FK_spline_variable_IK_06"
NAME = "chain"
DESCRIPTION = "FK chain with a spline driven joints. And variable number of \
IK controls. \nFK is master, IK Slave"

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

    def postInit(self):
        """Initialize the position for the guide"""

        self.save_transform = ["root", "#_loc"]
        self.save_blade = ["blade"]
        self.addMinMax("#_loc", 1, -1)

    def addObjects(self):
        """Add the Guide Root, blade and locators"""
        self.root = self.addRoot()
        self.locs = self.addLocMulti("#_loc", self.root)
        self.blade = self.addBlade("blade", self.root, self.locs[0])

        centers = [self.root]
        centers.extend(self.locs)
        self.dispcrv = self.addDispCurve("crv", centers)
        self.addDispCurve("crvRef", centers, 3)

    def addParameters(self):
        """Add the configurations settings"""
        self.pNeutralPose = self.addParam("neutralpose", "bool", False)
        self.pOverrideNegate = self.addParam("overrideNegate", "bool", False)
        self.pKeepLength = self.addParam("keepLength", "bool", False)
        self.pTwist = self.addParam("twist", "bool", False)
        self.pOverrideJointNb = self.addParam("overrideJntNb", "bool", False)
        self.pIkNb = self.addParam("ikNb", "long", 3, 1)
        self.pJntNb = self.addParam("jntNb", "long", 3, 1)
        self.pUseIndex = self.addParam("useIndex", "bool", False)
        self.pParentJointIndex = self.addParam(
            "parentJointIndex", "long", -1, None, None)
        self.pIkRefArray = self.addParam("ikrefarray", "string", "")

##########################################################
# Setting Page
##########################################################


class settingsTab(QtWidgets.QDialog, sui.Ui_Form):

    def __init__(self, parent=None):
        super(settingsTab, self).__init__(parent)
        self.setupUi(self)


class componentSettings(MayaQWidgetDockableMixin, guide.componentMainSettings):

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
        self.populateCheck(self.settingsTab.neutralPose_checkBox,
                           "neutralpose")
        self.populateCheck(self.settingsTab.overrideNegate_checkBox,
                           "overrideNegate")
        self.populateCheck(self.settingsTab.keepLength_checkBox,
                           "keepLength")
        self.populateCheck(self.settingsTab.overrideJntNb_checkBox,
                           "overrideJntNb")
        self.populateCheck(self.settingsTab.twist_checkBox,
                           "twist")
        self.settingsTab.jntNb_spinBox.setValue(self.root.attr("jntNb").get())
        self.settingsTab.ikNb_spinBox.setValue(self.root.attr("ikNb").get())

        ikRefArrayItems = self.root.attr("ikrefarray").get().split(",")
        for item in ikRefArrayItems:
            self.settingsTab.ikRefArray_listWidget.addItem(item)

    def create_componentLayout(self):

        self.settings_layout = QtWidgets.QVBoxLayout()
        self.settings_layout.addWidget(self.tabs)
        self.settings_layout.addWidget(self.close_button)

        self.setLayout(self.settings_layout)

    def create_componentConnections(self):

        self.settingsTab.neutralPose_checkBox.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.neutralPose_checkBox,
                    "neutralpose"))

        self.settingsTab.overrideNegate_checkBox.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.overrideNegate_checkBox,
                    "overrideNegate"))

        self.settingsTab.keepLength_checkBox.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.keepLength_checkBox,
                    "keepLength"))

        self.settingsTab.overrideJntNb_checkBox.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.overrideJntNb_checkBox,
                    "overrideJntNb"))

        self.settingsTab.jntNb_spinBox.valueChanged.connect(
            partial(self.updateSpinBox,
                    self.settingsTab.jntNb_spinBox,
                    "jntNb"))

        self.settingsTab.ikNb_spinBox.valueChanged.connect(
            partial(self.updateSpinBox,
                    self.settingsTab.ikNb_spinBox,
                    "ikNb"))

        self.settingsTab.twist_checkBox.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.twist_checkBox,
                    "twist"))

        self.settingsTab.ikRefArrayAdd_pushButton.clicked.connect(
            partial(self.addItem2listWidget,
                    self.settingsTab.ikRefArray_listWidget,
                    "ikrefarray"))

        self.settingsTab.ikRefArrayRemove_pushButton.clicked.connect(
            partial(self.removeSelectedFromListWidget,
                    self.settingsTab.ikRefArray_listWidget,
                    "ikrefarray"))
        self.settingsTab.ikRefArray_listWidget.installEventFilter(self)

    def dockCloseEventTriggered(self):
        pyqt.deleteInstances(self, MayaQDockWidget)
