"""Component Chassis 01 module"""

import pymel.core as pm
from mgear.shifter import component
from mgear.core import attribute, transform, primitive, node, constraints


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
        self.setup = primitive.addTransformFromPos(
            self.setupWS, self.getName("WS"))
        attribute.lockAttribute(self.setup)

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

        self.ctl = self.addCtl(self.ik_cns,
                               "ctl",
                               t,
                               self.color_ik,
                               self.settings["icon"],
                               w=self.settings["ctlSize"] * self.size,
                               h=self.settings["ctlSize"] * self.size,
                               d=self.settings["ctlSize"] * self.size,
                               tp=self.parentCtlTag)

        t = transform.setMatrixPosition(t, self.guide.pos["0_loc"])
        self.lr_ik_cns = primitive.addTransform(
            self.root, self.getName("lr_ik_cns"), t)
        
        self.lr_ctl = self.addCtl(self.lr_ik_cns,
                               "lrctl",
                               t,
                               self.color_ik,
                               self.settings["icon"],
                               w=self.settings["ctlSize"] * self.size,
                               h=self.settings["ctlSize"] * self.size,
                               d=self.settings["ctlSize"] * self.size,
                               tp=self.parentCtlTag)

        t = transform.setMatrixPosition(t, self.guide.pos["1_loc"])
        self.lf_ik_cns = primitive.addTransform(
            self.root, self.getName("lf_ik_cns"), t)

        self.lf_ctl = self.addCtl(self.lf_ik_cns,
                               "lfctl",
                               t,
                               self.color_ik,
                               self.settings["icon"],
                               w=self.settings["ctlSize"] * self.size,
                               h=self.settings["ctlSize"] * self.size,
                               d=self.settings["ctlSize"] * self.size,
                               tp=self.parentCtlTag)

        t = transform.setMatrixPosition(t, self.guide.pos["2_loc"])
        self.rf_ik_cns = primitive.addTransform(
            self.root, self.getName("rf_ik_cns"), t)

        self.rf_ctl = self.addCtl(self.rf_ik_cns,
                               "rfctl",
                               t,
                               self.color_ik,
                               self.settings["icon"],
                               w=self.settings["ctlSize"] * self.size,
                               h=self.settings["ctlSize"] * self.size,
                               d=self.settings["ctlSize"] * self.size,
                               tp=self.parentCtlTag)

        t = transform.setMatrixPosition(t, self.guide.pos["3_loc"])
        self.rr_ik_cns = primitive.addTransform(
            self.root, self.getName("rr_ik_cns"), t)

        self.rr_ctl = self.addCtl(self.rr_ik_cns,
                               "rrctl",
                               t,
                               self.color_ik,
                               self.settings["icon"],
                               w=self.settings["ctlSize"] * self.size,
                               h=self.settings["ctlSize"] * self.size,
                               d=self.settings["ctlSize"] * self.size,
                               tp=self.parentCtlTag)
 
        # we need to set the rotation order before lock any rotation axis
        if self.settings["k_ro"]:
            rotOderList = ["XYZ", "YZX", "ZXY", "XZY", "YXZ", "ZYX"]
            attribute.setRotOrder(
                self.ctl, rotOderList[self.settings["default_rotorder"]])

        params = [s for s in
                  ["tx", "ty", "tz", "ro", "rx", "ry", "rz", "sx", "sy", "sz"]
                  if self.settings["k_" + s]]
        attribute.setKeyableAttributes(self.ctl, params)

        if self.settings["joint"]:
            self.jnt_pos.append([self.ctl, 0, None, self.settings["uniScale"]])


        # Nurbs plane
        nurbP = pm.nurbsPlane(n=self.getName("srf"),p=[0,0,0], ax=[0,1,0], 
                                w=1, lr=1, d=1, u=1, v=1, ch=0)[0]
        pm.parent(nurbP, self.setup)
        pm.setAttr(nurbP+'.v', 0)
        attribute.lockAttribute(nurbP)
        for ctl, port in zip((self.rf_ctl, self.rr_ctl, self.lf_ctl, self.lr_ctl), (0,1,2,3)):
            dcmp = node.createDecomposeMatrixNode(ctl.worldMatrix[0])
            pm.connectAttr(dcmp+'.outputTranslate', nurbP+'.controlPoints[{}]'.format(port))
        
        # Chassis root srf constraint
        t = transform.setMatrixPosition(t, self.guide.pos["root"])
        self.srfTra = primitive.addTransform(self.setup, self.getName("srf_cns"), t)
        self.fol    = constraints.constToSrfFol(self.srfTra, nurbP,
                        name=self.getName("fol"), mo=False)
        pm.parent(self.fol, self.setup)
        pm.parentConstraint(self.srfTra, self.ik_cns, mo=True)


    def addAttributes(self):
        # Ref
        if self.settings["ikrefarrayLR"]:
            ref_names = self.get_valid_alias_list(
                self.settings["ikrefarrayLR"].split(","))
            if len(ref_names) > 1:
                self.ikref_att_lr = self.addAnimEnumParam(
                    "ikreflr",
                    "Ik Ref LR",
                    0,
                    ref_names)

        if self.settings["ikrefarrayLF"]:
            ref_names = self.get_valid_alias_list(
                self.settings["ikrefarrayLF"].split(","))
            if len(ref_names) > 1:
                self.ikref_att_lf = self.addAnimEnumParam(
                    "ikreflf",
                    "Ik Ref LF",
                    0,
                    ref_names)

        if self.settings["ikrefarrayRF"]:
            ref_names = self.get_valid_alias_list(
                self.settings["ikrefarrayRF"].split(","))
            if len(ref_names) > 1:
                self.ikref_att_rf = self.addAnimEnumParam(
                    "ikrefrf",
                    "Ik Ref RF",
                    0,
                    ref_names)

        if self.settings["ikrefarrayRR"]:
            ref_names = self.get_valid_alias_list(
                self.settings["ikrefarrayRR"].split(","))
            if len(ref_names) > 1:
                self.ikref_att_rr = self.addAnimEnumParam(
                    "ikrefrr",
                    "Ik Ref RR",
                    0,
                    ref_names)

        if self.settings["globalscalearray"]:
            ref_names = self.get_valid_alias_list(self.settings["globalscalearray"].split(","))
            if pm.attributeQuery("globalScale", node=ref_names[0], ex=True):
                self.global_att = ref_names[0]+'.globalScale'
                [pm.connectAttr(self.global_att, self.fol[0]+attr) for attr in [".sx",".sy",".sz"]]

    def addOperators(self):
        return

    # =====================================================
    # CONNECTOR
    # =====================================================
    def setRelation(self):
        """Set the relation between object from guide to rig"""
        self.relatives["root"] = self.root

    def addConnection(self):
        """Add more connection definition to the set"""
        self.connections["standard"] = self.connect_standard
        self.connections["orientation"] = self.connect_orientation

    def connect_standard(self):
        """standard connection definition for the component"""
        self.connectRef(self.settings["ikrefarrayLR"], self.lr_ik_cns)
        self.connectRef(self.settings["ikrefarrayLF"], self.lf_ik_cns)
        self.connectRef(self.settings["ikrefarrayRF"], self.rf_ik_cns)
        self.connectRef(self.settings["ikrefarrayRR"], self.rr_ik_cns)
        self.parent.addChild(self.root) # parent chassis root

    def connect_orientation(self):
        """Orient connection definition for the component"""
        self.connect_orientCns()