"""Component Control 01 module"""

from mgear.shifter import component

from mgear.core import attribute, transform, primitive, constraints
from pymel.core import datatypes
import pymel.core as pm

import numpy as np
import uuid

import maya.cmds as cmds
import pprint
import maya.mel as mel
#############################################
# COMPONENT
#############################################
class Component(component.Main):
	def addObjects(self):
		"""Add all the objects needed to create the component."""
		self.comp_name  = self.guide.values['comp_name'] 
		self.comp_side  = self.guide.values['comp_side'] 
		self.comp_index = self.guide.values['comp_index']
		self.prefix = "{}_{}{}_".format(self.comp_name,self.comp_side,str(self.comp_index))
		
		root_matrix = transform.getTransform(self.root)
		sp_matrix   = root_matrix #steer point
		wcm_matrix  = self.guide.tra["center_loc"]
		sc_matrix   = self.guide.tra["circumference_loc"]
		wr_matrix   = self.guide.tra["radius_loc"]

		#Get the wheel radius
		pCenter = pm.PyNode(self.getName("center_loc"))
		pCircum = pm.PyNode(self.getName("circumference_loc"))
		pRadius = pm.PyNode(self.getName("radius_loc"))
		self.wheelRadius = abs(pRadius.translateY.get())#root_matrix[-1][1]
		self.steerRadius = abs(pCircum.translateX.get()) + abs(pCenter.translateX.get())

		guide_template_dict = self.guide.get_guide_template_dict()

		self.drive_ctl = self.addCtl(self.root,"drive_ctl",wr_matrix,self.color_ik,"arrow",w=self.size*2,h=self.size*2,d=self.size*2,tp=self.parentCtlTag)

		self.wheel_ctl        = primitive.addTransform(self.root, self.getName("ctl"), m=wcm_matrix)
		self.ball_jnt         = primitive.addTransform(self.root, self.getName("ball_place"), m = sp_matrix)
		self.wheel_jnt        = primitive.addTransform(self.ball_jnt, self.getName("wheel_place"), m = sc_matrix)
		self.wheelReset_cns   = primitive.addTransform(self.root, self.getName("wheelReset_cns"), wr_matrix)        
		self.steeringPt_loc   = primitive.addLocator(self.root, self.getName("steeringPt_loc"), m=sp_matrix, size=0.25)
		self.translateFollow_cns = primitive.addTransform(self.root, self.getName("translateFollow_cns"), m=wcm_matrix)
		self.rotateFollow_cns = primitive.addTransform(self.translateFollow_cns, self.getName("rotateFollow_cns"), m=wcm_matrix)
		self.parentFollowConstraint_loc = primitive.addLocator(self.root, self.getName("parentFollowConstraint_loc"), m=wcm_matrix, size=0.25)
		
		self.jnt_pos.append([self.ball_jnt, 0, None, False])
		self.jnt_pos.append([self.wheel_jnt, 1, None, False])

		pm.hide(self.parentFollowConstraint_loc)
		pm.hide(self.steeringPt_loc)

	def addAttributes(self):
		self.steering_att    = self.addAnimParam("steering", self.getName("steering"),"double",0)
		self.steerDrive_att  = self.addAnimParam("steerDrive","steerDrive","double",0,keyable=False)
		self.wheelSpin_att   = self.addAnimParam("wheelSpin","wheelSpin","double",0)
		self.wheelDrive_att  = self.addAnimParam("wheelDrive","wheelDrive","double",0,keyable=False)
		self.steerRadius_att = self.addAnimParam("steerRadius","steerRadius","double",self.steerRadius,keyable=False)
		self.wheelRadius_att = self.addAnimParam("wheelRadius","wheelRadius","double",self.wheelRadius,keyable=False)
		self.brake_att       = self.addAnimParam("brake","brake","bool",False)
		self.amountBraked_att = self.addAnimParam("amountBraked","amountBraked","double",0,keyable=False)
		self.amountNotBraked_att = self.addAnimParam("amountNotBraked","amountNotBraked","double",0,keyable=False)
		self.livePreviewOrBaked_att = self.addAnimEnumParam("previewOrBaked","previewOrBaked",0,enum=["livePreview","baked"],keyable=True)

		uiHost = pm.PyNode(self.wheelSpin_att.split(".")[0])
		attrs = pm.listAttr(uiHost, ud = True, keyable = False)
		
		mp_string_attr_exists = False
		for attr in attrs:
			if attr.find("_mpCurve") != -1:
				mp_string_attr_exists = True

		if not mp_string_attr_exists:
			self.mpCurve_att = self.addAnimParam("mpCurve","mpCurve","string","",keyable=False)
			self.mpLocator_att = self.addAnimParam("mpLocator","mpLocator","string","",keyable=False)
			self.motionPathName_att = self.addAnimParam("motionPathName","motionPathName","string","",keyable=False)

	# =====================================================
	# CONNECTOR
	# =====================================================
	def setRelation(self):
		"""Set the relation beetween object from guide to rig"""
		self.relatives["root"] = self.root
		self.relatives["center_loc"] = self.wheel_ctl
		self.relatives["radius_loc"] = self.wheelReset_cns

		self.controlRelatives["radius_loc"] = self.drive_ctl


	def addConnection(self):
		"""Add more connection definition to the set"""
		self.connections["standard"] = self.connect_no_steering

	def connect_no_steering(self):
		drive_ctrl = self.drive_ctl
		wheelReset_cns = self.wheelReset_cns
		steeringPt_loc = self.steeringPt_loc
		wheel_jnt = self.wheel_jnt
		ball_jnt = self.ball_jnt

		pm.makeIdentity(wheelReset_cns, apply=True, t=1, r=True, s=True)
		pm.makeIdentity(drive_ctrl, apply=True, t=1, r=True, s=True)

		wheel_ctl = self.wheel_ctl

		pm.makeIdentity(ball_jnt, apply=True, r=True, s=True)
		pm.makeIdentity(wheel_jnt, apply=True, r=True, s=True)

		pm.parent(wheelReset_cns, drive_ctrl)
		pm.parent(wheel_ctl, wheelReset_cns)

		pm.makeIdentity(wheel_ctl, apply=True, t=1)

		self.steering_att >> steeringPt_loc.rotateY
												 
		pm.parent(steeringPt_loc, wheelReset_cns)

		drive_PMA = pm.createNode("plusMinusAverage", n = self.getName("drive_PMA"))
		livePreviewOrBakedBrake_FC = pm.createNode("floatCondition", n = self.getName("livePreviewOrBakedBrake_FC"))
		wheelSpin_PMA = pm.createNode("plusMinusAverage", n = self.getName("wheelSpin_PMA"))
		reverseWheel_MDL = pm.createNode("multDoubleLinear", n = self.getName("reverseWheel_MDL"))
		
		drive_PMA.operation.set(2)
		self.steerDrive_att >> drive_PMA.input1D.input1D[1]
		self.wheelDrive_att >> drive_PMA.input1D.input1D[0]
		self.wheelSpin_att >> wheelSpin_PMA.input1D.input1D[0]
		self.livePreviewOrBaked_att >> livePreviewOrBakedBrake_FC.condition
		
		self.rotateFollow_cns.rotateX >> livePreviewOrBakedBrake_FC.floatA
		livePreviewOrBakedBrake_FC.outFloat >> wheelSpin_PMA.input1D.input1D[1]
		wheelSpin_PMA.output1D >> reverseWheel_MDL.input1

		reverseWheel_MDL.output >> wheel_jnt.rotateX

		# Condition for left vs right 
		if self.side == "R":
			pm.setAttr(reverseWheel_MDL + ".input2", 1 )
		
		if self.side == "L":
			pm.setAttr(reverseWheel_MDL + ".input2", 1 )

		#setup the live preview
		self.calculate_steer_drive()
		uiHost = pm.PyNode(self.wheelSpin_att.split(".")[0])

		uuid_id = str(uuid.uuid4())
		expression_node = pm.expression(n = self.getName("brakeExpression_{uuid_id}".format(uuid_id=uuid_id)))

		pm.addAttr(expression_node, ln="drivePmaString", dt="string")
		drive_PMA.message >> expression_node.drivePmaString
		pm.addAttr(expression_node, ln="uiHostString", dt="string") 

		pm.connectAttr(uiHost.message, expression_node.uiHostString)

		amountBraked_att_only =  self.amountBraked_att.split(".")[1]
		amountNotBraked_att_only =  self.amountNotBraked_att.split(".")[1]

		expression_node.expression.set('''string $basename = "{expression_node}" ;
														
		// Using the uuid number to generate the expressions name
		// Need to determine the expression name and whether were working on a reference 
		
		string $expressionArray [];
		string $expressionName; 
		
		// In the case were working in the anim scene  (with */ namespace)
		$expressionArray = `ls ("*:" + $basename )`;
		if ( size($expressionArray) != 0 ) 
				$expressionName = $expressionArray[0];
		// In the case were working in the rig setup scene  (without namespace)
		$expressionArray = `ls ($basename)`;
		if (  size($expressionArray) != 0) 
				$expressionName = $expressionArray[0];
		
		// Get the uihost from the attachted message node
		string $uiHost[] = `listConnections  ($expressionName + ".uiHostString")`;

		float $inRotation = {drive_PMA}.output1D;
		float $isBreaked = {brake_att};

		float $amountBraked = `getAttr ($uiHost[0] + ".{amountBraked_att_only}")`;
		float $amountNotBraked = `getAttr ($uiHost[0] + ".{amountNotBraked_att_only}")`;
		
		// Knowing how much the wheel has moved will allow us know where to keep the wheel
		if ( $isBreaked == 0 ) 
				// how much have we rolled while not braked
				setAttr ($uiHost[0] + ".{amountNotBraked_att_only}") ($inRotation - $amountBraked);
																																										

		if ( $isBreaked == 1 )
				// how much have we rolled while not braked
				setAttr ($uiHost[0] +".{amountBraked_att_only}") (($inRotation - $amountNotBraked));


		{livePreviewOrBakedBrake_FC}.floatB = $inRotation - {uiHost}.{amountBraked_att_only};'''.format(expression_node=str(expression_node),
																										drive_PMA=str(drive_PMA),
																										brake_att=str(self.brake_att),
																										amountBraked_att_only=str(amountBraked_att_only),
																										amountNotBraked_att_only=str(amountNotBraked_att_only),
																										livePreviewOrBakedBrake_FC=str(livePreviewOrBakedBrake_FC),
																										uiHost=str(uiHost)))

		attribute.setKeyableAttributes(self.wheel_ctl, self.t_params)

		self.parent.addChild(self.root)
		grandparent = pm.listRelatives(self.parent, p = True)

		pm.parent(self.parentFollowConstraint_loc, grandparent)
		pm.parent(self.translateFollow_cns, grandparent)

		pm.makeIdentity(self.parentFollowConstraint_loc, apply=True, t=1, r=True, s=True)
		pm.makeIdentity(self.translateFollow_cns, apply=True, t=1, r=True, s=True)

		pm.parentConstraint (self.parent, self.parentFollowConstraint_loc, mo = True)
		pm.parentConstraint (self.ball_jnt, self.translateFollow_cns, mo = True)

		constraints.matrixConstraint(parent=pm.PyNode(self.steeringPt_loc),child=pm.PyNode(self.ball_jnt),transform='srt',offset=True)
		constraints.matrixConstraint(parent=self.parent,child=self.parentFollowConstraint_loc,transform='srt',offset=True)

		return

	def calculate_steer_drive(self):
		# live preview calculate steer drive
		steerDriveCircumferenceFraction_MD = pm.createNode("multiplyDivide",n=self.getName("steerDriveCircumferenceFraction_MD"))
		steerCircumferenceFraction_MD = pm.createNode("multiplyDivide",n=self.getName("steerCircumferenceFraction_MD"))
		steerDistance_and_invert_MD = pm.createNode("multiplyDivide",n=self.getName("steerDistance_and_invert_MD"))
		wheelCircumferenceCalc_MD = pm.createNode("multiplyDivide",n=self.getName("wheelCircumferenceCalc_MD"))
		steerCircumferenceCalc_MD = pm.createNode("multiplyDivide",n=self.getName("steerCircumferenceCalc_MD"))                                                   
		steerDriveDistance_MD = pm.createNode("multiplyDivide",n=self.getName("steerDriveDistance_MD"))

		steerCircumferenceCalc_MD.input2X.set(6.283)  #PI * 2
		self.steerRadius_att >> steerCircumferenceCalc_MD.input1X
		steerCircumferenceFraction_MD.operation.set(2) #divide
		steerCircumferenceFraction_MD.input2X.set(360)
		self.steering_att >> steerCircumferenceFraction_MD.input1X
		steerCircumferenceFraction_MD.outputX >> steerDistance_and_invert_MD.input1X
		steerCircumferenceCalc_MD.outputX >> steerDistance_and_invert_MD.input2X
		wheelCircumferenceCalc_MD.input2X.set(6.283)
		self.wheelRadius_att >> wheelCircumferenceCalc_MD.input1X
		steerDriveCircumferenceFraction_MD.operation.set(2) #divide
		steerDistance_and_invert_MD.outputX >> steerDriveCircumferenceFraction_MD.input1X
		wheelCircumferenceCalc_MD.outputX >> steerDriveCircumferenceFraction_MD.input2X
		steerDriveDistance_MD.input2X.set(-360)
		steerDriveCircumferenceFraction_MD.outputX >> steerDriveDistance_MD.input1X
		self.steerRadius_att >> steerDistance_and_invert_MD.input1Y
		reverseSteer_MDL = pm.createNode("multDoubleLinear", n = self.getName("reverseSteer_MDL"))
		steerDriveDistance_MD.outputX >> reverseSteer_MDL.input1
		pm.setAttr(reverseSteer_MDL + ".input2", -1 )
		reverseSteer_MDL.output >> self.steerDrive_att
		steerDistance_and_invert_MD.input2Y.set(-1)
		# Condition for left vs right 
		if self.side == "R":
			pm.setAttr(reverseSteer_MDL + ".input2", 1 )

		if self.side == "L":
			pm.setAttr(reverseSteer_MDL + ".input2", -1 )

	def connect_steering(self):
		self.parent.addChild(self.root)
		#self.connect_standardWithSimpleIkRef()
		self.connectRef(self.settings["ikrefarray"], self.steering_loc)

		if pm.objExists(self.getName('jnt_org')):
			pm.parent(self.jnt, self.getName('jnt_org'))

		self.steering_att = self.addAnimParam("steering","steering","double",0)

	def postScript(self):
		#Expression converting to nodes
		#original expression
		#mel.eval('''expression -s "global vector $vPos = << 0, 0, 0 >>; float $distance = 0.0;int $direction = 1;vector $vPosChange = `getAttr wheel_R0_drive_ctl.translate`;float $cx = $vPosChange.x - $vPos.x;float $cy = $vPosChange.y - $vPos.y;float $cz = $vPosChange.z - $vPos.z;float $distance = sqrt( `pow $cx 2` + `pow $cy 2` + `pow $cz 2` );float $angle = wheel_R0_drive_ctl.rotateY%360;if ( ( $vPosChange.x == $vPos.x ) && ( $vPosChange.y != $vPos.y ) && ( $vPosChange.z == $vPos.z ) ){}else {\tif ( $angle == 0 ){ \t\tif ( $vPosChange.z > $vPos.z ) $direction = 1;\t\telse $direction=-1;}\tif ( ( $angle > 0 && $angle <= 90 ) || ( $angle <- 180 && $angle >= -270 ) ){ \t\tif ( $vPosChange.x > $vPos.x ) $direction = 1 * $direction;\t\telse $direction = -1 * $direction; }\tif ( ( $angle > 90 && $angle <= 180 ) || ( $angle < -90 && $angle >= -180 ) ){\t\tif ( $vPosChange.z > $vPos.z ) $direction = -1 * $direction;\t\telse $direction = 1 * $direction; }\tif ( ( $angle > 180 && $angle <= 270 ) || ( $angle < 0 && $angle >= -90 ) ){\t\tif ( $vPosChange.x > $vPos.x ) $direction = -1 * $direction;\t\telse $direction = 1 * $direction; }\tif ( ( $angle > 270 && $angle <= 360 ) || ( $angle < -270 && $angle >= -360 ) ) {\t\tif ( $vPosChange.z > $vPos.z ) $direction = 1 * $direction;\t\telse $direction = -1 * $direction; }\tworld_ctl.wheel_wheelDrive = world_ctl.wheel_wheelDrive + ( ( $direction * ( ( $distance / ( 6.283185 * world_ctl.wheel_wheelRadius ) ) * 360.0 ) ) ); }$vPos = << wheel_R0_drive_ctl.translateX, wheel_R0_drive_ctl.translateY, wheel_R0_drive_ctl.translateZ >>;"  -o wheel_R0_drive_ctl -n "car_expression" -ae 1 -uc all ;''')
		#pm.parent ("pCylinder2","wheel_R0_wheel_jnt")

		distance_PMA = pm.createNode('plusMinusAverage', n=self.getName("distance_PMA"), ss=True)

		pm.setAttr('%s.operation' % distance_PMA, 1)  #add
		pm.connectAttr('%s.t' % self.drive_ctl, '%s.input3D[0]' % distance_PMA)
		self.parentFollowConstraint_loc.translate >> distance_PMA.input3D[1]
		#pm.setAttr('%s.input3D[1]' % distance_PMA, 0,0,0)

		distance_MD = pm.createNode('multiplyDivide', n=self.getName("distance_MD"), ss=True)
		pm.setAttr('%s.operation' % distance_MD, 3) #power
		pm.connectAttr('%s.output3D' % distance_PMA, '%s.input1' % distance_MD)
		pm.setAttr('%s.input2' % distance_MD, 2,2,2)

		dist_PMA = pm.createNode('plusMinusAverage', n=self.getName("dist_PMA"), ss=True)
		pm.setAttr('%s.operation' % dist_PMA, 1) #sum
		pm.connectAttr('%s.outputX' % distance_MD, '%s.input1D[0]' % dist_PMA)
		pm.connectAttr('%s.outputY' % distance_MD, '%s.input1D[1]' % dist_PMA)
		pm.connectAttr('%s.outputZ' % distance_MD, '%s.input1D[2]' % dist_PMA)

		dist_FM = pm.createNode('floatMath', n=self.getName("dist_FM"), ss=True)
		pm.setAttr('%s.operation' % dist_FM, 6) #power
		pm.connectAttr('%s.output1D' % dist_PMA, '%s.floatA' % dist_FM)
		pm.setAttr('%s.floatB' % dist_FM, 0.5)
		
		addParentLocRotation_PMA = pm.createNode('plusMinusAverage', n=self.getName("addParentLocRotation_PMA"), ss=True)

		self.drive_ctl.rotateY >> addParentLocRotation_PMA.input1D[0]
		self.parentFollowConstraint_loc.rotateY >> addParentLocRotation_PMA.input1D[1]

		angle_MD = pm.createNode('math_ModulusInt', n=self.getName("angle_MD"), ss=True)
		addParentLocRotation_PMA.output1D >> '%s.input1' % angle_MD
		pm.setAttr('%s.input2' % angle_MD, 360)

		angle_CND = pm.createNode('condition', n=self.getName("angle_CND"), ss=True)
		pm.setAttr('%s.operation' % angle_CND, 0) #equal
		pm.connectAttr('%s.output' % angle_MD, '%s.firstTerm' % angle_CND)
		pm.setAttr('%s.secondTerm' % angle_CND, 0)
		pm.setAttr('%s.colorIfTrueR' % angle_CND, 1)
		pm.setAttr('%s.colorIfFalseR' % angle_CND, 0)
		#angle 0 condition

		distCom0_CND = pm.createNode('condition', n=self.getName("distCom0_CND"), ss=True)
		pm.setAttr('%s.operation' % distCom0_CND, 2)
		pm.connectAttr('%s.output3Dz' % distance_PMA, '%s.firstTerm' % distCom0_CND)
		pm.setAttr('%s.secondTerm' % distCom0_CND, 0)
		pm.connectAttr('%s.outColorR' % angle_CND, '%s.colorIfTrueR' % distCom0_CND)
		pm.setAttr('%s.colorIfFalseR' % distCom0_CND, 0)

		distComN0_CND = pm.createNode('condition', n=self.getName("distComN0_CND"), ss=True)
		pm.setAttr('%s.operation' % distComN0_CND, 4)
		pm.connectAttr('%s.output3Dz' % distance_PMA, '%s.firstTerm' % distComN0_CND)
		pm.setAttr('%s.secondTerm' % distComN0_CND, 0)
		pm.connectAttr('%s.outColorR' % angle_CND, '%s.colorIfTrueR' % distComN0_CND)
		pm.setAttr('%s.colorIfFalseR' % distComN0_CND, 0)

		distVal0_FM = pm.createNode('floatMath',n=self.getName("distVal0_FM"), ss=True)
		pm.setAttr('%s.operation' % distVal0_FM, 2) #multiply
		pm.setAttr('%s.floatB' % distVal0_FM, -1)
		pm.connectAttr('%s.outColorR' % distComN0_CND, '%s.floatA' % distVal0_FM)

		carDirect_FM = pm.createNode('floatMath',n=self.getName("carDirect_FM"), ss=True)
		pm.setAttr('%s.operation' % carDirect_FM, 2) #multiply
		pm.connectAttr('%s.outColorR' % distCom0_CND, '%s.floatA' % carDirect_FM)

		carDirectN_FM = pm.createNode('floatMath',n=self.getName("carDirectN_FM"), ss=True)
		pm.setAttr('%s.operation' % carDirectN_FM, 2) #multiply
		pm.connectAttr('%s.outFloat' % distVal0_FM, '%s.floatA' % carDirectN_FM)

		#first if condition
		angle0_CND = pm.createNode('condition', n=self.getName("angle0_CND"), ss=True)
		pm.setAttr('%s.secondTerm' % angle0_CND, 0)
		pm.setAttr('%s.operation' % angle0_CND, 2)
		pm.connectAttr('%s.output' % angle_MD, '%s.firstTerm' % angle0_CND)

		angle1_CND = pm.createNode('condition', n=self.getName("angle1_CND"), ss=True)
		pm.setAttr('%s.secondTerm' % angle1_CND, 90)
		pm.setAttr('%s.operation' % angle1_CND, 5)
		pm.connectAttr('%s.output' % angle_MD, '%s.firstTerm' % angle1_CND)

		angle2_CND = pm.createNode('condition', n=self.getName("angle2_CND"), ss=True)
		pm.setAttr('%s.secondTerm' % angle2_CND, -180)
		pm.setAttr('%s.operation' % angle2_CND, 4)
		pm.connectAttr('%s.output' % angle_MD, '%s.firstTerm' % angle2_CND)

		angle3_CND = pm.createNode('condition', n=self.getName("angle3_CND"), ss=True)
		pm.setAttr('%s.secondTerm' % angle3_CND, -270)
		pm.setAttr('%s.operation' % angle3_CND, 3)
		pm.connectAttr('%s.output' % angle_MD, '%s.firstTerm' % angle3_CND)

		angleCom1_FM = pm.createNode('floatMath',n=self.getName("angleCom1_FM"), ss=True)
		pm.setAttr('%s.operation' % angleCom1_FM, 0)
		pm.connectAttr('%s.outColorR' % angle0_CND, '%s.floatA' % angleCom1_FM)
		pm.connectAttr('%s.outColorR' % angle1_CND, '%s.floatB' % angleCom1_FM)

		angleCom2_FM = pm.createNode('floatMath',n=self.getName("angleCom2_FM"), ss=True)
		pm.setAttr('%s.operation' % angleCom2_FM, 0)
		pm.connectAttr('%s.outColorR' % angle2_CND, '%s.floatA' % angleCom2_FM)
		pm.connectAttr('%s.outColorR' % angle3_CND, '%s.floatB' % angleCom2_FM)

		angleCom_CND = pm.createNode('condition', n=self.getName("angleCom_CND"), ss=True)
		pm.setAttr('%s.operation' % angleCom_CND, 1)
		pm.connectAttr('%s.outFloat' % angleCom1_FM, '%s.firstTerm' % angleCom_CND)
		pm.connectAttr('%s.outFloat' % angleCom2_FM, '%s.secondTerm' % angleCom_CND)
		pm.setAttr('%s.colorIfTrueR' % angleCom_CND, 1)
		pm.setAttr('%s.colorIfFalseR' % angleCom_CND, 0)

		distCom_CND = pm.createNode('condition', n=self.getName("distCom_CND"), ss=True)
		pm.setAttr('%s.operation' % distCom_CND, 2)
		pm.connectAttr('%s.output3Dx' % distance_PMA, '%s.firstTerm' % distCom_CND)
		pm.setAttr('%s.secondTerm' % distCom_CND, 0)
		pm.connectAttr('%s.outColorR' % angleCom_CND, '%s.colorIfTrueR' % distCom_CND)
		pm.setAttr('%s.colorIfFalseR' % distCom_CND, 0)

		distNCom_CND = pm.createNode('condition', n=self.getName("distNCom_CND"), ss=True)
		pm.setAttr('%s.operation' % distNCom_CND, 4)
		pm.connectAttr('%s.output3Dx' % distance_PMA, '%s.firstTerm' % distNCom_CND)
		pm.setAttr('%s.secondTerm' % distNCom_CND, 0)
		pm.connectAttr('%s.outColorR' % angleCom_CND, '%s.colorIfTrueR' % distNCom_CND)
		pm.setAttr('%s.colorIfFalseR' % distNCom_CND, 0)

		carDirect1_FM = pm.createNode('floatMath',n=self.getName("carDirect1_FM"), ss=True)
		pm.setAttr('%s.operation' % carDirect1_FM, 2) #multiply
		pm.setAttr('%s.floatB' % carDirect1_FM, 1)
		pm.connectAttr('%s.outColorR' % distCom_CND, '%s.floatA' % carDirect1_FM)

		distVal_FM = pm.createNode('floatMath',n=self.getName("distVal_FM"), ss=True)
		pm.setAttr('%s.operation' % distVal_FM, 2) #multiply
		pm.setAttr('%s.floatB' % distVal_FM, -1)
		pm.connectAttr('%s.outColorR' % distNCom_CND, '%s.floatA' % distVal_FM)

		carDirectN1_FM = pm.createNode('floatMath',n=self.getName("carDirectN1_FM"), ss=True)
		pm.setAttr('%s.operation' % carDirectN1_FM, 2) #multiply
		pm.setAttr('%s.floatB' % carDirectN1_FM, 1)
		pm.connectAttr('%s.outFloat' % distVal_FM, '%s.floatA' % carDirectN1_FM)

		#second if condition
		angle4_CND = pm.createNode('condition', n=self.getName("angle4_CND"), ss=True)
		pm.setAttr('%s.secondTerm' % angle4_CND, 90)
		pm.setAttr('%s.operation' % angle4_CND, 2)
		pm.connectAttr('%s.output' % angle_MD, '%s.firstTerm' % angle4_CND)

		angle5_CND = pm.createNode('condition', n=self.getName("angle5_CND"), ss=True)
		pm.setAttr('%s.secondTerm' % angle5_CND, 180)
		pm.setAttr('%s.operation' % angle5_CND, 5)
		pm.connectAttr('%s.output' % angle_MD, '%s.firstTerm' % angle5_CND)

		angle6_CND = pm.createNode('condition', n=self.getName("angle6_CND"), ss=True)
		pm.setAttr('%s.secondTerm' % angle6_CND, -90)
		pm.setAttr('%s.operation' % angle6_CND, 4)
		pm.connectAttr('%s.output' % angle_MD, '%s.firstTerm' % angle6_CND)

		angle7_CND = pm.createNode('condition', n=self.getName("angle7_CND"), ss=True)
		pm.setAttr('%s.secondTerm' % angle7_CND, -180)
		pm.setAttr('%s.operation' % angle7_CND, 3)
		pm.connectAttr('%s.output' % angle_MD, '%s.firstTerm' % angle7_CND)

		angleCom3_FM = pm.createNode('floatMath',n=self.getName("angleCom3_FM"), ss=True)
		pm.setAttr('%s.operation' % angleCom3_FM, 0)
		pm.connectAttr('%s.outColorR' % angle4_CND, '%s.floatA' % angleCom3_FM)
		pm.connectAttr('%s.outColorR' % angle5_CND, '%s.floatB' % angleCom3_FM)

		angleCom4_FM = pm.createNode('floatMath',n=self.getName("angleCom4_FM"), ss=True)
		pm.setAttr('%s.operation' % angleCom4_FM, 0)
		pm.connectAttr('%s.outColorR' % angle6_CND, '%s.floatA' % angleCom4_FM)
		pm.connectAttr('%s.outColorR' % angle7_CND, '%s.floatB' % angleCom4_FM)

		angleCom1_CND = pm.createNode('condition', n=self.getName("angleCom1_CND"), ss=True)
		pm.setAttr('%s.operation' % angleCom1_CND, 1)
		pm.connectAttr('%s.outFloat' % angleCom3_FM, '%s.firstTerm' % angleCom1_CND)
		pm.connectAttr('%s.outFloat' % angleCom4_FM, '%s.secondTerm' % angleCom1_CND)
		pm.setAttr('%s.colorIfTrueR' % angleCom1_CND, 1)
		pm.setAttr('%s.colorIfFalseR' % angleCom1_CND, 0)

		distCom1_CND = pm.createNode('condition', n=self.getName("distCom1_CND"), ss=True)
		pm.setAttr('%s.operation' % distCom1_CND, 2)
		pm.connectAttr('%s.output3Dz' % distance_PMA, '%s.firstTerm' % distCom1_CND)
		pm.setAttr('%s.secondTerm' % distCom1_CND, 0)
		pm.connectAttr('%s.outColorR' % angleCom1_CND, '%s.colorIfTrueR' % distCom1_CND)
		pm.setAttr('%s.colorIfFalseR' % distCom1_CND, 0)

		distComN1_CND = pm.createNode('condition', n=self.getName("distComN1_CND"), ss=True)
		pm.setAttr('%s.operation' % distComN1_CND, 4)
		pm.connectAttr('%s.output3Dz' % distance_PMA, '%s.firstTerm' % distComN1_CND)
		pm.setAttr('%s.secondTerm' % distComN1_CND, 0)
		pm.connectAttr('%s.outColorR' % angleCom1_CND, '%s.colorIfTrueR' % distComN1_CND)
		pm.setAttr('%s.colorIfFalseR' % distComN1_CND, 0)

		distVal1_FM = pm.createNode('floatMath',n=self.getName("distVal1_FM"), ss=True)
		pm.setAttr('%s.operation' % distVal1_FM, 2) #multiply
		pm.setAttr('%s.floatB' % distVal1_FM, -1)
		pm.connectAttr('%s.outColorR' % distCom1_CND, '%s.floatA' % distVal1_FM)


		carDirect2_FM = pm.createNode('floatMath',n=self.getName("carDirect2_FM"), ss=True)
		pm.setAttr('%s.operation' % carDirect2_FM, 2) #multiply
		pm.setAttr('%s.floatB' % carDirect2_FM, 1)
		pm.connectAttr('%s.outFloat' % distVal1_FM, '%s.floatA' % carDirect2_FM)

		carDirectN2_FM = pm.createNode('floatMath',n=self.getName("carDirectN2_FM"), ss=True)
		pm.setAttr('%s.operation' % carDirectN2_FM, 2) #multiply
		pm.setAttr('%s.floatB' % carDirectN2_FM, 1)
		pm.connectAttr('%s.outColorR' % distComN1_CND, '%s.floatA' % carDirectN2_FM)

		#third if condition
		angle8_CND = pm.createNode('condition', n=self.getName("angle8_CND"), ss=True)
		pm.setAttr('%s.secondTerm' % angle8_CND, 180)
		pm.setAttr('%s.operation' % angle8_CND, 2)
		pm.connectAttr('%s.output' % angle_MD, '%s.firstTerm' % angle8_CND)

		angle9_CND = pm.createNode('condition', n=self.getName("angle9_CND"), ss=True)
		pm.setAttr('%s.secondTerm' % angle9_CND, 270)
		pm.setAttr('%s.operation' % angle9_CND, 5)
		pm.connectAttr('%s.output' % angle_MD, '%s.firstTerm' % angle9_CND)

		angle10_CND = pm.createNode('condition', n=self.getName("angle10_CND"), ss=True)
		pm.setAttr('%s.secondTerm' % angle10_CND, 0)
		pm.setAttr('%s.operation' % angle10_CND, 4)
		pm.connectAttr('%s.output' % angle_MD, '%s.firstTerm' % angle10_CND)

		angle11_CND = pm.createNode('condition', n=self.getName("angle11_CND"), ss=True)
		pm.setAttr('%s.secondTerm' % angle11_CND, -90)
		pm.setAttr('%s.operation' % angle11_CND, 3)
		pm.connectAttr('%s.output' % angle_MD, '%s.firstTerm' % angle11_CND)

		angleCom5_FM = pm.createNode('floatMath',n=self.getName("angleCom5_FM"), ss=True)
		pm.setAttr('%s.operation' % angleCom5_FM, 0)
		pm.connectAttr('%s.outColorR' % angle8_CND, '%s.floatA' % angleCom5_FM)
		pm.connectAttr('%s.outColorR' % angle9_CND, '%s.floatB' % angleCom5_FM)

		angleCom6_FM = pm.createNode('floatMath',n=self.getName("angleCom6_FM"), ss=True)
		pm.setAttr('%s.operation' % angleCom6_FM, 0)
		pm.connectAttr('%s.outColorR' % angle10_CND, '%s.floatA' % angleCom6_FM)
		pm.connectAttr('%s.outColorR' % angle11_CND, '%s.floatB' % angleCom6_FM)

		angleCom2_CND = pm.createNode('condition', n=self.getName("angleCom2_CND"), ss=True)
		pm.setAttr('%s.operation' % angleCom2_CND, 1)
		pm.connectAttr('%s.outFloat' % angleCom5_FM, '%s.firstTerm' % angleCom2_CND)
		pm.connectAttr('%s.outFloat' % angleCom6_FM, '%s.secondTerm' % angleCom2_CND)
		pm.setAttr('%s.colorIfTrueR' % angleCom2_CND, 1)
		pm.setAttr('%s.colorIfFalseR' % angleCom2_CND, 0)

		distCom2_CND = pm.createNode('condition', n=self.getName("distCom2_CND"), ss=True)
		pm.setAttr('%s.operation' % distCom2_CND, 2)
		pm.connectAttr('%s.output3Dx' % distance_PMA, '%s.firstTerm' % distCom2_CND)
		pm.setAttr('%s.secondTerm' % distCom2_CND, 0)
		pm.connectAttr('%s.outColorR' % angleCom2_CND, '%s.colorIfTrueR' % distCom2_CND)
		pm.setAttr('%s.colorIfFalseR' % distCom2_CND, 0)

		distComN2_CND = pm.createNode('condition', n=self.getName("distComN2_CND"), ss=True)
		pm.setAttr('%s.operation' % distComN2_CND, 4)
		pm.connectAttr('%s.output3Dx' % distance_PMA, '%s.firstTerm' % distComN2_CND)
		pm.setAttr('%s.secondTerm' % distComN2_CND, 0)
		pm.connectAttr('%s.outColorR' % angleCom2_CND, '%s.colorIfTrueR' % distComN2_CND)
		pm.setAttr('%s.colorIfFalseR' % distComN2_CND, 0)

		distVal2_FM = pm.createNode('floatMath',n=self.getName("distVal2_FM"), ss=True)
		pm.setAttr('%s.operation' % distVal2_FM, 2) #multiply
		pm.setAttr('%s.floatB' % distVal2_FM, -1)
		pm.connectAttr('%s.outColorR' % distCom2_CND, '%s.floatA' % distVal2_FM)

		carDirect3_FM = pm.createNode('floatMath',n=self.getName("carDirect3_FM"), ss=True)
		pm.setAttr('%s.operation' % carDirect3_FM, 2) #multiply
		pm.setAttr('%s.floatB' % carDirect3_FM, 1)
		pm.connectAttr('%s.outFloat' % distVal2_FM, '%s.floatA' % carDirect3_FM)

		carDirectN3_FM = pm.createNode('floatMath',n=self.getName("carDirectN3_FM"), ss=True)
		pm.setAttr('%s.operation' % carDirectN3_FM, 2) #multiply
		pm.setAttr('%s.floatB' % carDirectN3_FM, 1)
		pm.connectAttr('%s.outColorR' % distComN2_CND, '%s.floatA' % carDirectN3_FM)

		#forth if condition
		angle12_CND = pm.createNode('condition', n=self.getName("angle12_CND"), ss=True)
		pm.setAttr('%s.secondTerm' % angle12_CND, 270)
		pm.setAttr('%s.operation' % angle12_CND, 2)
		pm.connectAttr('%s.output' % angle_MD, '%s.firstTerm' % angle12_CND)

		angle13_CND  = pm.createNode('condition', n=self.getName("angle13_CND "), ss=True)
		pm.setAttr('%s.secondTerm' % angle13_CND , 360)
		pm.setAttr('%s.operation' % angle13_CND , 5)
		pm.connectAttr('%s.output' % angle_MD, '%s.firstTerm' % angle13_CND )

		angle14_CND  = pm.createNode('condition', n=self.getName("angle14_CND "), ss=True)
		pm.setAttr('%s.secondTerm' % angle14_CND , -270)
		pm.setAttr('%s.operation' % angle14_CND , 4)
		pm.connectAttr('%s.output' % angle_MD, '%s.firstTerm' % angle14_CND )

		angle15_CND  = pm.createNode('condition', n=self.getName("angle15_CND "), ss=True)
		pm.setAttr('%s.secondTerm' % angle15_CND , -360)
		pm.setAttr('%s.operation' % angle15_CND , 3)
		pm.connectAttr('%s.output' % angle_MD, '%s.firstTerm' % angle15_CND )

		angleCom7_FM = pm.createNode('floatMath',n=self.getName("angleCom7_FM"), ss=True)
		pm.setAttr('%s.operation' % angleCom7_FM, 0)
		pm.connectAttr('%s.outColorR' % angle12_CND, '%s.floatA' % angleCom7_FM)
		pm.connectAttr('%s.outColorR' % angle13_CND , '%s.floatB' % angleCom7_FM)

		angleCom8_FM = pm.createNode('floatMath',n=self.getName("angleCom8_FM"), ss=True)
		pm.setAttr('%s.operation' % angleCom8_FM, 0)
		pm.connectAttr('%s.outColorR' % angle14_CND , '%s.floatA' % angleCom8_FM)
		pm.connectAttr('%s.outColorR' % angle15_CND , '%s.floatB' % angleCom8_FM)

		angleCom3_CND = pm.createNode('condition', n=self.getName("angleCom3_CND"), ss=True)
		pm.setAttr('%s.operation' % angleCom3_CND, 1)
		pm.connectAttr('%s.outFloat' % angleCom7_FM, '%s.firstTerm' % angleCom3_CND)
		pm.connectAttr('%s.outFloat' % angleCom8_FM, '%s.secondTerm' % angleCom3_CND)
		pm.setAttr('%s.colorIfTrueR' % angleCom3_CND, 1)
		pm.setAttr('%s.colorIfFalseR' % angleCom3_CND, 0)

		distCom3_CND = pm.createNode('condition', n=self.getName("distCom3_CND"), ss=True)
		pm.setAttr('%s.operation' % distCom3_CND, 2)
		pm.connectAttr('%s.output3Dz' % distance_PMA, '%s.firstTerm' % distCom3_CND)
		pm.setAttr('%s.secondTerm' % distCom3_CND, 0)
		pm.connectAttr('%s.outColorR' % angleCom3_CND, '%s.colorIfTrueR' % distCom3_CND)
		pm.setAttr('%s.colorIfFalseR' % distCom3_CND, 0)

		distComN3_CND = pm.createNode('condition', n=self.getName("distComN3_CND"), ss=True)
		pm.setAttr('%s.operation' % distComN3_CND, 4)
		pm.connectAttr('%s.output3Dz' % distance_PMA, '%s.firstTerm' % distComN3_CND)
		pm.setAttr('%s.secondTerm' % distComN3_CND, 0)
		pm.connectAttr('%s.outColorR' % angleCom3_CND, '%s.colorIfTrueR' % distComN3_CND)
		pm.setAttr('%s.colorIfFalseR' % distComN3_CND, 0)

		distVal3_FM = pm.createNode('floatMath',n=self.getName("distVal3_FM"), ss=True)
		pm.setAttr('%s.operation' % distVal3_FM, 2) #multiply
		pm.setAttr('%s.floatB' % distVal3_FM, -1)
		pm.connectAttr('%s.outColorR' % distComN3_CND, '%s.floatA' % distVal3_FM)

		carDirect4_FM = pm.createNode('floatMath',n=self.getName("carDirect4_FM"), ss=True)
		pm.setAttr('%s.operation' % carDirect4_FM, 2) #multiply
		pm.setAttr('%s.floatB' % carDirect4_FM, 1)
		pm.connectAttr('%s.outColorR' % distCom3_CND, '%s.floatA' % carDirect4_FM)

		carDirectN4_FM = pm.createNode('floatMath',n=self.getName("carDirectN4_FM"), ss=True)
		pm.setAttr('%s.operation' % carDirectN4_FM, 2) #multiply
		pm.setAttr('%s.floatB' % carDirectN4_FM, 1)
		pm.connectAttr('%s.outFloat' % distVal3_FM, '%s.floatA' % carDirectN4_FM)

		carDirect_PMA = pm.createNode('plusMinusAverage',n=self.getName("carDirect_PMA"), ss=True)
		pm.connectAttr('%s.outFloat' % carDirect_FM, '%s.input1D[0]' % carDirect_PMA)
		pm.connectAttr('%s.outFloat' % carDirectN_FM, '%s.input1D[1]' % carDirect_PMA)
		pm.connectAttr('%s.outFloat' % carDirect1_FM, '%s.input1D[2]' % carDirect_PMA)
		pm.connectAttr('%s.outFloat' % carDirectN1_FM, '%s.input1D[3]' % carDirect_PMA)
		pm.connectAttr('%s.outFloat' % carDirect2_FM, '%s.input1D[4]' % carDirect_PMA)
		pm.connectAttr('%s.outFloat' % carDirectN2_FM, '%s.input1D[5]' % carDirect_PMA)
		pm.connectAttr('%s.outFloat' % carDirect3_FM, '%s.input1D[6]' % carDirect_PMA)
		pm.connectAttr('%s.outFloat' % carDirectN3_FM, '%s.input1D[7]' % carDirect_PMA)
		pm.connectAttr('%s.outFloat' % carDirect4_FM, '%s.input1D[8]' % carDirect_PMA)
		pm.connectAttr('%s.outFloat' % carDirectN4_FM, '%s.input1D[9]' % carDirect_PMA)

		carDiamter_FM = pm.createNode('floatMath',n=self.getName("carDiamter_FM"), ss=True)       
		pm.setAttr('%s.operation' % carDiamter_FM, 2) #multiply
		pm.setAttr('%s.floatB' % carDiamter_FM, 6.283185)

		pm.setAttr('%s.floatA' % carDiamter_FM, self.wheelRadius)

		carCircum_FM = pm.createNode('floatMath',n=self.getName("carCircum_FM"), ss=True)       
		pm.setAttr('%s.operation' % carCircum_FM, 3) #Divide
		pm.connectAttr('%s.outFloat' % dist_FM, '%s.floatA' % carCircum_FM)
		pm.connectAttr('%s.outFloat' % carDiamter_FM, '%s.floatB' % carCircum_FM)

		carMath_FM = pm.createNode('floatMath',n=self.getName("carMath_FM"), ss=True)       
		pm.setAttr('%s.operation' % carMath_FM, 2) #multiply
		pm.connectAttr('%s.output1D' % carDirect_PMA, '%s.floatA' % carMath_FM) 
		pm.connectAttr('%s.outFloat' % carCircum_FM, '%s.floatB' % carMath_FM)

		carR_FM = pm.createNode('floatMath',n=self.getName("carR_FM"), ss=True)       
		pm.setAttr('%s.operation' % carR_FM, 2) #multiply
		pm.connectAttr('%s.outFloat' % carMath_FM, '%s.floatA' % carR_FM)
		pm.setAttr('%s.floatB' % carR_FM, 360)

		wheelDrive_FM = pm.createNode('floatMath',n=self.getName("wheelDrive_FM"), ss=True)
		pm.setAttr('%s.operation' % wheelDrive_FM, 0) #add

		pm.connectAttr('%s.outFloat' % carR_FM, '%s.floatB' % wheelDrive_FM)
		pm.setAttr('%s.floatA' % wheelDrive_FM, 0)

		wheelDriveOut_FM = pm.createNode('floatMath',n=self.getName("wheelDriveOut_FM"), ss=True)
		pm.setAttr('%s.operation' % wheelDriveOut_FM, 0) #add
		pm.setAttr('%s.floatA' % wheelDriveOut_FM, 0)
		pm.connectAttr('%s.outFloat' % wheelDrive_FM, '%s.floatB' % wheelDriveOut_FM)
		pm.connectAttr('%s.outFloat' % wheelDriveOut_FM, self.wheelDrive_att)
