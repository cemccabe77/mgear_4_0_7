import maya.cmds as cmds
import pymel.core as pm
import xml
import curves as crv
import surfaces as srf;reload(srf)
import strap;reload(strap)
import rigUtils as rigu
import skincluster as skn
from collections import OrderedDict
import random
import mgear.core.transform as tra
from os import listdir
from os.path import isfile, join
import json


'''
TO USE:
import wingFeathers as wft;reload(wft)

# Create all builder obj's
wft.buildBuilders()

# Layout Feathers (select crv)
wft.build(strapWidth = 0.015, endJntSize = 0.1, offDir='.ty')

# Manually place each feather root (select _grp)
[wft.removeConstraints(i) for i in cmds.ls(sl=1)]

# Mirror Feathers
# First mirror curves, and build feathers
# (select RIGHT side _bfr's)
wft.mirrorSelBfr(cmds.ls(sl=1))

# Rig Feathers (select _grp)
wft.rig(dorNum=9, ctlSize=0.15, wgtFile='D:/Working/cmlib/python/components/wingFeathersWeights.json')


Connect global scale attr to 'off' and 'ctlRef'
ctlRef is under 'root' transforms. Select roots, then ctlRef. Then global scale

'''








########################################################################################################################
#local variables

'''
# BKUP Skin cluster joints for feather rig curve (canary rig)
priJtsL = ['wingKnuckle_L0_0_jnt', 'wingKnuckle_L0_1_jnt', 'wingKnuckle_L0_2_jnt']
secJtsL = ['wing_L0_0_jnt', 'wing_L0_1_jnt', 'wing_L0_2_jnt', 'wing_L0_3_jnt', 'wing_L0_4_jnt', 'wing_L0_6_jnt',
           'wing_L0_8_jnt', 'wing_L0_9_jnt', 'wing_L0_10_jnt', 'wing_L0_11_jnt', 'wing_L0_12_jnt']
priJtsR = ['wingKnuckle_R0_0_jnt', 'wingKnuckle_R0_1_jnt', 'wingKnuckle_R0_2_jnt']
secJtsR = ['wing_R0_0_jnt', 'wing_R0_1_jnt', 'wing_R0_2_jnt', 'wing_R0_3_jnt', 'wing_R0_4_jnt', 'wing_R0_6_jnt',
           'wing_R0_8_jnt', 'wing_R0_9_jnt', 'wing_R0_10_jnt', 'wing_R0_11_jnt', 'wing_R0_12_jnt']
'''

# Skin cluster joints for feather rig curve (biped wing)
priJtsL = ['secondaryMaster_L0_2_jnt', 'primaryMid_L0_1_jnt',]
secJtsL = ['scapulaMaster_L0_2_jnt', 'tertialMaster_L0_2_jnt', 'secondaryMaster_L0_2_jnt']

priBotJtsL = ['secondaryMaster_L0_1_jnt', 'primaryMid_L0_0_jnt',]
secBotJtsL = ['scapulaMaster_L0_1_jnt', 'tertialMaster_L0_1_jnt', 'secondaryMaster_L0_1_jnt']

priTopJtsL = ['secondaryMaster_L0_1_jnt', 'primaryMid_L0_0_jnt',]
secTopJtsL = ['scapulaMaster_L0_0_jnt', 'tertialMaster_L0_0_jnt', 'primaryMid_L0_1_jnt']



priJtsR = ['secondaryMaster_R0_2_jnt', 'primaryMid_R0_1_jnt',]
secJtsR = ['scapulaMaster_R0_2_jnt', 'tertialMaster_R0_2_jnt', 'secondaryMaster_R0_2_jnt']

priBotJtsR = ['secondaryMaster_R0_1_jnt', 'primaryMid_R0_0_jnt',]
secBotJtsR = ['scapulaMaster_R0_1_jnt', 'tertialMaster_R0_1_jnt', 'secondaryMaster_R0_1_jnt']

priTopJtsR = ['secondaryMaster_R0_1_jnt', 'primaryMid_R0_0_jnt',]
secTopJtsR = ['scapulaMaster_R0_0_jnt', 'tertialMaster_R0_0_jnt', 'primaryMid_R0_1_jnt']


# Pool of feathers to randomly build from
arayPri = ['featherCenterPrimary_01', 'featherCenterPrimary_02', 'featherCenterPrimary_03', 'featherCenterPrimary_04']
araySec = ['featherCenterSecondary_01', 'featherCenterSecondary_02', 'featherCenterSecondary_03']
arayPriTop = ['featherTopMidPrimary_01', 'featherTopMidPrimary_02', 'featherTopMidPrimary_03']
araySecTop = ['featherTopMidSecondary_01', 'featherTopMidSecondary_02']
arayTailC  = ['featherCenterPrimary_03', 'featherCenterPrimary_04']

########################################################################################################################
featherEdgeDict = { # Name of feather geometry : Edges on geo to extract curve for strap surface.
                   'featherCenterPrimary_01'   : [329, 328, 330, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194],
                   'featherCenterPrimary_02'   : [329, 328, 330, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194],
                   'featherCenterPrimary_03'   : [329, 328, 330, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194],
                   'featherCenterPrimary_04'   : [329, 328, 330, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194],

                   'featherCenterSecondary_01' : [329, 328, 330, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194],
                   'featherCenterSecondary_02' : [329, 328, 330, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194],
                   'featherCenterSecondary_03' : [329, 328, 330, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194],

                   'featherTopMidPrimary_01'   : [329, 328, 330, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194],
                   'featherTopMidPrimary_02'   : [329, 328, 330, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194],
                   'featherTopMidPrimary_03'   : [329, 328, 330, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194],

                   'featherTopMidSecondary_01' : [329, 328, 330, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194],
                   'featherTopMidSecondary_02' : [329, 328, 330, 215, 214, 213, 212, 211, 210, 209, 208, 207, 206, 205, 204, 203, 202, 201, 200, 199, 198, 197, 196, 195, 194],
                   }
