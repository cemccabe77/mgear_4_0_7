import maya.cmds as cmds

# Foot roll
for ui in ['backLegUI_L0_ctl', 'backLegUI_R0_ctl', 
		   'frontLegUI_L0_ctl', 'frontLegUI_R0_ctl']:
	if cmds.objExists(ui):
		cmds.setAttr(ui+'.foot_angle_0', 0)
