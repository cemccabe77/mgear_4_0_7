"""Functions to create primitives (Non geometry)"""

import pymel.core as pm
import pymel.core.datatypes as datatypes

from mgear.core import transform

# encore
from mgear.core import curve, constraints, dag

#############################################
# PRIMITIVE
#############################################


def addTransform(parent, name, m=datatypes.Matrix()):
    """Create a transform dagNode.

    Arguments:
        parent (dagNode): The parent for the node.
        name (str): The Node name.
        m (matrix): The matrix for the node transformation (optional).

    Returns:
        dagNode: The newly created node.

    """
    node = pm.PyNode(pm.createNode("transform", n=name))
    node.setTransformation(m)

    if parent is not None:
        parent.addChild(node)

    return node


def addTransformFromPos(parent, name, pos=datatypes.Vector(0, 0, 0)):
    """Create a transform dagNode.

    Arguments:
        parent (dagNode): The parent for the node.
        name (str): The Node name.
        pos (vector): The vector for the node position (optional).

    Returns:
        dagNode: The newly created node.

    """
    node = pm.PyNode(pm.createNode("transform", n=name))
    node.setTranslation(pos, space="world")

    if parent is not None:
        parent.addChild(node)

    return node

# ===========================================
# LOCATOR


def addLocator(parent, name, m=datatypes.Matrix(), size=1):
    """Create a space locator dagNode.

    Arguments:
        parent (dagNode): The parent for the node.
        name (str): The Node name.
        m (matrix): The matrix for the node transformation (optional).
        size (float): The space locator shape size (optional).

    Returns:
        dagNode: The newly created node.

    """
    node = pm.PyNode(pm.createNode("locator")).getParent()
    node.rename(name)
    node.setTransformation(m)
    node.setAttr("localScale", size, size, size)

    if parent is not None:
        parent.addChild(node)

    return node


def addLocatorFromPos(parent, name, pos=datatypes.Vector(0, 0, 0), size=1):
    """Create a space locator dagNode.

    Arguments:
        parent (dagNode): The parent for the node.
        name (str): The Node name.
        pos (vector): The vector for the node position (optional).
        size (float): The space locator shape size (optional).

    Returns:
        dagNode: The newly created node.

    """
    node = pm.PyNode(pm.createNode("locator")).getParent()
    node.rename(name)
    node.setTranslation(pos, space="world")
    node.setAttr("localScale", size, size, size)

    if parent is not None:
        parent.addChild(node)

    return node

# ===========================================
# JOINT


def addJoint(parent, name, m=datatypes.Matrix(), vis=True):
    """Create a joint dagNode.

    Note:
        I'm not using the joint() comand because this is parenting
        the newly created joint to current selection which might not be desired

    Arguments:
        parent (dagNode): The parent for the node.
        name (str): The node name.
        m (matrix): The matrix for the node transformation (optional).
        vis (bool): Set the visibility of the new joint.

    Returns:
        dagNode: The newly created node.

    """
    node = pm.PyNode(pm.createNode("joint", n=name))
    node.setTransformation(m)
    node.setAttr("visibility", vis)

    if parent is not None:
        parent.addChild(node)

    return node


def addJointFromPos(parent, name, pos=datatypes.Vector(0, 0, 0)):
    """Create a joint dagNode.

    Note:
        I'm not using the joint() comand because this is parenting
        the newly created joint to current selection which might not be desired

    Arguments:
        parent (dagNode): The parent for the node.
        name (str): The node name.
        pos (vector): The vector for the node position (optional).
        vis (bool): Set the visibility of the new joint.

    Returns:
        dagNode: The newly created node.

    """
    node = pm.PyNode(pm.createNode("joint", n=name))
    node.setTranslation(pos, space="world")

    if parent is not None:
        parent.addChild(node)

    return node


