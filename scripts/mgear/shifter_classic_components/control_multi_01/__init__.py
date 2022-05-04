"""Component Control Multi 01 module"""

from mgear.shifter import component

from mgear.core import attribute, transform, primitive

import maya.cmds as cmds


#############################################
# COMPONENT
#############################################


class Component(component.Main):
    """Shifter component Class"""

    # =====================================================
    # OBJECTS
    # =====================================================
    def addObjects(self):
        """Add all the objects needed to create the component."""

        if self.settings["neutralRotation"]:
            t = transform.getTransformFromPos(self.guide.pos["root"])
        else:
            t = self.guide.tra["root"]
            if self.settings["mirrorBehaviour"] and self.negate:
                scl = [1, 1, -1]
            else:
                scl = [1, 1, 1]
            t = transform.setMatrixScale(t, scl)

        self.ik_cns = primitive.addTransform(
            self.root, self.getName("ik_cns"), t)
        self.npo = []
        self.ctl = []
        if self.settings["numofctl"] > 0:
            for num in range(self.settings["numofctl"]):
                npo = primitive.addTransform(self.ik_cns, self.getName("%s_npo" % num), t)
                ctl = self.addCtl(npo,
                                  "%s_ctl" % num,
                                  t,
                                  self.color_ik,
                                  self.settings["icon"],
                                  w=self.settings["ctlSize"] * self.size/(num+1),
                                  h=self.settings["ctlSize"] * self.size/(num+1),
                                  d=self.settings["ctlSize"] * self.size/(num+1),
                                  tp=self.parentCtlTag)
                self.npo.append(npo)
                self.ctl.append(ctl)
        else:
            ctl = self.addCtl(self.ik_cns,
                              "ctl",
                              t,
                              self.color_ik,
                              self.settings["icon"],
                              w=self.settings["ctlSize"] * self.size,
                              h=self.settings["ctlSize"] * self.size,
                              d=self.settings["ctlSize"] * self.size,
                              tp=self.parentCtlTag)
            self.ctl.append(ctl)

        if len(self.npo) > 1:
            for i in range(0, len(self.npo) - 1):
                parent = self.ctl[i]
                child = self.npo[i+1]
                child.setParent(parent)

        # we need to set the rotation order before lock any rotation axis
        if self.settings["k_ro"]:
            rotOderList = ["XYZ", "YZX", "ZXY", "XZY", "YXZ", "ZYX"]
            for ctl in self.ctl:
                #attribute.setRotOrder(self.ctl, rotOderList[self.settings["default_rotorder"]])
                attribute.setRotOrder(
                    ctl, rotOderList[self.settings["default_rotorder"]])

        params = [s for s in
                  ["tx", "ty", "tz", "ro", "rx", "ry", "rz", "sx", "sy", "sz"]
                  if self.settings["k_" + s]]
        for ctl in self.ctl:
            #attribute.setKeyableAttributes(self.ctl, params)
            attribute.setKeyableAttributes(ctl, params)

        if self.settings["joint"]:
            #self.jnt_pos.append([self.ctl, 0, None, self.settings["uniScale"]])
            #self.jnt_pos.append([self.ctl[-1], 0, None, self.settings["uniScale"]])
            for num, ctl in enumerate(self.ctl):
                self.jnt_pos.append([ctl, num, None, self.settings["uniScale"]])
        '''
        if self.settings["joint_per_ctl"]:
            #self.jnt_pos.append([self.ctl, 0, None, self.settings["uniScale"]])
            for num, ctl in enumerate(self.ctl):
                self.jnt_pos.append([ctl, num, None, self.settings["uniScale"]])
        '''

    def addAttributes(self):
        # Ref
        if self.settings["ikrefarray"]:
            ref_names = self.get_valid_alias_list(
                self.settings["ikrefarray"].split(","))
            if len(ref_names) > 1:
                self.ikref_att = self.addAnimEnumParam(
                    "ikref",
                    "Ik Ref",
                    0,
                    ref_names)

    def addOperators(self):
        return

    # =====================================================
    # CONNECTOR
    # =====================================================
    def setRelation(self):
        """Set the relation beetween object from guide to rig"""
        self.relatives["root"] = self.ctl
        self.controlRelatives["root"] = self.ctl
        if self.settings["joint"]:
            self.jointRelatives["root"] = 0
        self.aliasRelatives["root"] = "ctl"

    def addConnection(self):
        """Add more connection definition to the set"""
        self.connections["standard"] = self.connect_standard
        self.connections["orientation"] = self.connect_orientation

    def connect_standard(self):
        """standard connection definition for the component"""
        self.connect_standardWithSimpleIkRef()

    def connect_orientation(self):
        """Orient connection definition for the component"""
        self.connect_orientCns()
