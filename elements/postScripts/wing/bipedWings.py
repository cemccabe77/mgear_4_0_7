import maya.cmds as cmds
import mgearUtils as mgu
import rigUtils as rigu

rigRoot = mgu.getRigRoot()[0][0]

# L Wing tertial master constraint
lTirMstr = 'wing_L0_div6_loc|tertialMaster_L0_root'
if cmds.objExists(lTirMstr):
	lTirBlnd = cmds.createNode('transform', n='tertialMasterBlend_L0_drv', p='wing_L0_div6_loc', ss=True)
	cmds.parentConstraint('wing_L0_5_jnt', 'wing_L0_7_jnt', lTirBlnd, st=["x","y","z"])
	cmds.parentConstraint('wing_L0_6_jnt', lTirBlnd, sr=["x","y","z"])
	cmds.parentConstraint(lTirBlnd, lTirMstr, st=["x","z"], mo=True)

# R Wing tertial master constraint
rTirMstr = 'wing_R0_div6_loc|tertialMaster_R0_root'
if cmds.objExists(rTirMstr):
	rTirBlnd = cmds.createNode('transform', n='tertialMasterBlend_R0_drv', p='wing_R0_div6_loc', ss=True)
	cmds.parentConstraint('wing_R0_5_jnt', 'wing_R0_7_jnt', rTirBlnd, st=["x","y","z"])
	cmds.parentConstraint('wing_R0_6_jnt', rTirBlnd, sr=["x","y","z"])
	cmds.parentConstraint(rTirBlnd, rTirMstr, st=["x","z"], mo=True)

# Constrain mGear primaries
rigu.parentConstraint('wing_L0_div8_loc|wing_L0_wing_L0_div8_ctl', 'wing_L0_div0_loc|secondaryMaster_L0_root', mo=True)
rigu.parentConstraint('wing_L0_div9_loc|wing_L0_wing_L0_div9_ctl', 'wing_L0_div0_loc|primaryMid_L0_root', mo=True)
rigu.parentConstraint('wing_L0_div10_loc|wing_L0_wing_L0_div10_ctl', 'wing_L0_div0_loc|primaryMaster_L0_root', mo=True)

rigu.parentConstraint('wing_R0_div8_loc|wing_R0_wing_R0_div8_ctl', 'wing_R0_div0_loc|secondaryMaster_R0_root', mo=True)
rigu.parentConstraint('wing_R0_div9_loc|wing_R0_wing_R0_div9_ctl', 'wing_R0_div0_loc|primaryMid_R0_root', mo=True)
rigu.parentConstraint('wing_R0_div10_loc|wing_R0_wing_R0_div10_ctl', 'wing_R0_div0_loc|primaryMaster_R0_root', mo=True)

# Wing IK FK secondary ctls vis
if cmds.objExists('wingUI_L0_ctl'):
	# cmds.setAttr("wingUI_L0_ctl.chain_FK_vis", 0)
	cmds.setAttr("wingUI_L0_ctl.chain_IK_vis", 0)

if cmds.objExists('wingUI_R0_ctl'):
	# cmds.setAttr("wingUI_R0_ctl.chain_FK_vis", 0)
	cmds.setAttr("wingUI_R0_ctl.chain_IK_vis", 0)



'''

# Wing on Biped test.....
import wingFeathers as wft;reload(wft)

# Create all builder obj's
wft.buildBuilders()

# Layout Feathers (select crv)
wft.build(strapWidth = 0.015, endJntSize = 1.0)

# Manually place each feather root (select _grp)
[wft.removeConstraints(i) for i in cmds.ls(sl=1)]

# Mirror Feathers
# First mirror curves, and build feathers
# (select RIGHT side _bfr's)
wft.mirrorSelBfr(cmds.ls(sl=1))

# Rig Feathers (select _grp)
wft.rig(dorNum=9, ctlSize=0.05)


#Connect global scale attr to 'off' and 'ctlRef'
#ctlRef is under 'root' transforms. Select roots, then ctlRef. Then global scale
    
    
    
# To set biped guide to T-Pose
if cmds.ls(sl=1)==[]:
    raise IndexError('select guide root')

gdeRoot = cmds.ls(sl=1)[0]
rg = None
rg = mgear.shifter.Rig()
rg.guide.setFromSelection()

# Build rig
a = None
a = mgear.shifter.enc_catchBuild.PrePost(gdeRoot, rg.guide.components)

a.tPose()

a.bindPose(rg)

'''