########################################################################################################################
'''
####  featherDict  ####
featherObj = (str) Name of feather object to be instanced
count      = (int) Number of feathers to create along guide curve
name       = (str) Name to use when building groups
edgeList   = ([ ]) List taken from featherEdgeDict to create feather rig strap
offset     = (int) Distance to offset the mid and down feather layers
curveJnts  = ([ ]) List of rig joints to bind to the rebuild curve
parGrp     = (str) Name of parent group for feather rig group
visAttr    = (str) Name of attr on wingRigRoot to drive visiblities
'''
featherDict = {
                ############# Left Main
                # {curveName :       [count,   name,    offset,    curveJnts,       parGrp,             visAttr            membraineSrf      featherArray]
                'centerPri_L0_crv' : [9,  'centerPri_L0_', 0,       priJtsL, 'wingCenter_L0_drv', '__wing_L_main', 'wing_L0_membraineN2_drv', arayPri],
                'centerSec_L0_crv' : [30, 'centerSec_L0_', 0,       secJtsL, 'wingCenter_L0_drv', '__wing_L_main', 'wing_L0_membraineN2_drv', araySec],
               
                #### Left Top Mid
                'topMidPri_L0_crv' : [8,  'topMidPri_L0_', -0.075,  priBotJtsL, 'wingTopMid_L0_drv', '__wing_L_top_mid', 'wing_L0_membraineN2_drv', arayPri],
                'topMidSec_L0_crv' : [19, 'topMidSec_L0_', -0.075,  secBotJtsL, 'wingTopMid_L0_drv', '__wing_L_top_mid', 'wing_L0_membraineN2_drv', araySec],
                
                #### Left Top Tip
                'topTipPri_L0_crv' : [8,  'topTipPri_L0_', -0.125,  priJtsL, 'wingTopTip_L0_drv', '__wing_L_top_down', 'wing_L0_membraineN2_drv', arayPri],
                'topTipSec_L0_crv' : [18, 'topTipSec_L0_', -0.125,  secTopJtsL, 'wingTopTip_L0_drv', '__wing_L_top_down', 'wing_L0_membraineN2_drv', araySec],

                #### Left Bot Mid
                'botMidPri_L0_crv' : [8,  'botMidPri_L0_', 0.075,   priBotJtsL, 'wingBotMid_L0_drv', '__wing_L_bot_mid', 'wing_L0_membraineN2_drv', arayPri],
                'botMidSec_L0_crv' : [19, 'botMidSec_L0_', 0.075,   secBotJtsL, 'wingBotMid_L0_drv', '__wing_L_bot_mid', 'wing_L0_membraineN2_drv', araySec],

                #### Left Bot Down
                'botTipPri_L0_crv' : [8,  'botTipPri_L0_', 0.125,   priJtsL, 'wingBotTip_L0_drv', '__wing_L_bot_down', 'wing_L0_membraineN2_drv', arayPri],
                'botTipSec_L0_crv' : [18, 'botTipSec_L0_', 0.125,   secTopJtsL, 'wingBotTip_L0_drv', '__wing_L_bot_down', 'wing_L0_membraineN2_drv', araySec],

                

                ############# Right Main
                # {curveName :        [count,   name,   offset,    curveJnts,       parGrp,             visAttr            membraineSrf]
                'centerPri_R0_crv' : [9,  'centerPri_R0_', 0,       priJtsR, 'wingCenter_R0_drv', '__wing_R_main', 'wing_R0_membraineN2_drv', arayPri],
                'centerSec_R0_crv' : [30, 'centerSec_R0_', 0,       secJtsR, 'wingCenter_R0_drv', '__wing_R_main', 'wing_R0_membraineN2_drv', araySec],
               
                #### Left Top Mid
                'topMidPri_R0_crv' : [8,  'topMidPri_R0_', -0.075,  priBotJtsR, 'wingTopMid_R0_drv', '__wing_R_top_mid', 'wing_R0_membraineN2_drv', arayPri],
                'topMidSec_R0_crv' : [19, 'topMidSec_R0_', -0.075,  secBotJtsR, 'wingTopMid_R0_drv', '__wing_R_top_mid', 'wing_R0_membraineN2_drv', araySec],
                
                #### Left Top Tip
                'topTipPri_R0_crv' : [8,  'topTipPri_R0_', -0.125,  priTopJtsR, 'wingTopTip_R0_drv', '__wing_R_top_down', 'wing_R0_membraineN2_drv', arayPri],
                'topTipSec_R0_crv' : [18, 'topTipSec_R0_', -0.125,  secTopJtsR, 'wingTopTip_R0_drv', '__wing_R_top_down', 'wing_R0_membraineN2_drv', araySec],

                #### Left Bot Mid
                'botMidPri_R0_crv' : [8,  'botMidPri_R0_', 0.075,   priBotJtsR, 'wingBotMid_R0_drv', '__wing_R_bot_mid', 'wing_R0_membraineN2_drv', arayPri],
                'botMidSec_R0_crv' : [19, 'botMidSec_R0_', 0.075,   secBotJtsR, 'wingBotMid_R0_drv', '__wing_R_bot_mid', 'wing_R0_membraineN2_drv', araySec],
                #### Left Bot Down
                'botTipPri_R0_crv' : [8,  'botTipPri_R0_', 0.125,   priTopJtsR, 'wingBotTip_R0_drv', '__wing_R_bot_down', 'wing_R0_membraineN2_drv', arayPri],
                'botTipSec_R0_crv' : [18, 'botTipSec_R0_', 0.125,   secTopJtsR, 'wingBotTip_R0_drv', '__wing_R_bot_down', 'wing_R0_membraineN2_drv', araySec],

                

                ############# Tail Main
                'tailPri_C0_crv' : [12, 'tailPri_C0_',  0, ['tail_R0_0_jnt', 'tail_C0_0_jnt', 'tail_L0_0_jnt'], 'tailCenter_C0_drv', '__tail_C_main', 'wing_C0_membraineN2_drv', arayTailC],
               }
########################################################################################################################





