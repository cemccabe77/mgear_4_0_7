"""Guide Chassis 01 module"""

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
VERSION = [1, 0, 0]
TYPE = "veh_chassis_01"
NAME = "chassis"
DESCRIPTION = "4 wheel chassis component"

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

    connectors = ["orientation"]

    # =====================================================
    ##
    # @param self
    def postInit(self):
        self.save_transform = ["root", "sizeRef", "0_loc", "1_loc", "2_loc", "3_loc"]

    # =====================================================
    # Add more object to the object definition list.
    # @param self
    def addObjects(self):
        self.root = self.addRoot()
        vTemp = transform.getOffsetPosition(self.root, [0, 0, 1])
        self.sizeRef = self.addLoc("sizeRef", self.root, vTemp)
        pm.delete(self.sizeRef.getShapes())
        attribute.lockAttribute(self.sizeRef)

        self.loc0 = self.addLoc("0_loc", self.root, position=[ 2, 0,-3])
        self.loc1 = self.addLoc("1_loc", self.root, position=[ 2, 0, 3])
        self.loc2 = self.addLoc("2_loc", self.root, position=[-2, 0, 3])
        self.loc3 = self.addLoc("3_loc", self.root, position=[-2, 0,-3])
        self.locs = [self.root, self.loc0, self.loc1, self.loc2, self.loc3]

        centers = self.locs
        self.dispcrv = self.addDispCurve("crv", centers)

    # =====================================================
    # Add more parameter to the parameter definition list.
    # @param self
    def addParameters(self):
        self.pIcon = self.addParam("icon", "string", "cube")
        self.pJoint = self.addParam("joint", "bool", False)
        self.pJoint = self.addParam("uniScale", "bool", False)
        for s in ["tx", "ty", "tz", "ro", "rx", "ry", "rz", "sx", "sy", "sz"]:
            self.addParam("k_" + s, "bool", True)
        self.pDefault_RotOrder = self.addParam(
            "default_rotorder", "long", 0, 0, 5)
        self.pNeutralRotation = self.addParam("neutralRotation", "bool", True)
        self.pMirrorBehaviour = self.addParam("mirrorBehaviour", "bool", False)
        self.pCtlSize = self.addParam("ctlSize", "double", 1, None, None)
        self.pUseIndex = self.addParam("useIndex", "bool", False)
        self.pParentJointIndex = self.addParam(
            "parentJointIndex", "long", -1, None, None)
        self.pIkRefArrayLR = self.addParam("ikrefarrayLR", "string", "")
        self.pIkRefArrayLR = self.addParam("ikrefarrayLF", "string", "")
        self.pIkRefArrayRF = self.addParam("ikrefarrayRF", "string", "")
        self.pIkRefArrayRR = self.addParam("ikrefarrayRR", "string", "")
        self.pGlobalArray = self.addParam("globalscalearray", "string", "")

    def postDraw(self):
        "Add post guide draw elements to the guide"
        size = pm.xform(self.root, q=True, ws=True, scale=True)[0]
        self.add_ref_axis(self.root,
                          self.root.neutralRotation,
                          inverted=True,
                          width=.5 / size)

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
        self.iconsList = ['arrow',
                          'circle',
                          'compas',
                          'cross',
                          'crossarrow',
                          'cube',
                          'cubewithpeak',
                          'cylinder',
                          'diamond',
                          'flower',
                          'null',
                          'pyramid',
                          'sphere',
                          'square']

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
        self.resize(280, 520)

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
        self.populateCheck(self.settingsTab.joint_checkBox, "joint")
        self.populateCheck(self.settingsTab.uniScale_checkBox, "uniScale")
        self.populateCheck(self.settingsTab.neutralRotation_checkBox,
                           "neutralRotation")
        self.populateCheck(self.settingsTab.mirrorBehaviour_checkBox,
                           "mirrorBehaviour")
        self.settingsTab.ctlSize_doubleSpinBox.setValue(
            self.root.attr("ctlSize").get())
        sideIndex = self.iconsList.index(self.root.attr("icon").get())
        self.settingsTab.controlShape_comboBox.setCurrentIndex(sideIndex)

        self.populateCheck(self.settingsTab.tx_checkBox, "k_tx")
        self.populateCheck(self.settingsTab.ty_checkBox, "k_ty")
        self.populateCheck(self.settingsTab.tz_checkBox, "k_tz")
        self.populateCheck(self.settingsTab.rx_checkBox, "k_rx")
        self.populateCheck(self.settingsTab.ry_checkBox, "k_ry")
        self.populateCheck(self.settingsTab.rz_checkBox, "k_rz")
        self.populateCheck(self.settingsTab.ro_checkBox, "k_ro")
        self.populateCheck(self.settingsTab.sx_checkBox, "k_sx")
        self.populateCheck(self.settingsTab.sy_checkBox, "k_sy")
        self.populateCheck(self.settingsTab.sz_checkBox, "k_sz")

        self.settingsTab.ro_comboBox.setCurrentIndex(
            self.root.attr("default_rotorder").get())

        ikRefArrayItemsLR = self.root.attr("ikrefarrayLR").get().split(",")
        for item in ikRefArrayItemsLR:
            self.settingsTab.ikRefArrayLR_listWidget.addItem(item)

        ikRefArrayItemsLF = self.root.attr("ikrefarrayLF").get().split(",")
        for item in ikRefArrayItemsLF:
            self.settingsTab.ikRefArrayLF_listWidget.addItem(item)

        ikRefArrayItemsRF = self.root.attr("ikrefarrayRF").get().split(",")
        for item in ikRefArrayItemsRF:
            self.settingsTab.ikRefArrayRF_listWidget.addItem(item)

        ikRefArrayItemsRR = self.root.attr("ikrefarrayRR").get().split(",")
        for item in ikRefArrayItemsRR:
            self.settingsTab.ikRefArrayRR_listWidget.addItem(item)

        globalScaleArray = self.root.attr("globalscalearray").get().split(",")
        for item in globalScaleArray:
            self.settingsTab.globalScaleArray_listWidget.addItem(item)

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
        self.settingsTab.joint_checkBox.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.joint_checkBox,
                    "joint"))
        self.settingsTab.uniScale_checkBox.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.uniScale_checkBox,
                    "uniScale"))
        self.settingsTab.neutralRotation_checkBox.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.neutralRotation_checkBox,
                    "neutralRotation"))
        self.settingsTab.mirrorBehaviour_checkBox.stateChanged.connect(
            partial(self.updateCheck,
                    self.settingsTab.mirrorBehaviour_checkBox,
                    "mirrorBehaviour"))
        self.settingsTab.ctlSize_doubleSpinBox.valueChanged.connect(
            partial(self.updateSpinBox,
                    self.settingsTab.ctlSize_doubleSpinBox,
                    "ctlSize"))
        self.settingsTab.controlShape_comboBox.currentIndexChanged.connect(
            partial(self.updateControlShape,
                    self.settingsTab.controlShape_comboBox,
                    self.iconsList, "icon"))

        self.settingsTab.tx_checkBox.stateChanged.connect(
            partial(self.updateCheck, self.settingsTab.tx_checkBox, "k_tx"))
        self.settingsTab.ty_checkBox.stateChanged.connect(
            partial(self.updateCheck, self.settingsTab.ty_checkBox, "k_ty"))
        self.settingsTab.tz_checkBox.stateChanged.connect(
            partial(self.updateCheck, self.settingsTab.tz_checkBox, "k_tz"))
        self.settingsTab.rx_checkBox.stateChanged.connect(
            partial(self.updateCheck, self.settingsTab.rx_checkBox, "k_rx"))
        self.settingsTab.ry_checkBox.stateChanged.connect(
            partial(self.updateCheck, self.settingsTab.ry_checkBox, "k_ry"))
        self.settingsTab.rz_checkBox.stateChanged.connect(
            partial(self.updateCheck, self.settingsTab.rz_checkBox, "k_rz"))
        self.settingsTab.ro_checkBox.stateChanged.connect(
            partial(self.updateCheck, self.settingsTab.ro_checkBox, "k_ro"))
        self.settingsTab.sx_checkBox.stateChanged.connect(
            partial(self.updateCheck, self.settingsTab.sx_checkBox, "k_sx"))
        self.settingsTab.sy_checkBox.stateChanged.connect(
            partial(self.updateCheck, self.settingsTab.sy_checkBox, "k_sy"))
        self.settingsTab.sz_checkBox.stateChanged.connect(
            partial(self.updateCheck, self.settingsTab.sz_checkBox, "k_sz"))

        self.settingsTab.ro_comboBox.currentIndexChanged.connect(
            partial(self.updateComboBox,
                    self.settingsTab.ro_comboBox,
                    "default_rotorder"))

        self.mainSettingsTab.connector_comboBox.currentIndexChanged.connect(
            partial(self.updateConnector,
                    self.mainSettingsTab.connector_comboBox,
                    self.connector_items))


        self.settingsTab.ikRefArrayAddLR_pushButton.clicked.connect(
            partial(self.addItem2listWidget,
                    self.settingsTab.ikRefArrayLR_listWidget,
                    "ikrefarrayLR"))
        self.settingsTab.ikRefArrayRemoveLR_pushButton.clicked.connect(
            partial(self.removeSelectedFromListWidget,
                    self.settingsTab.ikRefArrayLR_listWidget,
                    "ikrefarrayLR"))
        self.settingsTab.ikRefArrayLR_listWidget.installEventFilter(self)


        self.settingsTab.ikRefArrayAddLF_pushButton.clicked.connect(
            partial(self.addItem2listWidget,
                    self.settingsTab.ikRefArrayLF_listWidget,
                    "ikrefarrayLF"))
        self.settingsTab.ikRefArrayRemoveLF_pushButton.clicked.connect(
            partial(self.removeSelectedFromListWidget,
                    self.settingsTab.ikRefArrayLF_listWidget,
                    "ikrefarrayLF"))
        self.settingsTab.ikRefArrayLF_listWidget.installEventFilter(self)


        self.settingsTab.ikRefArrayAddRF_pushButton.clicked.connect(
            partial(self.addItem2listWidget,
                    self.settingsTab.ikRefArrayRF_listWidget,
                    "ikrefarrayRF"))
        self.settingsTab.ikRefArrayRemoveRF_pushButton.clicked.connect(
            partial(self.removeSelectedFromListWidget,
                    self.settingsTab.ikRefArrayRF_listWidget,
                    "ikrefarrayRF"))
        self.settingsTab.ikRefArrayRF_listWidget.installEventFilter(self)


        self.settingsTab.ikRefArrayAddRR_pushButton.clicked.connect(
            partial(self.addItem2listWidget,
                    self.settingsTab.ikRefArrayRR_listWidget,
                    "ikrefarrayRR"))
        self.settingsTab.ikRefArrayRemoveRR_pushButton.clicked.connect(
            partial(self.removeSelectedFromListWidget,
                    self.settingsTab.ikRefArrayRR_listWidget,
                    "ikrefarrayRR"))
        self.settingsTab.ikRefArrayRR_listWidget.installEventFilter(self)


        self.settingsTab.globalArrayAdd_pushButton.clicked.connect(
            partial(self.addItem2listWidget,
                    self.settingsTab.globalScaleArray_listWidget,
                    "globalscalearray"))
        self.settingsTab.globalArrayRemove_pushButton.clicked.connect(
            partial(self.removeSelectedFromListWidget,
                    self.settingsTab.globalScaleArray_listWidget,
                    "globalscalearray"))
        self.settingsTab.globalScaleArray_listWidget.installEventFilter(self)



    def eventFilter(self, sender, event):
        if event.type() == QtCore.QEvent.ChildRemoved:
            if sender == self.settingsTab.ikRefArray_listWidget:
                self.updateListAttr(sender, "ikrefarray")
            return True
        else:
            return QtWidgets.QDialog.eventFilter(self, sender, event)

    def dockCloseEventTriggered(self):
        pyqt.deleteInstances(self, MayaQDockWidget)
