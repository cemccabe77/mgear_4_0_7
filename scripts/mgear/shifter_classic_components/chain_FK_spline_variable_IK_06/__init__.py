"""Component chain FK spline 06 module"""

import pymel.core as pm
from pymel.core import datatypes

from mgear.shifter import component

from mgear.core import transform, primitive, vector, curve, applyop, dag
from mgear.core import attribute, node, icon

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
        self.setup = primitive.addTransformFromPos(
            self.setupWS, self.getName("WS"))

        self.splineGrp = primitive.addTransformFromPos(
            self.setup, self.getName("ikSpline"))

        self.normal = self.guide.blades["blade"].y
        self.binormal = self.guide.blades["blade"].x

        self.WIP = self.options["mode"]

        if self.negate and self.settings["overrideNegate"]:
            self.negate = False
            self.n_factor = 1

        if self.settings["overrideNegate"]:
            self.mirror_conf = [0, 0, 1,
                                1, 1, 0,
                                0, 0, 0]
        else:
            self.mirror_conf = [0, 0, 0,
                                0, 0, 0,
                                0, 0, 0]

        # FK controllers ------------------------------------
        self.fk_npo = []
        self.fk_ctl = []
        self.ik_ctl = []
        self.upv_curv_lvl = []
        t = self.guide.tra["root"]

        parent = self.root
        tOld = False
        fk_ctl = None
        self.previusTag = self.parentCtlTag
        for i, t in enumerate(transform.getChainTransform(self.guide.apos,
                                                          self.normal,
                                                          self.negate)):
            self.dist = vector.getDistance(self.guide.apos[i],
                                           self.guide.apos[i + 1])
            if self.settings["neutralpose"] or not tOld:
                tnpo = t
            else:
                tnpo = transform.setMatrixPosition(
                    tOld,
                    transform.getPositionFromMatrix(t))

            fk_npo = primitive.addTransform(
                parent, self.getName("fk%s_npo" % i), tnpo)
            
            fk_ctl = self.addCtl(
                fk_npo,
                "fk%s_ctl" % i,
                t,
                self.color_fk,
                "cube",
                w=self.dist,
                h=self.size * .1,
                d=self.size * .1,
                po=datatypes.Vector(self.dist * .5 * self.n_factor, 0, 0),
                tp=self.previusTag,
                mirrorConf=self.mirror_conf)

            upv_curv_lvl = primitive.addTransform(
                fk_ctl, self.getName("upv%s_lvl" % i), t)
            upv_curv_lvl.attr("ty").set(.2)
            
            self.fk_npo.append(fk_npo)
            self.fk_ctl.append(fk_ctl)
            self.upv_curv_lvl.append(upv_curv_lvl)
            tOld = t
            self.previusTag = fk_ctl
            parent = fk_ctl

        # add FK end anchor
        fkEnd_lvl = primitive.addTransform(
            fk_ctl, self.getName("fkEnd_lvl"), t)

        upv_curv_lvl = primitive.addTransform(
            fkEnd_lvl, self.getName("upvFkEnd_lvl"), t)
        upv_curv_lvl.attr("ty").set(.2)

        self.fk_ctl_crv_points = self.fk_ctl + [fkEnd_lvl]
        self.upv_curv_lvl.append(upv_curv_lvl)

        if self.negate:
            self.off_dist = self.dist * -1
        else:
            self.off_dist = self.dist
        fkEnd_lvl.attr("tx").set(self.off_dist)

        # IK controls
        tagP = self.parentCtlTag
        self.ik_upv_cns = []
        self.ik_npo_cns = []
        self.ik_sps_cns = [] # added ik ref space switch transform
        self.ik_upv_lvl = []
        # self.ik_upvr_lvl = [] #cm reverseCurve
        self.ik_number = self.settings["ikNb"]
        for i in range(self.ik_number):
            # References
            ik_npo_cns = primitive.addTransform(self.root,
                                                self.getName("ik%s_cns" % i))

            pm.setAttr(ik_npo_cns + ".inheritsTransform", False)
            self.ik_npo_cns.append(ik_npo_cns)

            ik_upv_cns = primitive.addTransform(self.root,
                                                self.getName("ik%s_upv" % i))

            pm.setAttr(ik_upv_cns + ".inheritsTransform", False)
            self.ik_upv_cns.append(ik_upv_cns)

            t = transform.getTransform(ik_npo_cns)

            
            #cm
            # Create space switch transform
            ik_sps_cns = primitive.addTransform(ik_npo_cns,
                                                self.getName("ik%s_sps" % i), t)
            self.ik_sps_cns.append(ik_sps_cns)



            ik_ctl = self.addCtl(
                ik_sps_cns,
                "ik%s_ctl" % i,
                t,
                self.color_ik,
                "square",
                w=self.size * .15,
                h=self.size * .15,
                d=self.size * .15,
                ro=datatypes.Vector([0, 0, 1.5708]),
                tp=tagP,
                mirrorConf=self.mirror_conf)

            attribute.setKeyableAttributes(ik_ctl)

            tagP = ik_ctl
            self.ik_ctl.append(ik_ctl)

            ik_upv_lvl = primitive.addTransform(
                ik_ctl, self.getName("ik%s_lvl" % i), t)
            ik_upv_lvl.attr("ty").set(.2)
            self.ik_upv_lvl.append(ik_upv_lvl)

            # #cm reverseCurve
            # ik_upvr_lvl = primitive.addTransform(
            #     ik_ctl, self.getName("ik%s_lvl" % i), t)
            # ik_upvr_lvl.attr("ty").set(-.2)
            # self.ik_upvr_lvl.append(ik_upvr_lvl)

        # add length offset control if keep length
        # This option will be added only if keep length is active
        if self.settings["keepLength"]:
            self.ikTip_npo = primitive.addTransform(
                ik_ctl, self.getName("ikTip_npo"), t)
            ik_ctl = self.addCtl(
                self.ikTip_npo,
                "ikTip_ctl",
                t,
                self.color_fk,
                "square",
                w=self.size * .1,
                h=self.size * .1,
                d=self.size * .1,
                ro=datatypes.Vector([0, 0, 1.5708]),
                tp=tagP,
                mirrorConf=self.mirror_conf)

            ik_upv_lvl = primitive.addTransform(
                ik_ctl, self.getName("ikTip_lvl"), t)
            ik_upv_lvl.attr("ty").set(.2)

            # cm
            for shp in ik_ctl.getShapes():
                pm.delete(shp)

            # #cm reverseCurve
            # ik_upvr_lvl = primitive.addTransform(
            #     ik_ctl, self.getName("ikTipr_lvl"), t)
            # ik_upvr_lvl.attr("ty").set(-.2)
            # self.ik_upvr_lvl.append(ik_upvr_lvl)

            # move to align with the parent
            # we will offset later, so we cheat the space for keep length
            self.ikTip_npo.attr("tx").set(0)

            self.ik_ctl.append(ik_ctl)
            self.ik_upv_lvl.append(ik_upv_lvl)

            # add visual reference
            # self.line_ref = icon.connection_display_curve(
            #     self.getName("visualRef"),
            #     [self.ikTip_npo.getParent(), ik_ctl])

        # set keyable attr for tweak controls
        [attribute.setKeyableAttributes(i_ctl, ["tx","ty","tz","rx","ry","rz"])
            for i_ctl in self.ik_ctl]



        # Curves -------------------------------------------
        self.mst_crv = curve.addCnsCurve(self.root,
                                         self.getName("mst_crv"),
                                         self.fk_ctl_crv_points,
                                         3)

        self.upv_crv = curve.addCnsCurve(self.root,
                                         self.getName("upv_crv"),
                                         self.upv_curv_lvl,
                                         3)

        self.mst_crv.setAttr("visibility", False)
        self.upv_crv.setAttr("visibility", False)

        self.mstIK_crv = curve.addCnsCurve(self.root,
                                           self.getName("mstIK_crv"),
                                           self.ik_ctl[:-1],
                                           3)

        self.upvIK_crv = curve.addCnsCurve(self.root,
                                           self.getName("upvIK_crv"),
                                           self.ik_upv_lvl[:-1],
                                           3)
        # #cm reverseCurve
        # self.upvIKr_crv = curve.addCnsCurve(self.root,
        #                                    self.getName("upvIKr_crv"),
        #                                    self.ik_upvr_lvl,
        #                                    3)

        #cm
        self.sldIK_crv = curve.addCurve(self.root,
                         self.getName("sldIK_crv"),
                         [datatypes.Vector()] *len(self.ik_ctl)*5,
                         close=False,
                         degree=3)
        self.sldUV_crv = curve.addCurve(self.root,
                         self.getName("sldUV_crv"),
                         [datatypes.Vector()] *len(self.ik_upv_lvl)*5,
                         close=False,
                         degree=3)

        self.sldIK_crv.setAttr("overrideEnabled", 1)
        self.sldIK_crv.setAttr("overrideDisplayType", 1)

        self.mstIK_crv.setAttr("visibility", False)
        self.upvIK_crv.setAttr("visibility", False)
        self.sldUV_crv.setAttr("visibility", False)


        # Divisions
        self.div_cns = []
        self.upv_cns = []

        if self.settings["overrideJntNb"]:
            self.def_number = self.settings["jntNb"]
        else:
            self.def_number = len(self.guide.apos)


        for i in range(self.def_number):
            # References
            div_cns = primitive.addTransform(self.root,
                                             self.getName("%s_cns" % i))

            pm.setAttr(div_cns + ".inheritsTransform", False)
            self.div_cns.append(div_cns)

            upv_cns = primitive.addTransform(self.root,
                                             self.getName("%s_upv" % i))

            pm.setAttr(upv_cns + ".inheritsTransform", False)
            self.upv_cns.append(upv_cns)
            
            # self.jnt_pos.append([div_cns, i])
        



    # =====================================================
    # ATTRIBUTES
    # =====================================================
    def addAttributes(self):
        #cm, ik space switching
        self.ikref_lst = [] # creat a [list of [list]] of IK space switch from UI Host, for each IK ctl
        for i,cns in enumerate(self.ik_sps_cns):
            if self.settings["ikrefarray"]:
                # Make list of all items added to IK Ref Widget in component PPG
                ref_names = self.get_valid_alias_list(
                    self.settings["ikrefarray"].split(","))
                # append sps parent to add as space option
                ref_names.insert(0, str(self.ik_npo_cns[i]))

                if len(ref_names) > 1: # Create entries into space switch attr
                    ikref_att = self.addAnimEnumParam(
                        "ikref%s" % i,
                        "Ik Ref%s" % i,
                        0,
                        ref_names)
                    self.ikref_lst.append(ikref_att)

        """Create the anim and setup rig attributes for the component"""
        self.ikVis_att = self.addAnimParam("IK_vis",
                                           "IK vis",
                                           "bool",
                                           True)

        self.fkVis_att = self.addAnimParam("FK_vis",
                                           "FK vis",
                                           "bool",
                                           True)
        self.lengM_att = self.addAnimParam("Maintain_length",
                                           "Maintain length",
                                           "bool",
                                           True)

        self.maxStretch_att = self.addAnimParam("maxPathStretch",
                                           "Max path stretch",
                                           "double",
                                           10,
                                           0,
                                           99)
        self.maxSquash_att = self.addAnimParam("maxPathSquash",
                                           "Max path squash",
                                           "double",
                                           0,
                                           0,
                                           1)
        self.softness_att = self.addAnimParam("softness",
                                           "Softness",
                                           "double",
                                           0,
                                           0,
                                           1)

        if self.settings["keepLength"]:
            self.length_ratio_att = self.addAnimParam("jnt_length_ratio",
                                                      "Jnt Length Ratio",
                                                      "double",
                                                      10,
                                                      0.0001,
                                                      99)
        self.position_att = self.addAnimParam("jnt_position",
                                           "Jnt Position",
                                           "double",
                                           0,
                                           0,
                                           1)
        if self.settings["twist"]:
            self.twist_att = self.addAnimParam("Twist",
                                               "Twist",
                                               "bool",
                                               False)


    # =====================================================
    # OPERATORS
    # =====================================================
    def addOperators(self):
        """Create operators and set the relations for the component rig

        Apply operators, constraints, expressions to the hierarchy.
        In order to keep the code clean and easier to debug,
        we shouldn't create any new object in this method.

        """

        dm_node_scl = node.createDecomposeMatrixNode(self.root.worldMatrix)

        # IK controls
        if self.ik_number > 1:
            div_val = self.ik_number - 1
        else:
            div_val = 1
        step = 0.998 / div_val
        u = 0.001

        
        for i in range(self.ik_number):
            cnsUpv = applyop.pathCns(self.ik_upv_cns[i],
                                     self.upv_crv,
                                     cnsType=False,
                                     u=u,
                                     tangent=False)
            
            cns = applyop.pathCns(
                self.ik_npo_cns[i], self.mst_crv, False, u, True)

            # Connecting the scale for scaling compensation
            for axis, AX in zip("xyz", "XYZ"):
                pm.connectAttr(dm_node_scl.attr("outputScale{}".format(AX)),
                               self.ik_npo_cns[i].attr("s{}".format(axis)))

            cns.setAttr("worldUpType", 1)
            cns.setAttr("frontAxis", 0)
            cns.setAttr("upAxis", 1)

            pm.connectAttr(self.ik_upv_cns[i].attr("worldMatrix[0]"),
                           cns.attr("worldUpMatrix"))
            u += step

        # Divisions
        if self.settings["keepLength"]:
            arclen_node = pm.arclen(self.mstIK_crv, ch=True)
            alAttr = pm.getAttr(arclen_node + ".arcLength")
            ration_node = node.createMulNode(self.length_ratio_att,
                                             alAttr)

            pm.addAttr(self.mstIK_crv, ln="length_ratio", k=True, w=True)
            node.createDivNode(arclen_node.arcLength,
                               ration_node.outputX,
                               self.mstIK_crv.length_ratio)

            div_node_scl = node.createDivNode(self.mstIK_crv.length_ratio,
                                              dm_node_scl.outputScaleX)

        if self.def_number > 1:
            div_val = self.def_number - 1
        else:
            div_val = 1
        step = 0.998 / div_val
        u = 0.001

        self.mtnPthCns = []
        for i in range(self.def_number):
            cnsUpv = applyop.pathCns(self.upv_cns[i],
                                     self.upvIK_crv,
                                     cnsType=False,
                                     u=u,
                                     tangent=False)

            cns = applyop.pathCns(
                self.div_cns[i], self.mstIK_crv, False, u, True)
            
            self.mtnPthCns.append(cns)

            # Connectiong the scale for scaling compensation
            for axis, AX in zip("xyz", "XYZ"):
                pm.connectAttr(dm_node_scl.attr("outputScale{}".format(AX)),
                               self.div_cns[i].attr("s{}".format(axis)))

            if self.settings["keepLength"]:

                div_node2 = node.createDivNode(u, div_node_scl.outputX)

                cond_node = node.createConditionNode(div_node2.input1X,
                                                     div_node2.outputX,
                                                     4,
                                                     div_node2.input1X,
                                                     div_node2.outputX)

                pm.connectAttr(cond_node + ".outColorR",
                               cnsUpv + ".uValue")
                pm.connectAttr(cond_node + ".outColorR",
                               cns + ".uValue")

            cns.setAttr("worldUpType", 1)
            cns.setAttr("frontAxis", 0)
            cns.setAttr("upAxis", 1)

            pm.connectAttr(self.upv_cns[i].attr("worldMatrix[0]"),
                           cns.attr("worldUpMatrix"))
            u += step

        if self.settings["keepLength"]:
            # add the safty distance offset
            self.ikTip_npo.attr("tx").set(self.off_dist)
            # connect vis line ref
            # for shp in self.line_ref.getShapes():
            #     pm.connectAttr(self.ikVis_att, shp.attr("visibility"))

        for ctl in self.ik_ctl:
            for shp in ctl.getShapes():
                pm.connectAttr(self.ikVis_att, shp.attr("visibility"))
        for ctl in self.fk_ctl:
            for shp in ctl.getShapes():
                pm.connectAttr(self.fkVis_att, shp.attr("visibility"))


        #cm
        opSldMst = applyop.gear_curveslide2_op(self.sldIK_crv, self.mstIK_crv, 0, 1.5, .5, .5)
        pm.connectAttr(self.position_att, opSldMst+'.position')
        pm.connectAttr(self.maxStretch_att, opSldMst+'.maxstretch')
        pm.connectAttr(self.maxSquash_att, opSldMst+'.maxsquash')
        pm.connectAttr(self.softness_att, opSldMst+'.softness')

        opSldUV  = applyop.gear_curveslide2_op(self.sldUV_crv, self.upvIK_crv, 0, 1.5, .5, .5)
        pm.connectAttr(self.position_att, opSldUV+'.position')
        pm.connectAttr(self.maxStretch_att, opSldUV+'.maxstretch')
        pm.connectAttr(self.maxSquash_att, opSldUV+'.maxsquash')
        pm.connectAttr(self.softness_att, opSldUV+'.softness')

        # create ikSpline
        self.ikSpline = primitive.IkSplineOnCurve(self.sldIK_crv, count=len(self.div_cns), 
                                  attr=self.lengM_att, startCtl=None, endCtl=None, mpthNd=self.mtnPthCns)
        
        # constrain splineGrp to first IK ctl (proper ik spline rotation)
        applyop.gear_mulmatrix_op(self.ik_ctl[0].attr("worldMatrix"), self.splineGrp.attr("parentInverseMatrix[0]"), 
                                    target=self.splineGrp, transform='srt')


        # hide and parent ikSpline
        pm.setAttr(self.ikSpline[0][0]+'.v', 0)
        pm.setAttr(self.ikSpline[1][0]+'.v', 0)
        pm.parent(self.ikSpline[0][0], self.ikSpline[1][0], self.splineGrp)

        # twist
        if self.settings["twist"]:
            pm.connectAttr(self.twist_att, self.ikSpline[1][0]+".dTwistControlEnable")
            pm.setAttr(self.ikSpline[1][0]+".dWorldUpType", 4)
            pm.setAttr(self.ikSpline[1][0]+".dWorldUpAxis", 4)
            pm.connectAttr(self.ik_ctl[0]+'.wm[0]', self.ikSpline[1][0]+'.dWorldUpMatrix')
            pm.connectAttr(self.ik_ctl[-1]+'.wm[0]', self.ikSpline[1][0]+'.dWorldUpMatrixEnd')

        
        # mgear joints
        for i,jnt in enumerate(self.ikSpline[0]):
            self.jnt_pos.append([jnt, i])
        
    # =====================================================
    # CONNECTOR
    # =====================================================

    def setRelation(self):
        """Set the relation beetween object from guide to rig"""
        self.relatives["root"] = self.fk_ctl[0]
        self.controlRelatives["root"] = self.fk_ctl[0]
        self.jointRelatives["root"] = 0
        for i in range(0, len(self.fk_ctl) - 1):
            self.relatives["%s_loc" % i] = self.fk_ctl[i + 1]
            self.controlRelatives["%s_loc" % i] = self.fk_ctl[i + 1]
            self.jointRelatives["%s_loc" % i] = i + 1
            self.aliasRelatives["%s_ctl" % i] = i + 1
        self.relatives["%s_loc" % (len(self.fk_ctl) - 1)] = self.fk_ctl[-1]
        self.controlRelatives["%s_loc" % (
            len(self.fk_ctl) - 1)] = self.fk_ctl[-1]
        self.jointRelatives["%s_loc" % (
            len(self.fk_ctl) - 1)] = len(self.fk_ctl) - 1
        self.aliasRelatives["%s_loc" % (
            len(self.fk_ctl) - 1)] = len(self.fk_ctl) - 1

        #cm
        # for i,tra in enumerate(self.ik_npo_cns):
        #     self.relatives["ik%s_cns" % i] = tra
        for i,tra in enumerate(self.ik_npo_cns):
            self.aliasRelatives["ik%s_cns" % i] = tra
        
    def addConnection(self):
        """Add more connection definition to the set"""
        self.connections["standard"] = self.connect_standard

    def connect_standard(self):
        """standard connection definition for the component"""
        self.parent.addChild(self.root) # parent to root
        for num, i in enumerate(zip(self.ikref_lst, self.ik_sps_cns, self.ik_npo_cns)): # ref attributes (list) on hostUI, _sps transforms
            # i[0] = space switch attribute on UI Host for specific sps_cns
            # i[1] = _sps transform
            # i[2] = _cns transform

            # get rig names, from ikrefarray string list
            ref_names = self.get_valid_alias_list(self.settings["ikrefarray"].split(","))
            # add in _cns transform as first constraint
            ref_names.insert(0, str(i[2]))
            # add _sps transform as target
            ref_names.insert(len(ref_names), str(i[1]))
            # create constraint
            cns_node = pm.parentConstraint(*ref_names, maintainOffset=True)
            cns_attr = pm.parentConstraint(cns_node, query=True, weightAliasList=True)
            #py3 need to convert i[item] to variable (subscriptable err)
            uiAtt = i[0]
            for i, attr in enumerate(cns_attr):
                node_name = pm.createNode("condition")
                pm.connectAttr(uiAtt, node_name + ".firstTerm")
                pm.setAttr(node_name + ".secondTerm", i)
                pm.setAttr(node_name + ".operation", 0)
                pm.setAttr(node_name + ".colorIfTrueR", 1)
                pm.setAttr(node_name + ".colorIfFalseR", 0)
                pm.connectAttr(node_name + ".outColorR", attr)