import maya.cmds as cmds
import pymel.core as pm
import mgear.core.transform as trx
from mgear.core import attribute, vector
from mgear import rigbits
import mgear.core.anim_utils as amu
import mgear.shifter
from collections import OrderedDict

# To not break animation dept
try:
    import rigUtils as rigu
    import nodes as nde
    import mgearUtils as mgu
except:
    pass


class PrePost(object):
    def __init__(self, gdeRoot, gdeComponents):
        self.gdeRoot = gdeRoot
        self.gdeComponents = gdeComponents # all guide components under rig model
        self.armGdeDict = {}
        self.legGdeDict = {}
        self.visIco = None

    
    def preBuild(self, rigName):
        # Extract Ctl places ctlBuffer into ctl set.
        # Delete ctl set if exists.
        allSets = cmds.ls(type='objectSet')
        if allSets != []:
            for s in allSets:
                for x in ['_controllers_grp', '_sets_grp']:
                    if s == rigName+x:
                        cmds.delete(s)


    def tPose(self):
        # sort by component type
        if self.gdeComponents:
            for k,v in self.gdeComponents.items():
                compType = v.root.comp_type.get()
                
                if compType.startswith('arm_2jnt_freeTangentsOffset'):
                    if pm.attributeQuery('tPose', node=v.root, ex=True):
                        self.tPoseArms(v, v.root.tPose.get()) # component, T-Pose attr
                
                if compType.startswith('leg_2jnt_freeTangentsOffset'):
                    if pm.attributeQuery('tPose', node=v.root, ex=True):
                        self.tPoseLegs(v, v.root.tPose.get()) # component, T-Pose attr


    def bindPose(self, rg, ccn, fail=False):
        '''
        Restores guides and Ctls back to orig pose after rig build.

        ccn = (bol) Classic Channel Names - effects poseArm() and poseLeg() ikfk attr
        '''
        # Restore guides if set T-Pose is True
        if self.armGdeDict != {}:
            for k,v in self.armGdeDict.items():
                if v[1] == True: # Guide is in T-Pose
                    for gde in v[0]:
                        tra = pm.getAttr(gde.BindPose)
                        pm.xform(gde, ws=1, m=tra)
        if self.legGdeDict != {}:
            for k,v in self.legGdeDict.items():
                if v[1] == True: # Guide is in T-Pose
                    for gde in v[0]:
                        tra = pm.getAttr(gde.BindPose)
                        pm.xform(gde, ws=1, m=tra)

        # Restore ctls
        if fail == False: 
            self.poseArm(rg, ccn)
            self.poseLeg(rg, ccn)