# Layout feathers
def build(strapWidth, endJntSize, offDir='.ty'):
    '''
    Build initial heirarchy. Adds visibility attributes.

    strapWidth  = (float) Width of the individual feather strap rigs
    endJntSize  = (float) Radius of the feather section, end feather(s), bfr jnt
    offDir      = (str)   Axis to offset the feather layers, '.ty'=horz, '.tz'=vert

    '''
    if not cmds.ls(sl=1):
        raise IndexError('Select a grow curve.')

    crvLst = []
    for sel in cmds.ls(sl=1):
        if sel in featherDict.keys():
            crvLst.append(sel)
        else:
            print 'Selected object not found in featherDict', sel

    #Build wing heirarchy
    if not cmds.objExists('wingRigRoot'):
        visIco = cmds.createNode('transform', n='wingRigRoot', ss=True)
            #Vis attributes on wingRigRoot

        if not cmds.attributeQuery('__________', node=visIco, ex=True):
            cmds.addAttr(visIco, ln='__________', en='wingVis:', at='enum', ci=True, k=True)

        attrDict = OrderedDict()

        #### TOP
        attrDict['__________L_top_geo'] = 'space'
        attrDict['Geo__wing_L_main'] = ['bool', 1]
        attrDict['Geo__wing_L_top_mid'] = ['bool', 1]
        attrDict['Geo__wing_L_top_down'] = ['bool', 1]

        attrDict['__________L_top_Rig'] = 'space'
        attrDict['Rig__wing_L_main'] = ['bool', 0]
        attrDict['Rig__wing_L_top_mid'] = ['bool', 0]
        attrDict['Rig__wing_L_top_down'] = ['bool', 0]

        attrDict['__________R_top_geo'] = 'space'
        attrDict['Geo__wing_R_main'] = ['bool', 1]
        attrDict['Geo__wing_R_top_mid'] = ['bool', 1]
        attrDict['Geo__wing_R_top_down'] = ['bool', 1]

        attrDict['__________R_top_Rig'] = 'space'
        attrDict['Rig__wing_R_main'] = ['bool', 0]
        attrDict['Rig__wing_R_top_mid'] = ['bool', 0]
        attrDict['Rig__wing_R_top_down'] = ['bool', 0]
        
        ##### BOT
        attrDict['__________L_bot_geo'] = 'space'
        attrDict['Geo__wing_L_main'] = ['bool', 1]
        attrDict['Geo__wing_L_bot_mid'] = ['bool', 1]
        attrDict['Geo__wing_L_bot_down'] = ['bool', 1]

        attrDict['__________L_bot_Rig'] = 'space'
        attrDict['Rig__wing_L_main'] = ['bool', 0]
        attrDict['Rig__wing_L_bot_mid'] = ['bool', 0]
        attrDict['Rig__wing_L_bot_down'] = ['bool', 0]

        attrDict['__________R_bot_geo'] = 'space'
        attrDict['Geo__wing_R_main'] = ['bool', 1]
        attrDict['Geo__wing_R_bot_mid'] = ['bool', 1]
        attrDict['Geo__wing_R_bot_down'] = ['bool', 1]

        attrDict['__________R_bot_Rig'] = 'space'
        attrDict['Rig__wing_R_main'] = ['bool', 0]
        attrDict['Rig__wing_R_bot_mid'] = ['bool', 0]
        attrDict['Rig__wing_R_bot_down'] = ['bool', 0]

        ##### Tail
        attrDict['__________C_tail_geo'] = 'space'
        attrDict['Geo__tail_C_main'] = ['bool', 1]

        attrDict['__________C_tail_Rig'] = 'space'
        attrDict['Rig__tail_C_main'] = ['bool', 0]

        for k,v in attrDict.iteritems():
            if v == 'space':
                if not cmds.attributeQuery(k, node=visIco, ex=True):
                    cmds.addAttr(visIco, ln=k, en='__________', at='enum', ci=True, k=True)
            else:
                if not cmds.attributeQuery(k, node=visIco, ex=True):
                    cmds.addAttr(visIco, ci=True, k=True, at=v[0], sn=k, min=0, max=1, dv=v[1])
    

    traDict = OrderedDict([
                           # Left and Right
                           ('wing_L0_drv', 'wingRigRoot'), ('wing_R0_drv', 'wingRigRoot'), ('tail_C0_drv', 'wingRigRoot'),
                           # Left and Right Main
                           ('wingCenter_L0_drv', 'wing_L0_drv'), ('wingCenter_R0_drv', 'wing_R0_drv'),
                           # Top and Bot
                           ('wingTop_L0_drv', 'wing_L0_drv'), ('wingTop_R0_drv', 'wing_R0_drv'),
                           ('wingBot_L0_drv', 'wing_L0_drv'), ('wingBot_R0_drv', 'wing_R0_drv'),
                           # Mid, Down (TOP)
                           ('wingTopMid_L0_drv', 'wingTop_L0_drv'), ('wingTopTip_L0_drv', 'wingTop_L0_drv'),
                           ('wingTopMid_R0_drv', 'wingTop_R0_drv'), ('wingTopTip_R0_drv', 'wingTop_R0_drv'),
                           # Mid, Down (BOT)
                           ('wingBotMid_L0_drv', 'wingBot_L0_drv'), ('wingBotTip_L0_drv', 'wingBot_L0_drv'),
                           ('wingBotMid_R0_drv', 'wingBot_R0_drv'), ('wingBotTip_R0_drv', 'wingBot_R0_drv'),
                           # Tail
                           ('tailCenter_C0_drv', 'tail_C0_drv'),
                           ])
    for k,v in traDict.iteritems():
        if cmds.objExists(k):
            # Reparent
            if cmds.listRelatives(k, p=True) == None:
                cmds.parent(k,v)
        else:
            cmds.createNode('transform', n=k, p=v, ss=True)


    #Create feather rows from curve(s)
    if crvLst != []:
        for curve in crvLst:
            rigu.lockUnlockSRT2([curve], 1, 0)
            cmds.makeIdentity(curve, apply=True,t=1, r=1, s=1, n=0, pn=1)
            dictItem = featherDict.get(curve)
            count    = dictItem[0]
            name     = dictItem[1]
            offset   = dictItem[2]
            crvJts   = dictItem[3]
            parGrp   = dictItem[4]
            visAttr  = dictItem[5]
            wingSrf  = dictItem[6]

            buildFeathers(curve=curve, name=name, count=count,
                            wingSrf=wingSrf, offset=offset, offDir=offDir, crvJts=crvJts,
                            parGrp=parGrp, visAttr=visAttr, strapWidth=strapWidth, endJntSize=endJntSize)

   
    cmds.select(None)

