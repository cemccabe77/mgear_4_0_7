"""Guide Hydraulic 01 module"""

from functools import partial

from mgear.shifter.component import guide
from mgear.core import transform, pyqt, vector
from mgear.vendor.Qt import QtWidgets, QtCore

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.app.general.mayaMixin import MayaQDockWidget

from . import settingsUI as sui

# guide info
AUTHOR = "anima inc."
URL = "www.studioanima.co.jp"
EMAIL = ""
VERSION = [1, 0, 0]
TYPE = "cable_01"
NAME = "cable"
DESCRIPTION = "Create simple cable rig with 2 points attachment"

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
        self.save_transform = ["root", "tan0", "tan1", "tip"]
        self.save_blade = ["blade"]

    def addObjects(self):
        """Add the Guide Root, blade and locators"""

        self.root = self.addRoot()
        vTemp = transform.getOffsetPosition(self.root, [0, 4, 0])
        self.tip = self.addLoc("tip", self.root, vTemp)

        vTan0 = vector.linearlyInterpolate(
            self.root.getTranslation(space="world"),
            self.tip.getTranslation(space="world"),
            0.3333
        )
        self.tan0 = self.addLoc("tan0", self.root, vTan0)

        vTan1 = vector.linearlyInterpolate(
            self.tip.getTranslation(space="world"),
            self.root.getTranslation(space="world"),
            0.3333
        )
        self.tan1 = self.addLoc("tan1", self.tip, vTan1)

        self.blade = self.addBlade("blade", self.root, self.tan0)

        # spine curve
        centers = [self.root, self.tan0, self.tan1, self.tip]
        self.dispcrv = self.addDispCurve("crv", centers, 3)
        self.dispcrv.attr("lineWidth").set(5)

        # tangent handles
        self.disp_tancrv0 = self.addDispCurve("crvTan0",
                                              [self.root, self.tan0])
        self.disp_tancrv1 = self.addDispCurve("crvTan1",
                                              [self.tip, self.tan1])

    def addParameters(self):
        """Add the configurations settings"""

        self.pRefArray = self.addParam("ikrefarray", "string", "")
        self.pUseIndex = self.addParam("useIndex", "bool", False)
        self.pParentJointIndex = self.addParam(
            "parentJointIndex", "long", -1, None, None)

        self.pDiv = self.addParam("div", "long", 6, 2, None)

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
        self.settingsTab.div_spinBox.setValue(self.root.attr("div").get())

        refArrayItems = self.root.attr("ikrefarray").get().split(",")
        for item in refArrayItems:
            self.settingsTab.refArray_listWidget.addItem(item)

    def create_componentLayout(self):

        self.settings_layout = QtWidgets.QVBoxLayout()
        self.settings_layout.addWidget(self.tabs)
        self.settings_layout.addWidget(self.close_button)

        self.setLayout(self.settings_layout)

    def create_componentConnections(self):

        self.settingsTab.div_spinBox.valueChanged.connect(
            partial(self.updateSpinBox, self.settingsTab.div_spinBox, "div"))
        self.settingsTab.refArrayAdd_pushButton.clicked.connect(
            partial(self.addItem2listWidget,
                    self.settingsTab.refArray_listWidget,
                    "ikrefarray"))
        self.settingsTab.refArrayRemove_pushButton.clicked.connect(
            partial(self.removeSelectedFromListWidget,
                    self.settingsTab.refArray_listWidget,
                    "ikrefarray"))
        self.settingsTab.refArray_listWidget.installEventFilter(self)

    def eventFilter(self, sender, event):
        if event.type() == QtCore.QEvent.ChildRemoved:
            if sender == self.settingsTab.refArray_listWidget:
                self.updateListAttr(sender, "ikrefarray")
            return True
        else:
            return QtWidgets.QDialog.eventFilter(self, sender, event)

    def dockCloseEventTriggered(self):
        pyqt.deleteInstances(self, MayaQDockWidget)
