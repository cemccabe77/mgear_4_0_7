import maya.cmds as cmds

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

# Foot roll
if cmds.objExists('legUI_L0_ctl'):
	cmds.setAttr('legUI_L0_ctl.foot_L0_angle_1', 0)

if cmds.objExists('legUI_R0_ctl'):
	cmds.setAttr('legUI_R0_ctl.foot_L0_angle_1', 0)

# Wing IK FK secondary ctls
if cmds.objExists('wingUI_L0_ctl'):
	cmds.setAttr("wingUI_L0_ctl.chain_IK_vis", 0)
	cmds.setAttr("wingUI_L0_ctl.chain_FK_vis", 0)

if cmds.objExists('wingUI_R0_ctl'):
	cmds.setAttr("wingUI_R0_ctl.chain_FK_vis", 0)
	cmds.setAttr("wingUI_R0_ctl.chain_IK_vis", 0)


# Fold Attr L
if cmds.objExists('wingUI_L0_ctl'):
	if not cmds.attributeQuery('wing_fold', node='wingUI_L0_ctl', ex=True):
		cmds.addAttr('wingUI_L0_ctl', k=True, ci=True, at='enum', sn='__________________', enumName='wing_fold')
		cmds.addAttr('wingUI_L0_ctl', k=True, ci=True, at='float', sn='wing_fold', min=0, max=1)
# Fold Attr R
if cmds.objExists('wingUI_R0_ctl'):
	if not cmds.attributeQuery('wing_fold', node='wingUI_R0_ctl', ex=True):
		cmds.addAttr('wingUI_R0_ctl', k=True, ci=True, at='enum', sn='__________________', enumName='wing_fold')
		cmds.addAttr('wingUI_R0_ctl', k=True, ci=True, at='float', sn='wing_fold', min=0, max=1)