def buildFeathers(curve, name, count, wingSrf, offset, offDir, crvJts, parGrp, visAttr, strapWidth, endJntSize):
    '''
    curve = Name of selected curve
    name  = dict item, name to give system
    count = number of feathers
    wingSrf = name of nurbs membraine surface
    offset  = offset the feathers from membraine surface, for layering
    offDir  = direction to offset the feathers from membraine surface
    crvJts  = list of joints to weight the new system curve to
    parGrp  = group to parent under
    visAttr = attribute on 'wingRigRoot'
    strapWidth = width of the feather strap surface
    endJntSize = size of the placement joints on curve ends 
    '''


    #random feather (1)
    dictItem = featherDict.get(curve)
    #groups
    grp = cmds.createNode('transform', n=name+'grp', ss=True)
    geoGrp = cmds.createNode('transform', n=name+'geo', p=grp, ss=True)
    rigGrp = cmds.createNode('transform', n=name+'strap', p=grp, ss=True)
    rootGrp = cmds.createNode('transform', n=name+'root', p=grp, ss=True)
    cmds.setAttr(rigGrp+'.v', 0)
    #itentification attrs
    cmds.addAttr(grp, ci=True, at='bool',   sn='isFeatherGrp', min=1, max=1, k=False)
    #geo and strap rig vis
    cmds.addAttr(grp, ci=True, at='bool', sn='featherGeoVis', min=0, max=1, dv=1, k=True)
    cmds.addAttr(grp, ci=True, at='bool', sn='featherRigVis', min=0, max=1, dv=0, k=True)
    cmds.connectAttr(grp+'.featherGeoVis', geoGrp+'.v')
    cmds.connectAttr(grp+'.featherRigVis', rigGrp+'.v')
    cmds.connectAttr('wingRigRoot.Geo'+visAttr, grp+'.featherGeoVis')
    cmds.connectAttr('wingRigRoot.Rig'+visAttr, grp+'.featherRigVis')
    #feather roots
    fCtlRef = crv.createEvenAlongCrv(objType='joint', objName=name, count=count, crvName=curve, keepCrv=1, suffix='ctlRef', lra=False)
    [cmds.setAttr(jnt+'.drawStyle', 2) for jnt in fCtlRef]
    cmds.parent(fCtlRef, rootGrp)
    [srf.constToSrfMatrix(ref, wingSrf, translate=False) for ref in fCtlRef]
    #duplicate build curve (smooth) to constrain joint positions
    cnsCrv = cmds.rebuildCurve(curve, rt=0, ch=1, end=1, d=3, kr=0, s=6, kcp=0, tol=0.01, kt=0, rpo=0, kep=1)[0]
    cmds.setAttr(cnsCrv+'.v', 0)
    cmds.delete(cnsCrv, ch=True)
    cmds.parent(cnsCrv, grp)
    crv.consToCrvParametric(fCtlRef, cnsCrv, rotate=False)
    crvSkn = cmds.skinCluster(crvJts, cnsCrv, mi=2, bm=0, sm=0, dr=4, wd=0, tsb=1, n=name+'_featherSkin')[0]
    #feather buffer
    fBfr = crv.createEvenAlongCrv(objType='joint', objName=name, count=count, crvName=curve, keepCrv=1, suffix='bfr', lra=False)
    [cmds.setAttr(f+'.radius', endJntSize) for f in fBfr]
    #increment count
    incCount = count-1
    inc = 1.0/incCount

    for i,loc in enumerate(fBfr[:-1]): # Need to have last item separate to avoid self constraint cycle
        
        #random feather (2)
        feather = random.choice(dictItem[7])
        edgLst   = featherEdgeDict[feather]
        #side
        side = curve.split('_')[0][-3:]

        if i != 0:
            cmds.setAttr(loc+'.drawStyle', 2)
            weight = inc*i
            
            #parent constrain by increment
            parCons = cmds.parentConstraint(fBfr[0], fBfr[-1], loc, st=['x','y','z'], weight=1)
            cmds.setAttr(parCons[0]+'.'+cmds.listAttr(parCons[0])[-1], weight)
            cmds.setAttr(parCons[0]+'.'+cmds.listAttr(parCons[0])[-2], 1.0-weight)
            
            #scale constrain by increment
            sclCons = cmds.scaleConstraint(fBfr[0], fBfr[-1], loc, weight=1)
            cmds.setAttr(sclCons[0]+'.'+cmds.listAttr(sclCons[0])[-1], weight)
            cmds.setAttr(sclCons[0]+'.'+cmds.listAttr(sclCons[0])[-2], 1.0-weight)

            #create feather geo
            rigu.lockUnlockSRT2([feather], 1, 0)
            fthrDup = cmds.duplicate(feather)[0]
            # cmds.refresh()
            fthr = cmds.rename(fthrDup, fthrDup+'_fthr')
            cmds.delete(fthr, ch=True)
            cmds.setAttr(fthr+'.v', 1)
            
            #feather type attr for skincluster import
            cmds.addAttr(fthr, ci=True, dt='string', sn='featherType')
            cmds.setAttr(fthr+'.featherType', feather, type='string')

            #parent and zero out
            cmds.parent(fthr, loc)
            [cmds.setAttr(fthr+attr, 0) for attr in ['.tx', '.ty', '.tz', '.rx', '.ry', '.rz']]

            #parent ctlRef to group
            cmds.parent(loc, grp)

            #offset
            cmds.setAttr(loc+offDir, cmds.getAttr(loc+offDir)+offset)
            
            #create feather strap srf
            surface = strapSrf(fthr, edgLst, strapWidth)
            cmds.setAttr(surface+'.v', 0)
            cmds.parent(surface, loc)

           
        else:
            if side == 'Sec':
                cmds.color(loc, rgb=(0.0, 0.647, 0.0))
                cmds.setAttr(loc+'.radius', endJntSize+0.02)
            else:
                cmds.color(loc, rgb=(1.0, 0.2, 0.0))
            #feather geo
            rigu.lockUnlockSRT2([feather], 1, 0)
            fthrDup = cmds.duplicate(feather)[0]
            # cmds.refresh()
            fthr = cmds.rename(fthrDup, fthrDup+'_fthr')
            cmds.delete(fthr, ch=True)
            cmds.setAttr(fthr+'.v', 1)
            cmds.parent(fthr, loc)
            [cmds.setAttr(fthr+attr, 0) for attr in ['.tx', '.ty', '.tz', '.rx', '.ry', '.rz']]

            #feather type attr for skincluster import
            cmds.addAttr(fthr, ci=True, dt='string', sn='featherType')
            cmds.setAttr(fthr+'.featherType', feather, type='string')
            
            #parent ctlRef to group
            cmds.parent(loc, grp)
            
            #offset
            cmds.setAttr(loc+offDir, cmds.getAttr(loc+offDir)+offset)

            #create feather strap srf
            surface = strapSrf(fthr, edgLst, strapWidth)
            cmds.setAttr(surface+'.v', 0)
            cmds.parent(surface, loc)


    # last locator in list
    loc = fBfr[-1]
    if side == 'Sec':
        cmds.color(loc, rgb=(0.0, 0.647, 0.0))
        cmds.setAttr(loc+'.radius', endJntSize+0.02)
    else:
        cmds.color(loc, rgb=(1.0, 0.2, 0.0))
    
    #Feather geo
    rigu.lockUnlockSRT2([feather], 1, 0)
    fthrDup = cmds.duplicate(feather)[0]
    # cmds.refresh()
    fthr = cmds.rename(fthrDup, fthrDup+'_fthr')
    cmds.delete(fthr, ch=True)
    cmds.setAttr(fthr+'.v', 1)

    #feather type attr for skincluster import
    cmds.addAttr(fthr, ci=True, dt='string', sn='featherType')
    cmds.setAttr(fthr+'.featherType', feather, type='string')

    #parent and zero out
    cmds.parent(fthr, loc)
    [cmds.setAttr(fthr+attr, 0) for attr in ['.tx', '.ty', '.tz', '.rx', '.ry', '.rz']]

    #parent ctlRef to group
    cmds.parent(loc, grp)
    
    #offset
    cmds.setAttr(loc+offDir, cmds.getAttr(loc+offDir)+offset)

    #create feather strap srf
    surface = strapSrf(fthr, edgLst, strapWidth)
    cmds.setAttr(surface+'.v', 0)
    cmds.parent(surface, loc)

    for i,loc in enumerate(fBfr):
        cmds.parent(loc, fCtlRef[i])

    #parent the grp
    cmds.parent(grp, parGrp)


# Rig Feathers
def rig(dorNum, ctlSize, wgtFile=None):
    '''
    wingSrf = (str) Name of nurbs surface to constrain feathers to
    dorNum  = (int) Number of dorito joints (used to skin feather)
    wgtFile = (str) Path to feather skin weight file (json exported from Deform > Export Weights)
    '''
    for grp in cmds.ls(sl=1):#feather_grp transform(s)
        if cmds.attributeQuery('isFeatherGrp', node=grp, ex=True) == False:
            cmds.warning('Selection is not top transform of _grp')
        else:
            #Get membrain obj
            key = grp.replace('_grp', '_crv')
            wingSrf = featherDict[key][6]
            removeConstraints(grp)
            rigFeathers(grp=grp, wingSrf=wingSrf, dorNum=dorNum, ctlSize=ctlSize, wgtFile=wgtFile)

