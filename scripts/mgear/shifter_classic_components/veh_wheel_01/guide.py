"""Guide Control 01 module"""

from functools import partial
import pymel.core as pm

from mgear.shifter.component import guide
from mgear.core import transform, pyqt, attribute
from mgear.vendor.Qt import QtWidgets, QtCore
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.app.general.mayaMixin import MayaQDockWidget
from . import settingsUI as sui

# guide info
AUTHOR = "Jeremie Passerin, Miquel Campos"
URL = "www.jeremiepasserin.com, www.miquel-campos.com"
EMAIL = ""
VERSION = [1, 3, 0]
TYPE = "veh_wheel_01"
NAME = "wheel"
DESCRIPTION = "Creates a wheel component. \n"\

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

    connectors = ["steering"]

    # =====================================================
    # @param self
    def postInit(self):
        self.save_transform = ["root", "sizeRef", "circumference_loc", "center_loc", "radius_loc"]

    # =====================================================
    # Add more object to the object definition list.
    # @param self
    def addObjects(self):
        self.root = self.addRoot()

        vTemp = transform.getOffsetPosition(self.root, [0, 1, 1])
        self.sizeRef = self.addLoc("sizeRef", self.root, vTemp)
        pm.delete(self.sizeRef.getShapes())
        attribute.lockAttribute(self.sizeRef)

        self.loc0 = self.addLoc("center_loc", self.root, position=[1, 0, 0])
        self.loc1 = self.addLoc("circumference_loc", self.loc0, position=[1.5, 0, 0])
        self.loc2 = self.addLoc("radius_loc", self.loc0, position=[1,-1, 0])
        self.locs = [self.loc0, self.loc1, self.loc0, self.loc2]

        centers = [self.root]
        centers.extend(self.locs)
        self.dispcrv = self.addDispCurve("crv", centers)

    # =====================================================
    # Add more parameter to the parameter definition list.
    # @param self
    def addParameters(self):
        self.pNeutralRotation = self.addParam("neutralRotation", "bool", True)
        self.pUseIndex = self.addParam("useIndex", "bool", False)
        self.pParentJointIndex = self.addParam("parentJointIndex", "long", -1, None, None)
        return

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
        self.populate_componentControls()
        self.create_componentLayout()
        self.create_componentConnections()

    def setup_componentSettingWindow(self):
        self.mayaMainWindow = pyqt.maya_main_window()
        self.setObjectName(self.toolName)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(TYPE)
        self.resize(280, 520)

    def populate_componentControls(self):
        """
        Populate the controls values from the custom attributes of the
        component.
        """

        # populate tab
        self.tabs.insertTab(1, self.settingsTab, "Component Settings")

        # populate component settings

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
        self.mainSettingsTab.connector_comboBox.currentIndexChanged.connect(
            partial(self.updateConnector,
                    self.mainSettingsTab.connector_comboBox,
                    self.connector_items))

    def dockCloseEventTriggered(self):
        pyqt.deleteInstances(self, MayaQDockWidget)