############################################################################
    def aimAtArm(self, source, target):
        cons = pm.aimConstraint(target, source, weight=1, upVector=(0, 1, 0), worldUpType="vector", 
                                  offset=(0, 0, 0), aimVector=(1, 0, 0), worldUpVector=(0, 1, 0))
        return cons

    def aimAtLeg(self, source, target):
        cons = cmds.aimConstraint(target, source, weight=1, upVector=(0, 0, 1), worldUpType="vector", 
                                  offset=(0, 0, 0), aimVector=(0, -1, 0), worldUpVector=(0, 1, 0))
        return cons

    def tPoseArms(self, arm, tPose):
        lenLst = []
        rotPos = []
        traLst = []
        rtElbWrst = [arm.root]+[gde for gde in pm.listRelatives(arm.root, ad=True, type='transform')
                      if 'elbow' in gde.name() or 'wrist' in gde.name()]
        rtElbWrst = [[rtElbWrst[0], rtElbWrst[2], rtElbWrst[1]]][0] # root, elbow, wrist

        if tPose == True:
            self.armGdeDict[arm] = [rtElbWrst, tPose]
            # Set to build in IK
            pm.setAttr(arm.root.blend, 1)

            # arm.pos[key] returns guide vector
            fwdBck = vector.getPlaneBiNormal(arm.pos['root'], arm.pos['elbow'], arm.pos['wrist'])[2] #Getting binormal for ik solver

            for i,gde in enumerate(rtElbWrst):
                # Add bindpose matrix attr
                if pm.attributeQuery('BindPose', node=gde, ex=1) == False:
                    pm.addAttr(gde, ci=True, dt='matrix', sn='BindPose')
                bPose = pm.xform(gde, q=1, ws=1, m=1)
                pm.setAttr(gde+'.BindPose', bPose, type='matrix')

                # Store distance between guides in ws using transforms
                if i == 0:
                    pos = pm.xform(gde, q=1, ws=1, t=1)
                    rotPos = pos # store root translation
                    tra = pm.createNode('transform', n=gde+'_pos', ss=True)
                    pm.xform(tra, t=pos)
                    traLst.append(tra)
                else:
                    pos = pm.xform(gde, q=1, ws=1, t=1)
                    tra = pm.createNode('transform', n=gde+'_pos', ss=True)
                    pm.xform(tra, t=pos)
                    aim = self.aimAtArm(traLst[-1], tra) # Orient last tra to new tra
                    pm.delete(aim)
                    pm.parent(tra, traLst[-1])
                    if i == 2: # Orient wrist tra to elbow tra
                        pm.matchTransform(tra, traLst[-1], rot=1)
                    traLst.append(tra)
                    lenLst.append(pm.getAttr(tra+'.tx')) # add x value to list

            # Add side tag to list
            traLst.insert(0, pm.getAttr(arm.root.comp_side))

            # Negate x values for R side
            if traLst[0] == 'R':
                lenLst = [-x for x in lenLst]

            # Creates straight T-Pose positions
            gde0Tra = pm.createNode('transform', n=traLst[1]+'_tra0', ss=True)
            pm.xform(gde0Tra, t=rotPos)

            # Get tra1 offset
            gde1Pos = trx.getOffsetPosition(gde0Tra, offset=[lenLst[0], 0, 0])

            # Create elbow transform
            gde1Tra = pm.createNode('transform', n=traLst[2]+'_tra1', ss=True)
            pm.xform(gde1Tra, t=gde1Pos)

            # Get tra2 offset
            gde2Pos = trx.getOffsetPosition(gde1Tra, offset=[lenLst[1], 0, 0])

            # # Move elbow back in Z for IK solver
            if fwdBck > 0:
                zPos = trx.getOffsetPosition(gde1Tra, offset=[0, 0, 0.01])
            else:
                zPos = trx.getOffsetPosition(gde1Tra, offset=[0, 0, -0.01])

            pm.xform(gde1Tra, t=zPos)

            # Create tra2 transform
            gde2Tra = pm.createNode('transform', n=traLst[3]+'_tra2', ss=True)
            pm.xform(gde2Tra, t=gde2Pos)

            # Negate sx, and 180 rx
            if traLst[0] == 'R':
                for tra in [gde0Tra, gde1Tra]:
                    pm.xform(tra, ro=[180, 0, 0], s=[-1, 1, 1])
                pm.xform(gde2Tra, s=[-1, 1, 1])

            # tPose pos to tra matrix
            tPosePos = []
            for tra in [gde0Tra, gde1Tra, gde2Tra]:
                pos = pm.xform(tra, q=1, ws=1, m=1)
                tPosePos.append(pos)
            pm.delete(gde0Tra, gde1Tra, gde2Tra)

            # Move guides
            for i,gde in enumerate(rtElbWrst):
                scale = pm.xform(gde, q=1, s=1)
                pm.xform(gde, ws=1, m=tPosePos[i])
                pm.xform(gde, s=scale)

            pm.delete(traLst[1:])

        else:
            # Add bindpose matrix attr
            for i,gde in enumerate(rtElbWrst):
                if pm.attributeQuery('BindPose', node=gde, ex=1) == False:
                    pm.addAttr(gde, ci=True, dt='matrix', sn='BindPose')
                bPose = pm.xform(gde, q=1, ws=1, m=1)
                pm.setAttr(gde+'.BindPose', bPose, type='matrix')

    def tPoseLegs(self, leg, tPose):
        lenLst = []
        rotPos = []
        traLst = []
        rtKneeAnkle = [leg.root]+[gde for gde in pm.listRelatives(leg.root, ad=True, type='transform')
                      if 'knee' in gde.name() or 'ankle' in gde.name()]
        rtKneeAnkle = [[rtKneeAnkle[0], rtKneeAnkle[2], rtKneeAnkle[1]]][0] # root, knee, ankle

        if tPose == True:
            self.legGdeDict[leg] = [rtKneeAnkle, tPose]
            # Set to build in IK
            pm.setAttr(leg.root.blend, 1)
            # leg.pos[key] returns guide vector
            fwdBck = vector.getPlaneBiNormal(leg.pos['root'], leg.pos['knee'], leg.pos['ankle'])[2] #Getting binormal for ik solver
            
            for i,gde in enumerate(rtKneeAnkle):
                # Add bindpose matrix attr
                if pm.attributeQuery('BindPose', node=gde, ex=1) == False:
                    pm.addAttr(gde, ci=True, dt='matrix', sn='BindPose')
                bPose = pm.xform(gde, q=1, ws=1, m=1)
                pm.setAttr(gde+'.BindPose', bPose, type='matrix')

                # Store distance between guides in ws using transforms
                if i == 0:
                    pos = pm.xform(gde, q=1, ws=1, t=1)
                    rotPos = pos # store root translation
                    tra = pm.createNode('transform', n=gde+'_pos', ss=True)
                    pm.xform(tra, t=pos)
                    traLst.append(tra)
                else:
                    pos = pm.xform(gde, q=1, ws=1, t=1)
                    tra = pm.createNode('transform', n=gde+'_pos', ss=True)
                    pm.xform(tra, t=pos)
                    aim = self.aimAtArm(traLst[-1], tra) # Orient last tra to new tra
                    pm.delete(aim)
                    pm.parent(tra, traLst[-1])
                    if i == 2: # Orient ankle tra to knee tra
                        pm.matchTransform(tra, traLst[-1], rot=1)
                    traLst.append(tra)
                    lenLst.append(pm.getAttr(tra+'.tx')) # add x value to list

            # Add side tag to list
            traLst.insert(0, pm.getAttr(leg.root.comp_side))

            # # Negate len values
            lenLst = [-x for x in lenLst]
            
            # Creates straight T-Pose positions
            gde0Tra = pm.createNode('transform', n=traLst[1]+'_tra0', ss=True)
            pm.xform(gde0Tra, t=rotPos)

            # Get tra1 offset
            gde1Pos = trx.getOffsetPosition(gde0Tra, offset=[0, lenLst[0], 0])

            # Create knee transform
            gde1Tra = pm.createNode('transform', n=traLst[2]+'_tra1', ss=True)
            pm.xform(gde1Tra, t=gde1Pos)

            # Get tra2 offset
            gde2Pos = trx.getOffsetPosition(gde1Tra, offset=[0, lenLst[1], 0])

            # Move knee forward or back in Z for IK solver
            if fwdBck > 0:
                zPos = trx.getOffsetPosition(gde1Tra, offset=[0, 0, 0.01])
            else:
                zPos = trx.getOffsetPosition(gde1Tra, offset=[0, 0, -0.01])
            pm.xform(gde1Tra, t=zPos)

            # Create tra2 transform
            gde2Tra = pm.createNode('transform', n=traLst[3]+'_tra2', ss=True)
            pm.xform(gde2Tra, t=gde2Pos)

            # Negate sx, and 180 rx
            if traLst[0] == 'R':
                for tra in [gde0Tra, gde1Tra, gde2Tra]:
                    pm.xform(tra, s=[-1, 1, 1])

            # tPose pos to tra matrix
            tPosePos = []
            for tra in [gde0Tra, gde1Tra, gde2Tra]:
                pos = pm.xform(tra, q=1, ws=1, m=1)
                tPosePos.append(pos)
            pm.delete(gde0Tra, gde1Tra, gde2Tra)

            # Move guides
            for i,gde in enumerate(rtKneeAnkle):
                scale = pm.xform(gde, q=1, s=1)
                pm.xform(gde, ws=1, m=tPosePos[i])
                pm.xform(gde, s=scale)

            pm.delete(traLst[1:])

        else: # Add bindpose matrix attr
            for i,gde in enumerate(rtKneeAnkle):
                if pm.attributeQuery('BindPose', node=gde, ex=1) == False:
                    pm.addAttr(gde, ci=True, dt='matrix', sn='BindPose')
                bPose = pm.xform(gde, q=1, ws=1, m=1)
                pm.setAttr(gde+'.BindPose', bPose, type='matrix')

    def poseArm(self, rg, ccn):
        for arm, items in self.armGdeDict.items(): # items = [guides, tPose]
            cmpCtl    = rg.findControlRelative(items[0][-1]) # Get component ctl from guide (arm.root)
            uiHost    = amu.get_host_from_node(cmpCtl) # Get component UI Host
            blendAttr = [attr for attr in cmds.listAttr(uiHost) if attr.endswith('blend')][0]
            ikMirror  = cmds.getAttr(items[0][0]+'.mirrorIK') # Mirror IK Ctl, checkbox in arm settings
            ikRotCtl  = cmds.getAttr(items[0][0]+'.ikTR') # IK separated Trans and Rot ctl
            ctlAttr   = '_'.join(items[0][-1].split('_')[:2])+'_id0_ctl' # Attr on uiHost that contains all ctl names

            # classic channel names
            if ccn == True:
                ikfk = amu.get_ik_fk_controls_by_role(uiHost, 
                               '_'.join(items[0][-1].split('_')[:2])+'_id0_ctl_cnx')# Get ikfk ctls from cnx attr
            else:
                ikfk = amu.get_ik_fk_controls_by_role(uiHost, 
                               '_'.join(items[0][-1].split('_')[:1])+'_id0_ctl_cnx')# Get ikfk ctls from cnx attr


            # Match wrist ctl to wrist guide
            wristCtl = ikfk[0].get('ik_cns')
            wristGde = pm.PyNode([gde for gde in items[0] if gde.endswith('_wrist')][0]) # arm_*0_wrist
            if wristCtl and wristGde:
                pm.matchTransform(wristCtl, wristGde, rot=1, pos=1)

            # Orient wrist
            eff  = pm.listRelatives(wristGde, c=1, type='transform') # Attempt to get eff gde
            tra1 = pm.createNode('transform', n='tra1', ss=True)
            tra2 = pm.createNode('transform', n='tra2', ss=True)
            pm.matchTransform(tra1, wristGde)
            pm.matchTransform(tra2, eff)

            if ikRotCtl != False: # If separated Trans and Rot ctl
                if 'R' in wristGde.name().split('_')[1]:
                    aimVec = (-1, 0, 0)
                    upVec  = (0, 0, -1)
                else:
                    aimVec = (1, 0, 0)
                    upVec  = (0, 0, 1)
            else:
                if 'R' in wristGde.name().split('_')[1]:
                    aimVec = (-1, 0, 0)
                    upVec  = (0, -1, 0)
                else:
                    aimVec = (1, 0, 0)
                    upVec  = (0, 1, 0)

            cons = pm.aimConstraint(tra2, tra1, weight=1, upVector=upVec, worldUpType="objectrotation", 
            worldUpObject=wristGde, offset=(0, 0, 0), aimVector=aimVec, worldUpVector=(0, 1, 0))
            
            if ikRotCtl != False:
                rotCtl = ikfk[0].get('ik_rot')
                pm.matchTransform(rotCtl, tra1, rot=1)
            else: # orient ikcns ctl
                pm.matchTransform(wristCtl, tra1, rot=1)

            pm.delete(tra1, tra2)

            # ikmid ctl
            ikMid = ikfk[0].get('ik_mid')
            # Move elbow
            elbowGde = pm.PyNode([gde for gde in items[0] if gde.endswith('_elbow')][0]) # arm_R0_elbow
            if elbowGde and ikMid:
                pm.matchTransform(ikMid, elbowGde)

            # # Match FK to IK
            rigRoot = mgu.getRigRoot(py=True)[0][0]
            upV   = ikfk[0].get('pole_vector') # arm_R0_upv_ctl
            ikCtl = ikfk[0].get('ik_control') # arm_R0_ik_ctl
            fkLst = []
            # Convert 'pymel.core.other.DependNodeName' to list of strings
            [fkLst.append(str(i).split('"')[0]) for i in ikfk[1]]

            if ikRotCtl != False:
                # ikFkMatch(model, ikfk_attr, ui_host, fks, ik, upv, ik_rot=None, key=None):
                amu.ikFkMatch(rigRoot, blendAttr, uiHost, fkLst, ikCtl, 
                              upV, ik_rot=rotCtl, key=None)
            else:
                amu.ikFkMatch(rigRoot, blendAttr, uiHost, fkLst, ikCtl, 
                              upV, ik_rot=None, key=None)

            # Add attr for synoptic reset transform
            srtLst = []
            [srtLst.append(pm.PyNode(i)) for i in ikfk[0].values() if i != None] # ik ctls
            [srtLst.append(pm.PyNode(i)) for i in ikfk[1]] # fk ctls

            if srtLst != []:
                for node in srtLst:
                    tx, ty, tz = node.getTranslation()
                    rx, ry, rz = node.getRotation()
                    sx, sy, sz = node.getScale()
                    trsDic = OrderedDict()
                    trsDic = {"tx": tx,
                              "ty": ty,
                              "tz": tz,
                              "rx": rx,
                              "ry": ry,
                              "rz": rz,
                              "sx": sx,
                              "sy": sy,
                              "sz": sz}
                    pm.addAttr(node, ci=True, dt='string', sn='BindPose')
                    pm.setAttr(node.BindPose, str(trsDic))

    def poseLeg(self, rg, ccn):
        for leg, items in self.legGdeDict.items(): # items = [guides, tPose]
            cmpCtl    = rg.findControlRelative(items[0][-1]) # Get component ctl from guide (leg_*0_ikoff_ctl)
            uiHost    = amu.get_host_from_node(cmpCtl) # Get component UI Host
            blendAttr = [attr for attr in cmds.listAttr(uiHost) if attr.endswith('blend')][0]
            
            # classic channel names
            if ccn == True:
                ikfk = amu.get_ik_fk_controls_by_role(uiHost, 
                               '_'.join(items[0][-1].split('_')[:2])+'_id0_ctl_cnx')# Get ikfk ctls from cnx attr
            else:
                ikfk = amu.get_ik_fk_controls_by_role(uiHost, 
                               '_'.join(items[0][-1].split('_')[:1])+'_id0_ctl_cnx')# Get ikfk ctls from cnx attr


            ankleCtl = ikfk[0].get('ik_cns')  # leg_R0_ikcns_ctl
            ankleGde = pm.PyNode([gde for gde in items[0] if gde.endswith('_ankle')][0]) # leg_R0_ankle
            if ankleCtl and ankleGde:
                pm.matchTransform(ankleCtl, ankleGde, rot=1, pos=1) # Match ikcns ctl to ankle gde
                pm.setAttr(ankleCtl.rx, 0) # Catches right side flip

            # Move knee
            ikMid = ikfk[0].get('ik_mid')
            kneeGde = pm.PyNode([gde for gde in items[0] if gde.endswith('_knee')][0]) # leg_R0_knee
            if kneeGde and ikMid:
                pm.matchTransform(ikMid, kneeGde)

            rigRoot = mgu.getRigRoot(py=True)[0][0]
            upV   = ikfk[0].get('pole_vector') # leg_R0_upv_ctl
            ikCtl = ikfk[0].get('ik_control') # leg_R0_ik_ctl
            fkLst = []
            # Convert 'pymel.core.other.DependNodeName' to list of strings
            [fkLst.append(str(i).split('"')[0]) for i in ikfk[1]]

            amu.ikFkMatch(rigRoot, blendAttr, uiHost, fkLst, ikCtl, 
                          upV, ik_rot=None, key=None)
            
            # Add attr for synoptic reset transform
            srtLst = []
            [srtLst.append(pm.PyNode(i)) for i in ikfk[0].values() if i != None] # ik ctls
            [srtLst.append(pm.PyNode(i)) for i in ikfk[1]] # fk ctls

            if srtLst != []:
                for node in srtLst:
                    tx, ty, tz = node.getTranslation()
                    rx, ry, rz = node.getRotation()
                    sx, sy, sz = node.getScale()
                    trsDic = OrderedDict()
                    trsDic = {"tx": tx,
                              "ty": ty,
                              "tz": tz,
                              "rx": rx,
                              "ry": ry,
                              "rz": rz,
                              "sx": sx,
                              "sy": sy,
                              "sz": sz}
                    pm.addAttr(node, ci=True, dt='string', sn='BindPose')
                    pm.setAttr(node.BindPose, str(trsDic))

            pm.setAttr(uiHost+'.'+blendAttr, 1)

    def cleanUp(self, rigName):
        cmds.select(None) # mGear selects the ctls after build
        print('Creating custom transforms')
        if cmds.objExists(rigName):
            # Geo group
            traDict = OrderedDict([('custom_org',rigName), ('customAttrs', 'custom_org'), ('geo_org',rigName), 
                ('highResGeo_org','geo_org'), ('lowResGeo_org','geo_org'), ('model','highResGeo_org'), ('customGeo_org','highResGeo_org')])
            # Lock attrs
            lckAttr = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']

            for k,v in traDict.items():
                if cmds.objExists(k):
                    # Reparent
                    if cmds.listRelatives(k, p=True) == None:
                        cmds.parent(k,v)
                else:
                    cmds.createNode('transform', n=k, p=v, ss=True)

                if k == 'customAttrs': # Remove keyable attrs
                    [cmds.setAttr(k+'.'+att, k=False, l=True) for att in lckAttr]
                    cmds.setAttr(k+'.visibility', k=False)

        #________________________________________________________________________________________________________
            # Visibility attrs
            print('Creating custom attributes on faceUI_C0_ctl')
            # Get attr host objects
            allCtl = [ctl for ctl in cmds.listRelatives(rigName, ad=True, type='transform') if ctl.endswith('_ctl')]
            allUIs = [ctl for ctl in allCtl if cmds.attributeQuery('isUiHost', node=ctl, ex=True)]
            faceUI = [ui for ui in allUIs if cmds.getAttr(ui+'.uiHostType') == 'face']
            
            # visIco = 'faceUI_C0_ctl'
            if faceUI != []:
                self.visIco = faceUI[0]
                if cmds.objExists(self.visIco):
                    if not cmds.attributeQuery('__________', node=self.visIco, ex=True):
                        cmds.addAttr(self.visIco, ln='__________', en='visibilities:', at='enum', ci=True, k=True)

                    attrDict = OrderedDict()
                    attrDict['LOD1'] = ['bool', 0]
                    attrDict['allGeoVis'] = ['bool', 1]
                    attrDict['bodySecondaryCtls'] = ['bool', 0]
                    attrDict['bodyTertiaryCtls'] = ['bool', 0]
                    attrDict['facePrimaryCtls'] = ['bool', 0]
                    attrDict['faceSecondaryCtls'] = ['bool', 0]
                    attrDict['faceTertiaryCtls'] = ['bool', 0]
                    attrDict['faceSliderCtls'] = ['bool', 0]
                    attrDict['faceHairVis'] = ['bool', 0]
                    for k,v in attrDict.items():
                        if not cmds.attributeQuery(k, node=self.visIco, ex=True):
                            cmds.addAttr(self.visIco, ci=True, k=True, at=v[0], sn=k, min=0, max=1, dv=v[1])
            else:
                self.visIco = None
        
        #________________________________________________________________________________________________________
            print('Remove global ctl from dagPose')
            # Remove global ctl from dagPose, since scale is now driven by global scale attr
            if cmds.objExists('global_C0_ctl'):
                if cmds.attributeQuery('globalScale', node='global_C0_ctl', ex=True):
                    if cmds.listConnections('global_C0_ctl'+'.message') != []:
                        conn = cmds.listConnections('global_C0_ctl'+'.message', p=True)
                        for c in conn:
                            if 'dagPose' in c:
                                cmds.disconnectAttr('global_C0_ctl'+'.message', c)

        #________________________________________________________________________________________________________
            # Add mGear face ctrls to simplex face ctrl vis
            if self.visIco != None:
                print('Connecting mGear face ctls to faceTertiaryCtls')
                # Primary
                for ctl in ['teethTop_C0_ctl', 'teethBot_C0_ctl', 'tongue_C0_fk5_ctl','tongue_C0_fk4_ctl',
                            'tongue_C0_fk3_ctl','tongue_C0_fk2_ctl','tongue_C0_fk1_ctl','tongue_C0_fk0_ctl']:
                    if cmds.objExists(ctl) and cmds.objExists(self.visIco):
                        cmds.setAttr(ctl+'.v', l=0)
                        cmds.connectAttr(self.visIco+'.facePrimaryCtls', ctl+'.v', f=True)
                # Tertiary
                for ctl in ['eye_L0_lashTop_ctl', 'eye_L0_lashBot_ctl',
                            'eye_R0_lashTop_ctl', 'eye_R0_lashBot_ctl']:
                    if cmds.objExists(ctl) and cmds.objExists(self.visIco):
                        cmds.setAttr(ctl+'.v', l=0)
                        cmds.connectAttr(self.visIco+'.faceTertiaryCtls', ctl+'.v', f=True)

        #________________________________________________________________________________________________________
            # Geo vis
            if self.visIco != None:
                print('Connecting geo vis attrs')
                if cmds.objExists('mGear_geoVisRev'):
                    revNde = cmds.ls('mGear_geoVisRev')[0]
                else:
                    revNde = cmds.createNode('reverse', n='mGear_geoVisRev', ss=True)

                # LOD vis
                if cmds.listConnections(revNde+'.inputX') != None:
                    if cmds.listConnections(revNde+'.inputX', p=True, s=True)[0] != self.visIco+'.LOD1':
                        cmds.connectAttr(self.visIco+'.LOD1', revNde+'.inputX', f=True)
                else:
                    cmds.connectAttr(self.visIco+'.LOD1', revNde+'.inputX', f=True)


                if cmds.listConnections('lowResGeo_org.v') != None:
                    if cmds.listConnections('lowResGeo_org.v', p=True, s=True)[0] != revNde+'.outputX':
                        cmds.connectAttr(revNde+'.outputX', 'lowResGeo_org.v', f=True)
                else:
                    cmds.connectAttr(revNde+'.outputX', 'lowResGeo_org.v', f=True)
                

                if cmds.listConnections('highResGeo_org.v') != None:
                    if cmds.listConnections('highResGeo_org.v', p=True, s=True)[0] != self.visIco+'.LOD1':
                        cmds.connectAttr(self.visIco+'.LOD1', 'highResGeo_org.v', f=True)
                else:
                    cmds.connectAttr(self.visIco+'.LOD1', 'highResGeo_org.v', f=True)
                # All Geo vis
                cmds.connectAttr(self.visIco+'.allGeoVis', 'geo_org.v')

        #________________________________________________________________________________________________________
            # allGeo Display Layer
            print('Creating display layers')
            if not pm.ls(rigName+'_allGeo', type='displayLayer'):
                dspLyr = pm.createDisplayLayer(name=rigName+'_allGeo')
                geoGrp = pm.SCENE.geo_org
                pm.editDisplayLayerMembers(dspLyr, geoGrp)
                pm.setAttr(dspLyr.displayType, 2)
            else:
                dspLyr = pm.ls(rigName+'_allGeo', type='displayLayer')[0]
                geoGrp = pm.SCENE.geo_org
                pm.editDisplayLayerMembers(dspLyr, geoGrp)
                # pm.setAttr(dspLyr.displayType, 2) #reference

        #________________________________________________________________________________________________________
            # SMPX Secondary face ctls
            smpxFaceCtls = []
            if cmds.objExists('simplexFaceCtls'):
                priGrp = []
                secGrp = []
                tirGrp = []
                headCutTir = []
                print('Creating SMPX Secondary Ctl attrs')
                priGrp = [c for c in cmds.listRelatives('simplexFaceCtls', c=True, type='transform') if c=='primaryCtls']
                secGrp = [c for c in cmds.listRelatives('simplexFaceCtls', c=True, type='transform') if c=='secondaryCtls']
                tirGrp = [c for c in cmds.listRelatives('simplexFaceCtls', c=True, type='transform') if c=='tertiaryCtls']
                headCutTir = [c for c in cmds.listRelatives('simplexFaceCtls', c=True, type='transform') if c=='headCutTir']

                # Could be in customGeo_org
                if cmds.objExists('customGeo_org'):
                    #custom_geo may not have any children
                    if cmds.listRelatives('customGeo_org', c=True, type='transform') != None:
                        if 'headCutTir' in cmds.listRelatives('customGeo_org', c=True, type='transform'):
                            headCutTir = [c for c in cmds.listRelatives('customGeo_org', c=True, type='transform') if c=='headCutTir']

                
                if self.visIco != None:
                    if priGrp != []:
                        if cmds.attributeQuery('facePrimaryCtls', node=self.visIco, ex=True):
                            grp = priGrp[0]
                            cmds.connectAttr(self.visIco+'.facePrimaryCtls', grp+'.v', f=1)
                            cmds.setAttr(self.visIco+'.facePrimaryCtls', 1)
                    if secGrp != []:
                        if cmds.attributeQuery('faceSecondaryCtls', node=self.visIco, ex=True):
                            grp = secGrp[0]
                            cmds.connectAttr(self.visIco+'.faceSecondaryCtls', grp+'.v', f=1)
                            cmds.setAttr(self.visIco+'.faceSecondaryCtls', 0)
                    if tirGrp != []:
                        if cmds.attributeQuery('faceTertiaryCtls', node=self.visIco, ex=True):
                            grp = tirGrp[0]
                            cmds.connectAttr(self.visIco+'.faceTertiaryCtls', grp+'.v', f=1)
                            cmds.setAttr(self.visIco+'.faceTertiaryCtls', 0)
                            
                    if headCutTir != []:
                        headCut = headCutTir[0]
                        if cmds.attributeQuery('LOD1', node=self.visIco, ex=True):
                            cmds.connectAttr(self.visIco+'.LOD1', headCut+'.v', f=1)

                # prep secondary face ctls for selection set creation
                print('List SMPX Ctls to add to selection set')
                for grp in [priGrp, secGrp, tirGrp]:
                    if grp != []:
                        smpxFaceCtls.append([ctl for ctl in cmds.listRelatives(grp, ad=True, type='joint') if ctl.endswith('_ctl')])

                print('Add headCutTir to allGeo display layer test')
                if headCutTir != []:
                    dspLyr = cmds.ls(rigName+'_allGeo', type='displayLayer')[0]
                    cmds.editDisplayLayerMembers(dspLyr, headCutTir)


            
            # SMPX Sliders
            smpxSliders = []
            if cmds.objExists('faceSlidersOffset'):
                print('Constraining slider to head')
                if self.visIco != None:
                    cmds.connectAttr(self.visIco+'.faceSliderCtls', 'faceSlidersOffset.v', f=True)
                # Parent constraint
                if cmds.objExists('neck_C0_head_jnt') and cmds.objExists('simplexSlidersRoot'):
                    rigu.parentConstraint('neck_C0_head_jnt', 'simplexSlidersRoot')
            
                # prep smpx sliders for set creation
                smpxSliders = []
                smpxSliders.append([ctl for ctl in cmds.listRelatives('simplexSlidersRoot', ad=True, type='transform') if ctl.endswith('_Ctrl')])
            
        #________________________________________________________________________________________________________
            # Selection Sets

            # Create selection sets
            print('Creating selection sets')
            fkCtls = cmds.ls('*_fk*_ctl', type='transform')
            selectionDict = {'_faceSliders_grp': smpxSliders,
                             '_faceSecondaryCtls_grp': smpxFaceCtls,
                             '_mocapFK_grp': fkCtls,
                             }

            # Add ctls to rig set(s)
            for key, value in selectionDict.items():
                cmds.select(None)
                print('Creating selection set ', key)
                newSet  = None
                mstrSet = None
                allSets = cmds.ls(type='objectSet')
                # See if set exists
                if allSets != []:
                    for s in allSets:
                        if s == rigName+key:
                            newSet  = s
                        if s == rigName+'_sets_grp':
                            mstrSet = s
                
                # Create if missing the set
                if newSet == None: 
                    newSet = cmds.sets(n=rigName + key)
                    idx = nde.getNextFreeMultiIndex(rigName+'.rigGroups', 2)# Get next available port
                    cmds.connectAttr(newSet+'.message', rigName+'.rigGroups[{}]'.format(idx))
                    if mstrSet != None:
                        cmds.sets(newSet, edit=True, add=mstrSet)

                if value != []:
                    # Add ctrls to set, if not already a member, or in skip list.
                    print('Adding ctls to selection set ', key)
                    if key == '_mocapFK_grp':
                        for ctl in value:
                            if ctl.split('_')[0] not in ['eye', 'finger', 'thumb', 'tongue', 'jaw']:
                                if cmds.sets(ctl, isMember=newSet) == False:
                                    cmds.sets(ctl, edit=True, forceElement=newSet)

                    else:
                        for ctl in value:
                            if cmds.sets(ctl, isMember=newSet) == False:
                                    cmds.sets(ctl, edit=True, forceElement=newSet)

                if mstrSet != None:
                    cmds.sets(newSet, edit=True, forceElement=mstrSet)