def rigFeathers(grp, wingSrf, dorNum, ctlSize, wgtFile=None):
    '''
    grp     = (str) Name of feather grp, that has isFeatherGrp attr
    wingSrf = (str) Name of nurbs surface to constrain feather to
    dorNum  = (int) Number of dorito joints (used to skin feather)
    ctlSize = (float) Size of the rdCtls on feather strap rig
    wgtFile = (str) Path to feather skin weight file (json exported from Deform > Export Weights)
    '''
    

    #Import feather weights
    if wgtFile != None:
        with open(wgtFile) as f:
            data = f.read()
            json_data = json.loads(data)#convert string to dict  
            f.close()

    #get strap drv's
    nrbDrv = []
    nrbDrv = [nrb for nrb in cmds.listRelatives(grp, ad=True) if nrb.endswith('_drv')]
    if nrbDrv != []:
        name = '_'.join(grp.split('_')[:2])
        #get groups
        geo = [i for i in cmds.listRelatives(grp, c=True) if i.endswith('_geo')][0]
        root = [i for i in cmds.listRelatives(grp, c=True) if i.endswith('_root')][0]
        strap = [i for i in cmds.listRelatives(grp, c=True) if i.endswith('strap')][0]
        strapDrv = cmds.createNode('transform', n=name+'_strapDrv', p=grp)
        cmds.setAttr(root+'.v', 0)
        #strap drv cv's
        cvList = ['.cv[0][1]', '.cv[1][1]', '.cv[2][1]', '.cv[3][1]', '.cv[4][1]', '.cv[5][1]']
        
        for nrb in nrbDrv:
            #get feather
            bfr = cmds.listRelatives(nrb, p=True)[0]
            ref = cmds.listRelatives(bfr, p=True)[0]
            fthr = None
            fthr = [i for i in cmds.listRelatives(bfr, c=True) if i.endswith('_fthr')][0]
            #prepSrf
            cmds.parent(nrb, w=True)
            cmds.setAttr(nrb+'.v', 1)
            newSrf = cmds.rebuildSurface(nrb, rt=0, kc=0, fr=0, ch=1, end=1, sv=0, su=0, kr=0, dir=2, kcp=0, tol=0.01, dv=2, du=2, rpo=0)[0]
            cmds.ToggleSurfaceOrigin(newSrf)

            cmds.reverseSurface(newSrf, d=3, ch=0, rpo=1)
            cmds.reverseSurface(newSrf, d=1, ch=0, rpo=1)

            cmds.delete(nrb)
            newSrf = cmds.rename(newSrf, nrb)
            cmds.setAttr(newSrf+'.v', 0)

            #feather rig
            surface = None
            surface = strapRig(newSrf, dorNum, ctlSize)
            cmds.setAttr(surface[0]+'.v', 0)
            cmds.parent(surface[2], strap)
            #global scale ctlRef (below)
            ctlRef = [c.topCtl.replace('_ctl', '_ctlRef') for c in surface[1]]

            #dorito joints
            dorJts = []
            dorJts = [i for i in cmds.listRelatives(surface[0], c=True) if i.endswith('_jnt')]
            [cmds.setAttr(jnt+'.v', 0) for jnt in dorJts]
            cmds.delete(fthr, ch=True)
            cmds.parent(fthr, geo)
            cmds.makeIdentity(fthr, apply=True, t=1, r=1, s=1, n=0, pn=1)

            
            fthrSkin = cmds.skinCluster(dorJts, fthr, mi=2, bm=0, sm=0, dr=4, wd=0, tsb=1, n=name+'_featherSkin')[0]
            # Import weights for feather
            if wgtFile != None:
                fthNme = fthr.split('_')[0]
                fthIdx = fthr.split('_')[1]

                x = {} # new dict for skinPercent to read
                for d in json_data['deformerWeight']['weights']:#list of dictionaries (d)
                    jnt = d['source']# joint name
                    jnt = fthNme+'_'+fthIdx+'_'+'_'.join(jnt.split('_')[2:]) # switch jnt name to current feather name
                    for d in d['points']:
                        vtxIdx = d['index']# vertex ID
                        wght   = d['value']# joint weight
                        if vtxIdx not in x:
                            x[vtxIdx] = list()
                        x[vtxIdx].append((jnt, wght))
                        cmds.skinPercent(fthrSkin, fthr+'.vtx[{}]'.format(vtxIdx), normalize=True, tv=x[vtxIdx])


            # global scale dorito jnts
            globalScale(dorJts)

            #constrain rig to wing srf
            jntGrp = cmds.createNode('transform', n=name+'_sDrv', p=strapDrv)
            drvJts = []
            offJts = []
            #rig driver joints, with offset constraint to wingSrf
            for i,cv in enumerate(cvList):
                pos = cmds.xform(newSrf+cv, q=True, ws=True, t=True)
                jnt = cmds.createNode('joint', n=newSrf+str(i)+'_cns')
                off = cmds.createNode('transform', n=newSrf+str(i)+'_off')
                cmds.xform(jnt, ws=True, t=pos)
                cmds.xform(off, ws=True, t=pos)
                cmds.setAttr(jnt+'.radius', 0.1)
                cmds.setAttr(off+'.v', 0)
                #constrain to wingSrf
                srf.constToSrfMatrix(off, wingSrf)
                # if i < 3: #constrain first 3 offsets to linear membraine
                #     srf.constToSrfMatrix(off, wingSrf.replace('N2_', 'N1_'))
                # else:
                #     srf.constToSrfMatrix(off, wingSrf)
                cmds.parent(jnt, off)
                [cmds.setAttr(jnt+a, 0) for a in ['.tx', '.tz']]
                cmds.parent(off, jntGrp)
                drvJts.append(jnt)
                offJts.append(off)
            globalScale(offJts)
            drvJts.append(ref)
            
            #strap drv skin
            strapSkn = cmds.skinCluster(drvJts, newSrf, mi=2, bm=0, sm=0, dr=4, wd=0, tsb=1, n=name+'_wingSrfSkin')[0]
            globalScale(ctlRef)
            globalScale([ref])

            #delete bfr
            cmds.delete(bfr)


