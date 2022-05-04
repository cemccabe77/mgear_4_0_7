"""Component Eye 01 module"""
import maya.cmds as cmds
from pymel.core import datatypes

from mgear.shifter import component

from mgear.core import attribute, transform, primitive, applyop

from collections import OrderedDict


##########################################################
# COMPONENT
##########################################################


class Component(component.Main):
    """Shifter component Class"""

    # =====================================================
    # OBJECTS
    # =====================================================
    def addObjects(self):
        """Add all the objects needed to create the component."""

        t = transform.getTransformFromPos(self.guide.pos["root"])
        lashTop_t = transform.getTransformFromPos(self.guide.pos["lashTop"])
        lashBot_t = transform.getTransformFromPos(self.guide.pos["lashBot"])
        self.controls = []

        self.eye_npo = primitive.addTransform(self.root,
                                              self.getName("eye_npo"),
                                              t)

        self.lashTop_npo = primitive.addTransform(self.root,
                                              self.getName("lashTop_npo"),
                                              lashTop_t)

        self.lashBot_npo = primitive.addTransform(self.root,
                                              self.getName("lashBot_npo"),
                                              lashBot_t)

        self.eyeFK_ctl = self.addCtl(self.eye_npo,
                                     "fk_ctl",
                                     t,
                                     self.color_fk,
                                     "arrow",
                                     w=1 * self.size,
                                     tp=self.eye_npo)

        self.lashTop_ctl = self.addCtl(self.lashTop_npo,
                                     "lashTop_ctl",
                                     lashTop_t,
                                     self.color_fk,
                                     "diamond",
                                     w=0.2 * self.size,
                                     tp=self.lashTop_npo)

        attribute.lockAttribute(self.lashTop_ctl, 
                                attributes=["tx","tz",
                                "rx", "ry", "rz",
                                "sx", "sy", "sz",
                                "v"])

        self.lashBot_ctl = self.addCtl(self.lashBot_npo,
                                     "lashBot_ctl",
                                     lashBot_t,
                                     self.color_fk,
                                     "diamond",
                                     w=0.2 * self.size,
                                     tp=self.lashBot_npo)

        attribute.lockAttribute(self.lashBot_ctl, 
                                attributes=["tx","tz",
                                "rx", "ry", "rz",
                                "sx", "sy", "sz",
                                "v"])

        # look at
        t = transform.getTransformFromPos(self.guide.pos["look"])
        self.ik_cns = primitive.addTransform(
            self.root, self.getName("ik_cns"), t)

        self.eyeIK_npo = primitive.addTransform(
            self.ik_cns, self.getName("ik_npo"), t)

        self.eyeIK_ctl = self.addCtl(self.eyeIK_npo,
                                     "ik_ctl",
                                     t,
                                     self.color_fk,
                                     "circle",
                                     w=.5 * self.size,
                                     tp=self.eyeFK_ctl,
                                     ro=datatypes.Vector([1.5708, 0, 0]))
        attribute.setKeyableAttributes(self.eyeIK_ctl, self.t_params)

        self.jnt_pos.append([self.eyeFK_ctl, "eye", "parent_relative_jnt"])

        self.controls.append(self.lashTop_ctl)
        self.controls.append(self.lashBot_ctl)

        for control in self.controls:    
            transformNode = cmds.createNode('transform', name=control.replace('ctl', 'Rev'), 
                parent=str(self.eye_npo), skipSelect=True)
            position = cmds.xform(str(self.eye_npo), query=1, translation=1, worldSpace=1)
            cmds.xform(transformNode, translation=position, worldSpace=1)
            if not cmds.objExists('%s_revNde' % transformNode):
              #floatMath node
              # reversNode = cmds.createNode('floatMath', name='%s_revNde' % transformNode, skipSelect=True)
              # cmds.setAttr('%s.operation' % reversNode, 3) #divide
              # cmds.setAttr('%s.floatB' % reversNode, -1)
              # cmds.connectAttr('%s.ty' % control, '%s.floatA' %reversNode)
              # cmds.connectAttr('%s.outFloat' % reversNode, '%s.ty' % transformNode)

              # MultiplyDivide node
              reversNode = cmds.createNode('multiplyDivide', name='%s_revNde' % transformNode, ss=True)
              cmds.setAttr('%s.operation' % reversNode, 2) #divide
              cmds.setAttr('%s.input2X' % reversNode, -1)
              cmds.connectAttr('%s.ty' % control, '%s.input1X' %reversNode)
              cmds.connectAttr('%s.outputX' % reversNode, '%s.ty' % transformNode)

    # =====================================================
    # ATTRIBUTES
    # =====================================================
    def addAttributes(self):
        """Create the anim and setupr rig attributes for the component"""

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

    # =====================================================
    # OPERATORS
    # =====================================================
    def addOperators(self):
        """Create operators and set the relations for the component rig

        Apply operators, constraints, expressions to the hierarchy.
        In order to keep the code clean and easier to debug,
        we shouldn't create any new object in this method.

        """

        upvDir = self.settings["upVectorDirection"]
        if upvDir == 0:
            upvVec = [1, 0, 0]
        elif upvDir == 1:
            upvVec = [0, 1, 0]
        else:
            upvVec = [0, 0, 1]

        applyop.aimCns(
            self.eye_npo, self.eyeIK_ctl, "zy", 2, upvVec, self.root, False)

    # =====================================================
    # CONNECTOR
    # =====================================================
    def setRelation(self):
        """Set the relation beetween object from guide to rig"""
        self.relatives["root"] = self.eyeFK_ctl
        self.controlRelatives["root"] = self.eyeFK_ctl

        self.jointRelatives["root"] = 0
        self.jointRelatives["look"] = 1

        self.aliasRelatives["root"] = "eye"

    def connect_standard(self):
        """standard connection definition for the component"""
        self.connect_standardWithSimpleIkRef()