def add2DChain2(parent, name, positions, normal, negate=False, vis=True):
    """Experimental 2D Chain creation function.

    Create a 2D joint chain. Like Softimage 2D chain.

    Warning:
        This function is WIP and not ready for production.

    Warning:
        This function will create un expected results if all the
        positions are not in the same 2D plane.

    Arguments:
        parent (dagNode): The parent for the chain.
        name (str): The node name.
        positions(list of vectors): the positons to define the chain.
        normal (vector): The normal vector to define the direction of
            the chain.
        negate (bool): If True will negate the direction of the chain

    Returns;
        list of dagNodes: The list containg all the joints of the chain



    >>> self.chain3bones = pri.add2DChain2(
        self.setup,
        self.getName("chain3bones%s_jnt"),
        self.guide.apos[0:4],
        self.normal,
        False)

    """
    if "%s" not in name:
        name += "%s"

    transforms = transform.getChainTransform(positions, normal, negate)
    t = transform.setMatrixPosition(transforms[-1], positions[-1])
    transforms.append(t)

    chain = []
    for i, t in enumerate(transforms):
        node = addJoint(parent, name % i, t, vis)
        chain.append(node)
        parent = node

    # moving rotation value to joint orient
    for i, jnt in enumerate(chain):

        if i == 0:
            jnt.setAttr("jointOrient", jnt.getAttr("rotate"))
        elif i == len(chain) - 1:
            jnt.setAttr("jointOrient", 0, 0, 0)
        else:
            # This will fail if chain is not always oriented the same
            # way (like Z chain)
            v0 = positions[i] - positions[i - 1]
            v1 = positions[i + 1] - positions[i]
            angle = datatypes.degrees(v0.angle(v1))

            jnt.setAttr("jointOrient", 0, 0, angle)

        jnt.setAttr("rotate", 0, 0, 0)
        jnt.setAttr("radius", 1.5)

    return chain


def add2DChain(parent, name, positions, normal, negate=False, vis=True):
    """Create a 2D joint chain. Like Softimage 2D chain.

    Warning:
        This function will create un expected results if all the
        positions are not in the same 2D plane.

    Arguments:
        parent (dagNode): The parent for the chain.
        name (str): The node name.
        positions(list of vectors): the positons to define the chain.
        normal (vector): The normal vector to define the direction of
            the chain.
        negate (bool): If True will negate the direction of the chain

    Returns;
        list of dagNodes: The list containg all the joints of the chain

    >>> self.rollRef = pri.add2DChain(
        self.root,
        self.getName("rollChain"),
        self.guide.apos[:2],
        self.normal,
        self.negate)

    """
    if "%s" not in name:
        name += "%s"

    transforms = transform.getChainTransform(positions, normal, negate)
    t = transform.setMatrixPosition(transforms[-1], positions[-1])
    transforms.append(t)

    chain = []
    for i, t in enumerate(transforms):
        node = addJoint(parent, name % i, t, vis)
        chain.append(node)
        parent = node

    # moving rotation value to joint orient
    for i, jnt in enumerate(chain):
        if i == 0:
            jnt.setAttr("jointOrient", jnt.getAttr("rotate"))
            jnt.setAttr("rotate", 0, 0, 0)
        elif i == len(chain) - 1:
            jnt.setAttr("jointOrient", 0, 0, 0)
            jnt.setAttr("rotate", 0, 0, 0)
        else:
            # This will fail if chain is not always oriented the same
            # way (like X chain)
            v0 = positions[i] - positions[i - 1]
            v1 = positions[i + 1] - positions[i]
            angle = datatypes.degrees(v0.angle(v1))
            jnt.setAttr("rotate", 0, 0, 0)
            jnt.setAttr("jointOrient", 0, 0, angle)

        # check if we have to negate Z angle by comparing the guide
        # position and the resulting position.
        if i >= 1:
            # round the position values to 6 decimals precission
            # TODO: test with less precision and new check after apply
            # Ik solver
            if ([round(elem, 4) for elem in transform.getTranslation(jnt)]
                    != [round(elem, 4) for elem in positions[i]]):

                jp = jnt.getParent()

                # Aviod intermediate e.g. `transform3` groups that can appear
                # between joints due to basic moving around.
                while jp.type() == "transform":
                    jp = jp.getParent()

                jp.setAttr(
                    "jointOrient", 0, 0, jp.attr("jointOrient").get()[2] * -1)

        jnt.setAttr("radius", 1.5)

    return chain


def addIkHandle(parent, name, chn, solver="ikRPsolver", poleV=None):
    """Creates and connect an IKhandle to a joints chain.

    Arguments:
        parent (dagNode): The parent for the IKhandle.
        name (str): The node name.
        chn (list): List of joints.
        solver (str): the solver to be use for the ikHandel. Default
            value is "ikRPsolver"
        poleV (dagNode): Pole vector for the IKHandle

    Returns:
        dagNode: The IKHandle

    >>> self.ikHandleUpvRef = pri.addIkHandle(
        self.root,
        self.getName("ikHandleLegChainUpvRef"),
        self.legChainUpvRef,
        "ikSCsolver")

    """
    # creating a crazy name to avoid name clashing before convert to pyNode.
    node = pm.ikHandle(n=name + "kjfjfklsdf049r58420582y829h3jnf",
                       sj=chn[0],
                       ee=chn[-1],
                       solver=solver)[0]
    node = pm.PyNode(node)
    pm.rename(node, name)
    node.attr("visibility").set(False)

    if parent:
        parent.addChild(node)

    if poleV:
        pm.poleVectorConstraint(poleV, node)

    return node