# Utils
def strapRig(srf, dorNum, ctlSize):
    '''
    srf    = (str) Name of nurbs surface to build rig with
    dorNum = (int) Number of dorito joints (used to skin feather)
    '''
    a = None
    a = strap.Strap()
    a.buildGuide(srf, rows=1, columns=3, skipLast=False)
    a.buildRig(srf, jntRows=1, jntColumns=dorNum, skipLast=True, ctlShape='circleV', ctlSize=ctlSize, ctlColor=1, 
                          ctlSuffix='ctl', jntSuffix='jnt', makeFK=True, ikSpline=False, ikSplineNum=0, 
                          margin=0.1, lra='x')

    # Set smooth skin weights on dorito nurbs srf
    clst = skn.getSkinClusters(a.dorSrf[0])
    infl = skn.getSkinClusterInfluences(clst)

    cmds.skinPercent(clst, a.dorSrf[0]+'.cv[0]', transformValue=[(infl[0], 1.0)])
    cmds.skinPercent(clst, a.dorSrf[0]+'.cv[1]', transformValue=[(infl[0], 1.0)])
    cmds.skinPercent(clst, a.dorSrf[0]+'.cv[2]', transformValue=[(infl[0], 1.0)])

    cmds.skinPercent(clst, a.dorSrf[0]+'.cv[3]', transformValue=[(infl[0], 0.935), (infl[1], 0.065)])
    cmds.skinPercent(clst, a.dorSrf[0]+'.cv[4]', transformValue=[(infl[0], 0.935), (infl[1], 0.065)])
    cmds.skinPercent(clst, a.dorSrf[0]+'.cv[5]', transformValue=[(infl[0], 0.935), (infl[1], 0.065)])

    cmds.skinPercent(clst, a.dorSrf[0]+'.cv[6]', transformValue=[(infl[0], 0.413), (infl[1], 0.587)])
    cmds.skinPercent(clst, a.dorSrf[0]+'.cv[7]', transformValue=[(infl[0], 0.413), (infl[1], 0.587)])
    cmds.skinPercent(clst, a.dorSrf[0]+'.cv[8]', transformValue=[(infl[0], 0.413), (infl[1], 0.587)])

    cmds.skinPercent(clst, a.dorSrf[0]+'.cv[9]',  transformValue=[(infl[0], 0.290), (infl[1], 0.478), (infl[2], 0.232)])
    cmds.skinPercent(clst, a.dorSrf[0]+'.cv[10]', transformValue=[(infl[0], 0.290), (infl[1], 0.478), (infl[2], 0.232)])
    cmds.skinPercent(clst, a.dorSrf[0]+'.cv[11]', transformValue=[(infl[0], 0.290), (infl[1], 0.478), (infl[2], 0.232)])

    cmds.skinPercent(clst, a.dorSrf[0]+'.cv[12]', transformValue=[(infl[1], 0.180), (infl[2], 0.820)])
    cmds.skinPercent(clst, a.dorSrf[0]+'.cv[13]', transformValue=[(infl[1], 0.180), (infl[2], 0.820)])
    cmds.skinPercent(clst, a.dorSrf[0]+'.cv[14]', transformValue=[(infl[1], 0.180), (infl[2], 0.820)])

    cmds.skinPercent(clst, a.dorSrf[0]+'.cv[15]', transformValue=[(infl[1], 0.010), (infl[2], 0.990)])
    cmds.skinPercent(clst, a.dorSrf[0]+'.cv[16]', transformValue=[(infl[1], 0.010), (infl[2], 0.990)])
    cmds.skinPercent(clst, a.dorSrf[0]+'.cv[17]', transformValue=[(infl[1], 0.010), (infl[2], 0.990)])



    return a.dorSrf[0], a.dorSrf[1], a.dorSrf[2]  # a.dorSrf = [doritoSurface, [controls], control grp]

def strapSrf(feather, edgLst, strapWidth):
    edgNme = [feather+'.e['+str(edge)+']' for edge in edgLst]
    cmds.select(None)
    cmds.select(edgNme, add=True)
    curve = cmds.polyToCurve(form=2,  degree=3, conformToSmoothMeshPreview=1)
    curve1 = cmds.rebuildCurve(ch=1, rpo=0, rt=0, end=1, kr=0, kcp=0, kep=0, kt=0, s=2, d=1, tol=0.01, name="testCrv")
    surface = srf.loftCrvs(curve1, strapWidth, 'x', feather+'_srf', keepCrv=0)
    prepSrf = srf.nurbsSrfPrep(create=0, srfName=surface)
    cmds.setAttr(prepSrf+'.v', 0)


    cmds.reverseSurface(prepSrf, d=3, ch=0, rpo=1)
    cmds.reverseSurface(prepSrf, d=1, ch=0, rpo=1)

    cmds.delete(prepSrf, ch=True)

    cmds.delete(curve1)
    cmds.delete(curve)
    newSrf = cmds.rename(prepSrf, feather.replace('_fthr', '_drv'))
    cmds.select(None)

    return newSrf

def importSkinWeights(obj, fthrType, xmls=None):
    '''
    obj      = (str) Obj to apply skincluster
    fthrType = (str) Feather template name

    '''
    path = r'D:/Working/Maya/wingFeathers/elements/weights/xml/templates/'
    weightFile  = fthrType+'.xml'
    skinFileXML = xml.etree.ElementTree.parse(path+weightFile)
    influences = []
    for elem in skinFileXML.findall('weights'):
        jnt = elem.get('source')
        influences.append(jnt)

    
    #get name of feather obj
    fthrName = obj.split('_')[0]
    #replace feather name in influences
    newInf = [fthrName+'_'+'_'.join(inf.split('_')[1:]) for inf in influences]
    # Make sure influences exists
    sknInfl = []
    for jnt in newInf:
        if cmds.objExists(jnt):
            sknInfl.append(jnt)

    
    if cmds.objExists(obj) and sknInfl != []:
        # Check for existing skinCluster
        if skn.getSkinClusters(obj):
            currSkin = skn.getSkinClusters(obj)
            currInfl = skn.getSkinClusterInfluences(currSkin)
            # add any missing joints to current skinCluster
            toAdd = [x for x in sknInfl if x not in currInfl]
            if toAdd:
                cmds.skinCluster(currSkin, e=1, ai=toAdd , lw=1, wt=0)
            # load skin weights
            cmds.deformerWeights(weightFile, path=path, im=1, df=currSkin, m='index')
            [cmds.setAttr(infs + '.liw', 0) for infs in cmds.skinCluster(currSkin, q=1, inf=1)]
            cmds.skinPercent(currSkin, obj, nrm=1)
        else:
            skin = cmds.skinCluster(obj, sknInfl, tsb=1)[0]
            cmds.deformerWeights(weightFile, path=path, im=1, df=skin, m='index')
            cmds.skinPercent(skin, obj, nrm=1)
    else:
        print obj, '<'*80
        cmds.warning('Skin object does not exist in the scene')

def removeConstraints(grp):
    cons= []
    for cn in cmds.listRelatives(grp, ad=True):
        if cmds.objectType(cn) == 'parentConstraint':
            cons.append(cn)
        if cmds.objectType(cn) == 'scaleConstraint':
            cons.append(cn)

    if cons != []:
        cmds.delete(cons)

def globalScale(itemLst):
    if cmds.objExists('global_C0_ctl'):
        gblObj = 'global_C0_ctl'
        ax = ['.sx','.sy','.sz']
        if cmds.attributeQuery('globalScale', node=gblObj, ex=True):
            for item in itemLst:
                sclAxs = ['.sx', '.sy', '.sz']
                [cmds.connectAttr(gblObj+'.globalScale', item+axis) for axis in sclAxs]

