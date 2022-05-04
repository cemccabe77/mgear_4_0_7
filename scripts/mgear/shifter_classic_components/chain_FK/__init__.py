"""Component Chain FK module"""

import pymel.core as pm
from pymel.core import datatypes

from mgear.shifter import component

from mgear.core import node, applyop, vector
from mgear.core import attribute, transform, primitive

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

        self.normal = self.guide.blades["blade"].z * -1
        self.binormal = self.guide.blades["blade"].x

        self.isFk = self.settings["mode"] != 1
        self.isIk = self.settings["mode"] != 0
        self.isFkIk = self.settings["mode"] == 2

        self.WIP = self.options["mode"]

        # FK controllers ------------------------------------
        if self.isFk:
            self.fk_npo = []
            self.fk_ctl = []
            self.fk_ref = []
            self.fk_off = []
            t = self.guide.tra["root"]
            self.ik_cns = primitive.addTransform(
                self.root, self.getName("ik_cns"), t)
            parent = self.ik_cns
            tOld = False
            fk_ctl = None
            self.previusTag = self.parentCtlTag
            for i, t in enumerate(transform.getChainTransform(self.guide.apos,
                                                              self.normal,
                                                              self.negate)):
                dist = vector.getDistance(self.guide.apos[i],
                                          self.guide.apos[i + 1])
                if self.settings["neutralpose"] or not tOld:
                    tnpo = t
                else:
                    tnpo = transform.setMatrixPosition(
                        tOld,
                        transform.getPositionFromMatrix(t))
                if i:
                    tref = transform.setMatrixPosition(
                        tOld,
                        transform.getPositionFromMatrix(t))
                    fk_ref = primitive.addTransform(
                        fk_ctl,
                        self.getName("fk%s_ref" % i),
                        tref)
                    self.fk_ref.append(fk_ref)
                else:
                    tref = t
                fk_off = primitive.addTransform(
                    parent, self.getName("fk%s_off" % i), tref)
                fk_npo = primitive.addTransform(
                    fk_off, self.getName("fk%s_npo" % i), tnpo)
                fk_ctl = self.addCtl(
                    fk_npo,
                    "fk%s_ctl" % i,
                    t,
                    self.color_fk,
                    "cube",
                    w=dist,
                    h=self.size * .1,
                    d=self.size * .1,
                    po=datatypes.Vector(dist * .5 * self.n_factor, 0, 0),
                    tp=self.previusTag)

                self.fk_off.append(fk_off)
                self.fk_npo.append(fk_npo)
                self.fk_ctl.append(fk_ctl)
                tOld = t
                self.previusTag = fk_ctl

            # Chain
            self.chain = primitive.add2DChain(self.root,
                                              self.getName("chain"),
                                              self.guide.apos,
                                              self.normal,
                                              self.negate)
            self.chain[0].attr("visibility").set(self.WIP)

        # Chain of deformers -------------------------------
        self.loc = []
        parent = self.root
        for i, t in enumerate(transform.getChainTransform(self.guide.apos,
                                                          self.normal,
                                                          self.negate)):
            loc = primitive.addTransform(parent, self.getName("%s_loc" % i), t)

            self.loc.append(loc)
            self.jnt_pos.append([loc, i, None, False])

    # =====================================================
    # ATTRIBUTES
    # =====================================================
    def addAttributes(self):
        """Create the anim and setup rig attributes for the component"""
        pass

    # =====================================================
    # OPERATORS
    # =====================================================
    def addOperators(self):
        """Create operators and set the relations for the component rig

        Apply operators, constraints, expressions to the hierarchy.
        In order to keep the code clean and easier to debug,
        we shouldn't create any new object in this method.

        """

        # FK Chain -----------------------------------------
        if self.isFk:
            for off, ref in zip(self.fk_off[1:], self.fk_ref):
                applyop.gear_mulmatrix_op(
                    ref.worldMatrix, off.parentInverseMatrix, off, "rt")


        # Chain of deformers -------------------------------
        for i, loc in enumerate(self.loc):

            if self.settings["mode"] == 0:  # fk only
                pm.parentConstraint(self.fk_ctl[i], loc, maintainOffset=False)
                pm.connectAttr(self.fk_ctl[i] + ".scale", loc + ".scale")

            elif self.settings["mode"] == 1:  # ik only
                pm.parentConstraint(self.chain[i], loc, maintainOffset=False)

            elif self.settings["mode"] == 2:  # fk/ik

                rev_node = node.createReverseNode(self.blend_att)

                # orientation
                cns = pm.parentConstraint(
                    self.fk_ctl[i], self.chain[i], loc, maintainOffset=False)
                cns.interpType.set(0)
                weight_att = pm.parentConstraint(
                    cns, query=True, weightAliasList=True)
                pm.connectAttr(rev_node + ".outputX", weight_att[0])
                pm.connectAttr(self.blend_att, weight_att[1])

                # scaling
                blend_node = pm.createNode("blendColors")
                pm.connectAttr(self.chain[i].attr("scale"),
                               blend_node + ".color1")
                pm.connectAttr(self.fk_ctl[i].attr("scale"),
                               blend_node + ".color2")
                pm.connectAttr(self.blend_att, blend_node + ".blender")
                pm.connectAttr(blend_node + ".output", loc + ".scale")

    # =====================================================
    # CONNECTOR
    # =====================================================
    def setRelation(self):
        """Set the relation beetween object from guide to rig"""

        self.relatives["root"] = self.loc[0]
        self.jointRelatives["root"] = 0

        if not self.isIk:
            self.controlRelatives["root"] = self.fk_ctl[0]
            self.controlRelatives["%s_loc" % (len(self.loc) - 1)] = self.fk_ctl[-1]
        else:
            self.controlRelatives["root"] = self.ik_ctl
            self.controlRelatives["%s_loc" % (len(self.loc) - 1)] = self.ik_ctl

        for i in range(0, len(self.loc) - 1):
            self.relatives["%s_loc" % i] = self.loc[i + 1]
            self.jointRelatives["%s_loc" % i] = i + 1
            self.aliasRelatives["%s_ctl" % i] = i + 1
            if not self.isIk:
                self.controlRelatives["%s_loc" % i] = self.fk_ctl[i + 1]
            else:
                self.controlRelatives["%s_loc" % i] = self.ik_ctl

        self.relatives["%s_loc" % (len(self.loc) - 1)] = self.loc[-1]
        self.jointRelatives["%s_loc" % (len(self.loc) - 1)] = len(self.loc) - 1
        self.aliasRelatives["%s_loc" % (len(self.loc) - 1)] = len(self.loc) - 1

    # @param self
    def addConnection(self):
        """Add more connection definition to the set"""

        self.connections["standard"] = self.connect_standard
        self.connections["orientation"] = self.connect_orientation
        self.connections["parent"] = self.connect_parent

    def connect_orientation(self):
        """orientation connection definition for the component"""
        self.connect_orientCns()

    def connect_standard(self):
        """standard connection definition for the component"""
        self.connect_standardWithSimpleIkRef()

    def connect_parent(self):
        self.connect_standardWithSimpleIkRef()