# ========================================
# Encore =================================
# ========================================

def IkSplineOnCurve(crvNode, count, attr=None, startCtl=None, endCtl=None, mpthNd=[]):
    '''
    Creates ikSpline that is constrained to a curve.
    Optional spline twist driven by two transforms. (Twist will introduce 180 flip)
    Spline will follow spcJts. spcJts can exist, or be created herein.
    
    crvNode  = (dag) Node of crv to create ikSpline onto
    count    = (int) Number of joints to create in ikSpline
    attr     = Existing attr to connect 'MaintainLength'
    startCtl = (dag) Node of start ctl
    endCtl   = (dag) Node of end ctl
    '''

    ikSpln = curve.ikSplineOnCrv(crvNode, count=count)

    # If no existing joints constrained to curve, by motionPath nodes
    if mpthNd == []:
        spcJts = curve.createEvenAlongCrv(crvNode=crvNode, objType='joint', 
                                          objName='spacer', count=count,
                                          suffix='spc', lra=False)
        pm.parent(spcJts, crvNode)
        mpthNd = constraints.consToCrvParametric(crvNode, spcJts, upType=4)
        [pm.setAttr(jnt+'.drawStyle', 2) for jnt in spcJts]

    lengthAttr = ikSplineCrvStretch(mpthNd, ikSpln[0])

    ikHdl = ikSpln[1][0]
    # pm.setAttr(ikHdl+'.v', 0)

    if attr != None and lengthAttr != None:
        pm.connectAttr(attr, lengthAttr)
    
    # Advanced twist controls
    if startCtl != None and endCtl != None:
        ikHdl = ikSpln[1][0]
        pm.setAttr(ikHdl+'.dTwistControlEnable', 1)
        pm.setAttr(ikHdl+'.dWorldUpType', 4)
        pm.connectAttr(endCtl+'.wm', ikHdl+'.dWorldUpMatrixEnd')
        pm.connectAttr(startCtl+'.wm', ikHdl+'.dWorldUpMatrix')

    return ikSpln # joints, ikHandle

def ikSplineCrvStretch(motPthNdes, jts):
    '''
    Uses joints, that are constrained to a curve by motionPath nodes,
    to drive position along curve for spline joints. Giving anim the option
    to turn off Maintain Length for the ik spline.
    Currently used in IkSplineOnCurve()

    motPthNdes = ([])  List of param joint mp nodes from createEvenAlongCrv()
    jts        = ([])  List of spline joints from ikSplineOnCrv()
    '''
    pm.addAttr(motPthNdes[0], at='bool', k=True, ci=True, sn='MaintainLength', dv=1)

    for i, nde in enumerate(motPthNdes[:-1]):
        distBet = pm.createNode('distanceBetween', n='mtnPthStr_ikDistBet_'+str(i), ss=True)
        distZero = pm.createNode('floatMath', n='mtnPthStr_ikDistZero_'+str(i), ss=True)
        distDiff = pm.createNode('floatMath', n='mtnPthStr_ikDistDiff_'+str(i), ss=True)
        rigScale = pm.createNode('floatMath', n='mtnPthStr_rigScale'+str(i), ss=True)
        pm.connectAttr(motPthNdes[i]+'.allCoordinates', distBet+'.point1')
        pm.connectAttr(motPthNdes[i+1]+'.allCoordinates', distBet+'.point2')
        pm.setAttr(rigScale+'.operation', 3) # Divide
        pm.setAttr(distZero+'.operation', 1) # Subtract
        pm.setAttr(distDiff+'.operation', 1) # Subtract
        pm.setAttr(distZero+'.floatA', pm.getAttr(distBet+'.distance'))
        pm.connectAttr(distBet+'.distance', rigScale+'.floatA')
        pm.connectAttr(rigScale+'.outFloat', distZero+'.floatB')
        pm.setAttr(distDiff+'.floatA', pm.getAttr(distBet+'.distance'))
        pm.connectAttr(distZero+'.outFloat', distDiff+'.floatB')
        # Maintain length tx
        lengthCond = pm.createNode('condition', n='mtnPthStr_lengthCond_'+str(i), ss=True)
        pm.connectAttr(motPthNdes[0]+'.MaintainLength', lengthCond+'.firstTerm')
        pm.setAttr(lengthCond+'.secondTerm', 1)
        pm.connectAttr(distDiff+'.outFloat', lengthCond+'.colorIfFalseR')
        pm.setAttr(lengthCond+'.colorIfTrueR', pm.getAttr(distBet+'.distance'))
        pm.connectAttr(lengthCond+'.outColorR', jts[i+1]+'.translateX')

    return motPthNdes[0]+'.MaintainLength'