def mirrorSelBfr(sel):
    '''
    Select bfr(s) on Right side.

    sel = ([]) Selection of bfr object from right wing
    '''

    [removeConstraints(i) for i in cmds.ls(sl=1)]
    for i in pm.ls(sl=1):
        if i.endswith('_bfr'):
            mirrNme = i.replace('_R0_', '_L0_')
            mirrCtl = pm.PyNode(mirrNme)
            mirrMat = tra.getTransform(mirrCtl)
            newMat  = tra.getSymmetricalTransform(mirrMat, axis="yz", fNegScale=False)
            tra.setTransformFromMatrix(newMat, i)

def reSkinCnsCrv():
    for k,v in featherDict.iteritems():
        if cmds.objExists(k+'rebuiltCurve1'):
            crvNme = k+'rebuiltCurve1'
            name = v[1]
            jts  = v[3]

            skins  = []
            shapes = []
            shapes = cmds.listRelatives(crvNme, shapes=True)
            if shapes != []:
                for s in shapes:
                    history = cmds.listHistory(s, pruneDagObjects=True, il=2) or []
                    skin = [x for x in history if cmds.nodeType(x) == 'skinCluster']
                    if skin:
                        skins.append(skin)
            
            if skins == []:
                cmds.skinCluster(jts, crvNme, mi=2, bm=0, sm=0, dr=4, wd=0, tsb=1, n=name+'_featherSkin')





def buildMembraine():
    memDictL = {'scapulaMaster_L0_0_jnt': '.cv[0][0]',
                'scapulaMaster_L0_1_jnt': '.cv[0][1]',
                'scapulaMaster_L0_2_jnt': '.cv[0][2]',
                'scapulaMaster_L0_3_jnt': '.cv[0][3]',
                
                'tertialMaster_L0_0_jnt': '.cv[1][0]',
                'tertialMaster_L0_1_jnt': '.cv[1][1]',
                'tertialMaster_L0_2_jnt': '.cv[1][2]',
                'tertialMaster_L0_3_jnt': '.cv[1][3]',
                
                'secondaryMaster_L0_0_jnt': '.cv[2][0]',
                'secondaryMaster_L0_1_jnt': '.cv[2][1]',
                'secondaryMaster_L0_2_jnt': '.cv[2][2]',
                'secondaryMaster_L0_3_jnt': '.cv[2][3]',
                
                'primaryMid_L0_0_jnt': '.cv[3][0]',
                'primaryMid_L0_1_jnt': '.cv[3][1]',
                'primaryMid_L0_2_jnt': '.cv[3][2]',
                'primaryMid_L0_3_jnt': '.cv[3][3]',
                
                'primaryMaster_L0_0_jnt': '.cv[4][0]',
                'primaryMaster_L0_1_jnt': '.cv[4][1]',
                'primaryMaster_L0_2_jnt': '.cv[4][2]',
                'primaryMaster_L0_3_jnt': '.cv[4][3]',
               }

    memDictR = {'scapulaMaster_R0_0_jnt': '.cv[0][0]',
                'scapulaMaster_R0_1_jnt': '.cv[0][1]',
                'scapulaMaster_R0_2_jnt': '.cv[0][2]',
                'scapulaMaster_R0_3_jnt': '.cv[0][3]',
                
                'tertialMaster_R0_0_jnt': '.cv[1][0]',
                'tertialMaster_R0_1_jnt': '.cv[1][1]',
                'tertialMaster_R0_2_jnt': '.cv[1][2]',
                'tertialMaster_R0_3_jnt': '.cv[1][3]',
                
                'secondaryMaster_R0_0_jnt': '.cv[2][0]',
                'secondaryMaster_R0_1_jnt': '.cv[2][1]',
                'secondaryMaster_R0_2_jnt': '.cv[2][2]',
                'secondaryMaster_R0_3_jnt': '.cv[2][3]',
                
                'primaryMid_R0_0_jnt': '.cv[3][0]',
                'primaryMid_R0_1_jnt': '.cv[3][1]',
                'primaryMid_R0_2_jnt': '.cv[3][2]',
                'primaryMid_R0_3_jnt': '.cv[3][3]',
                
                'primaryMaster_R0_0_jnt': '.cv[4][0]',
                'primaryMaster_R0_1_jnt': '.cv[4][1]',
                'primaryMaster_R0_2_jnt': '.cv[4][2]',
                'primaryMaster_R0_3_jnt': '.cv[4][3]',
               }

    memDictC = {'tail_R0_0_jnt': '.cv[0][0]',
                'tail_R0_1_jnt': '.cv[0][1]',
                'tail_R0_2_jnt': '.cv[0][2]',
                'tail_R0_3_jnt': '.cv[0][3]',
                
                'tail_C0_0_jnt': '.cv[1][0]',
                'tail_C0_1_jnt': '.cv[1][1]',
                'tail_C0_2_jnt': '.cv[1][2]',
                'tail_C0_3_jnt': '.cv[1][3]',
                
                'tail_L0_0_jnt': '.cv[2][0]',
                'tail_L0_1_jnt': '.cv[2][1]',
                'tail_L0_2_jnt': '.cv[2][2]',
                'tail_L0_3_jnt': '.cv[2][3]',

                   }

    for dic, side in zip([memDictL, memDictR, memDictC], ['L', 'R', 'C']):
        if cmds.objExists(list(dic.keys())[0]): #If rig (joint) is present
            #Create Nurbs
            if dic == memDictC: #tail
                n1 =cmds.nurbsPlane(ch=1, d=1, v=3, p=(0, 0, 0), u=2, w=0.1, ax=(0, 1, 0), lr=1)[0]
            else:
                n1 = cmds.nurbsPlane(ch=0, d=1, v=3, p=(0, 0, 0), u=4, w=0.1, ax=(0, 1, 0), lr=1)[0]
            
            #Move cv's to match joint pos
            for k,v in dic.items():
                pos = cmds.xform(k, q=True, t=True, ws=True)
                cmds.xform(n1+v, t=pos, ws=True)

            #Set skinweights to 100% per jnt
            cmds.skinCluster(list(dic.keys()), n1, mi=2, bm=0, sm=0, dr=4, wd=0, tsb=1, n='wing_'+side+'0_membraineN1_skn')
            for k,v in dic.items():
                cmds.skinPercent('wing_'+side+'0_membraineN1_skn', n1+v, transformValue=[(k, 1.0)])

            #Convert to smooth nurbs
            n2 = cmds.rebuildSurface(n1, rt=0, kc=0, fr=0, ch=1, end=1, sv=0, su=0, kr=0, dir=2, kcp=1, tol=0.01, dv=2, du=2, rpo=0)[0]
            cmds.delete(n2, ch=True)
            cmds.skinCluster(list(dic.keys()), n2, mi=2, bm=0, sm=0, dr=4, wd=0, tsb=1, n='wing_'+side+'0_membraineN2_skn')
            for k,v in dic.items():
                cmds.skinPercent('wing_'+side+'0_membraineN1_skn', n1+v, transformValue=[(k, 1.0)])
            #cmds.copySkinWeights(ss='wing_'+side+'0_membraineN1_skn', ds='wing_'+side+'0_membraineN2_skn', noMirror=True)
            cmds.select(None)

            #Clean up
            cmds.parent(n1, n2, 'wingFeatherBuilder')
            cmds.setAttr(n1+'.v', 0)
            cmds.rename(n1, 'wing_'+side+'0_membraineN1_drv')
            cmds.rename(n2, 'wing_'+side+'0_membraineN2_drv')
        else:
            cmds.warning('Rig is not present? Cannot build a membraine')

    cmds.select(None)


def buildHeirarchy():
    hDict = OrderedDict()

    hDict['wingFeatherBuilder'] = None
    hDict['featherTemplates'  ] = 'wingFeatherBuilder'
    hDict['wingGrowCurves' ]    = 'wingFeatherBuilder'

    hDict['wing_L0_crvGrp' ]   = 'wingGrowCurves'

    hDict['wingCenter_L0_crvGrp'] = 'wing_L0_crvGrp'
    hDict['wingTop_L0_crvGrp']    = 'wing_L0_crvGrp'
    hDict['wingBot_L0_crvGrp']    = 'wing_L0_crvGrp'
    
    for tra,par in hDict.iteritems():
        if not cmds.objExists(tra):
            cmds.createNode('transform', n=tra, p=par, ss=True)

def buildCurves():
    cDict = OrderedDict()
    
    # Left Center
    cDict['centerPri_L0_crv'] = ['wingCenter_L0_crvGrp', ['secondaryMaster_L0_0_jnt', 'primaryMaster_L0_0_jnt']]
    cDict['centerSec_L0_crv'] = ['wingCenter_L0_crvGrp', ['scapulaMaster_L0_0_jnt', 'tertialMaster_L0_0_jnt', 'secondaryMaster_L0_0_jnt']]

    # Left Top
    cDict['topMidPri_L0_crv'] = ['wingTop_L0_crvGrp', ['secondaryMaster_L0_0_jnt', 'primaryMaster_L0_0_jnt']]
    cDict['topMidSec_L0_crv'] = ['wingTop_L0_crvGrp', ['scapulaMaster_L0_0_jnt', 'tertialMaster_L0_0_jnt', 'secondaryMaster_L0_0_jnt']]

    cDict['topTipPri_L0_crv'] = ['wingTop_L0_crvGrp', ['secondaryMaster_L0_0_jnt', 'primaryMaster_L0_0_jnt']]
    cDict['topTipSec_L0_crv'] = ['wingTop_L0_crvGrp', ['scapulaMaster_L0_0_jnt', 'tertialMaster_L0_0_jnt', 'secondaryMaster_L0_0_jnt']]

    # Left Bottom
    cDict['botMidPri_L0_crv'] = ['wingBot_L0_crvGrp', ['secondaryMaster_L0_0_jnt', 'primaryMaster_L0_0_jnt']]
    cDict['botMidSec_L0_crv'] = ['wingBot_L0_crvGrp', ['scapulaMaster_L0_0_jnt', 'tertialMaster_L0_0_jnt', 'secondaryMaster_L0_0_jnt']]

    cDict['botTipPri_L0_crv'] = ['wingBot_L0_crvGrp', ['secondaryMaster_L0_0_jnt', 'primaryMaster_L0_0_jnt']]
    cDict['botTipSec_L0_crv'] = ['wingBot_L0_crvGrp', ['scapulaMaster_L0_0_jnt', 'tertialMaster_L0_0_jnt', 'secondaryMaster_L0_0_jnt']]

    for curve , values in cDict.iteritems():
        if cmds.objExists(values[1][0]):
            if len(values[1]) == 2:
                p0 = cmds.xform(values[1][0], q=True, t=True, ws=True)
                p1 = cmds.xform(values[1][1], q=True, t=True, ws=True)
                growCurve = cmds.curve(p=[p0, p1], k=[0, 1], d=1, n=curve)
                cmds.parent(growCurve, values[0])
            if len(values[1]) == 3:
                p0 = cmds.xform(values[1][0], q=True, t=True, ws=True)
                p1 = cmds.xform(values[1][1], q=True, t=True, ws=True)
                p2 = cmds.xform(values[1][2], q=True, t=True, ws=True)
                growCurve = cmds.curve(p=[p0, p1, p2], k=[0, 1, 2], d=1, n=curve)
                cmds.parent(growCurve, values[0])

        else:
            cmds.warning('Rig is not present? Cannot build curves')

    # Tail Curve
    if not cmds.objExists('tailPri_C0_crv'):
        if cmds.objExists('wing_C0_membraineN2_drv'):
            tailPly = cmds.nurbsToPoly('wing_C0_membraineN2_drv', uss=1, ch=1, ft=0.01, d=0.1, pt=0, f=3, mrt=0, mel=0.001, 
                                        ntr=0, vn=3, pc=21, chr=0.9, un=3, vt=1, ut=1, ucr=0, cht=0.2, mnd=1, es=0, uch=0)[0]
            cmds.select(tailPly+'.e[0]', r=True)
            cmds.select(tailPly+'.e[10]', tgl=True)
            tailCrv = cmds.polyToCurve(conformToSmoothMeshPreview=1, degree=3, form=2)[0]
            cmds.delete(tailPly)
            cmds.parent(tailCrv, 'wingGrowCurves')
            cmds.rename(tailCrv, 'tailPri_C0_crv')



def featherTemplateImport():
    objDir = r'D:/Working/cmlib/mGear/templateGeo/feathers/'
    onlyfiles = [f for f in listdir(objDir) if isfile(join(objDir, f))]

    objLst = []
    if onlyfiles != []:
        for f in onlyfiles:
            if f.endswith('.ma'):
                objLst.append(f)
    
    # MA
    if objLst != []:
        for o in objLst:
            # See if obj exists
            if not cmds.objExists(o[:-3]): #name-.ma
                importObj = cmds.file(objDir+o, pr=1, ignoreVersion=1, i=1, type="mayaAscii", namespace=":", importTimeRange="combine", ra=True, rdn=1, mergeNamespacesOnClash=True, options="v=1")
                objNme = importObj.split('/')[-1].replace('.ma', '')
                cmds.parent(objNme, 'featherTemplates')
                cmds.setAttr(objNme+'.v', 0)

    # OBJ
    # if objLst != []:
    #     for o in objLst:
    #         # See if obj exists
    #         if not cmds.objExists(o[:-3]): #name-.ma
    #             importObj = cmds.file(objDir+o, i = True, returnNewNodes=True, type="OBJ")[0]
    #             cmds.parent(importObj, 'featherTemplates')
    #             newNme = cmds.rename(importObj[1:], o[:-4])
    #             cmds.setAttr(newNme+'.v', 0)



def buildBuilders():
    buildHeirarchy()
    buildMembraine() #Membraine before Curves
    buildCurves()
    featherTemplateImport()
    cmds.select(None)