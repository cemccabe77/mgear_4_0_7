import pymel.core as pm
import maya.OpenMaya as om
import pymel.core.datatypes as datatypes
from . import transform as tra

##################
# Helper functions
##################

def setName(name, namePrefix="pCns", side="C", idx=None):
    namesList = [namePrefix, side, name]
    if idx is not None:
        namesList[1] = side + str(idx)
    name = "_".join(namesList)
    return name

def getDagPath(node=None):
    sel = om.MSelectionList()
    sel.add(node)
    d = om.MDagPath()
    sel.getDagPath(0, d)
    return d

def getLocalOffset(parent, child):
    parentWorldMatrix = getDagPath(parent).inclusiveMatrix()
    childWorldMatrix = getDagPath(child).inclusiveMatrix()
    return childWorldMatrix * parentWorldMatrix.inverse()

def decomposeMatrixConnect(node=None,
                           child=None,
                           transform='srt'):

    if node and child:
        dm_node = pm.createNode('decomposeMatrix',
                                name=setName(child + "_decompMatrix"))
        pm.connectAttr(node + ".matrixSum",
                       dm_node + ".inputMatrix")
        if 't' in transform:
            pm.connectAttr(dm_node + ".outputTranslate",
                           child.attr("translate"), f=True)
        if 'r' in transform:
            pm.connectAttr(dm_node + ".outputRotate",
                           child.attr("rotate"), f=True)
        if 's' in transform:
            pm.connectAttr(dm_node + ".outputScale",
                           child.attr("scale"), f=True)

def matrixConstraint(parent=None,
                     child=None,
                     transform='srt',
                     offset=False):
    """Create constraint based on Maya Matrix node.

    """

    if parent and child:
        node = pm.createNode('multMatrix',
                             name=setName(parent + "_multMatrix"))
        if offset:
            localOffset = getLocalOffset(parent.name(), child.name())
            pm.setAttr(node + ".matrixIn[0]",
                       [localOffset(i, j) for i in range(4) for j in range(4)],
                       type="matrix")
            mId = ["[1]", "[2]"]
        else:
            mId = ["[0]", "[1]"]

        for m, mi, mx in zip([parent, child],
                             ['matrixIn' + mId[0], 'matrixIn' + mId[1]],
                             [".worldMatrix", ".parentInverseMatrix"]):
            m = m + mx
            if isinstance(m, datatypes.Matrix):
                pm.setAttr(node.attr(mi), m)
            else:
                pm.connectAttr(m, node.attr(mi))

        decomposeMatrixConnect(node, child, transform)

        return node

def matrixBlendConstraint(parent=None,  # should be a list
                          child=None,
                          weights=None,  # should be a list
                          transform='rt',
                          offset=False,
                          host=None):

    if parent and child:
        if not isinstance(parent, (list,)):
            pm.displayWarning(
                "matrixBlendConstraint [parent] variable should be a list.")
            return

        if weights:
            if isinstance(parent, (list,)):
                if len(weights) != len(parent):
                    pm.displayWarning(
                        "weights list should be equal to parents list.")
                    return
            else:
                pm.displayWarning(
                    "matrixBlendConstraint [weights] "
                    "variable should be a list.")
                return
        else:
            weights = []
            weight = 1.0 / len(parent)
            for p in parent:
                weights.append(weight)

        wtMat_node = pm.createNode('wtAddMatrix',
                                   name=setName(child + "_wtAddMatrix"))

        x = 0
        for p in parent:
            if offset:
                localOffset = getLocalOffset(p.name(), child.name())
                offset_node = pm.createNode(
                    'multMatrix',
                    name=setName(p + "_offsetMultMatrix"))
                pm.setAttr(
                    offset_node + ".matrixIn[0]",
                    [localOffset(i, j) for i in range(4) for j in range(4)],
                    type="matrix")
                pm.connectAttr(p + ".worldMatrix[0]",
                               offset_node + ".matrixIn[1]")
                pm.connectAttr(offset_node + ".matrixSum",
                               wtMat_node + ".wtMatrix[{}].matrixIn".format(x))
            else:
                pm.connectAttr(p + ".worldMatrix[0]",
                               wtMat_node + ".wtMatrix[{}].matrixIn".format(x))

            # set weights
            if host:
                name = setName(p + "_wtWeight")
                host.addAttr(name,
                             keyable=True,
                             attributeType='float',
                             min=0.0,
                             max=1.0)
                pm.connectAttr(host + "." + name,
                               wtMat_node + ".wtMatrix[{}].weightIn".format(x))
                pm.setAttr(host + "." + name, weights[x])
            else:
                wtMat_node.attr(
                    'wtMatrix[{}]'.format(x)).weightIn.set(weights[x])

            x += 1

        decomposeMatrixConnect(wtMat_node, child, transform)

        return wtMat_node

def oriCns(driver, driven, maintainOffset=False):
    """Apply orientation constraint

    Apply orientation constraint changing XYZ  default connexions by
    rotate compound connexions

    Note:
        We have found an evaluation difference in the values if the connexion
        is compound or by axis

    Arguments:
        driver (dagNode or dagNode list): Driver object.
        driven (dagNode): Driven object.
        maintainOffset (bool): Keep the offset.

    Returns:
        pyNode: Orientation constraintn node.

    Example:
        .. code-block:: python

            import mgear.core.applyop as aop
            import pymel.core as pm
            sphere = pm.polySphere(n='sphereDriver')
            cube = pm.polyCube(n='cubeDriven')
            ori_cns = aop.oriCns(sphere[0], cube[0], True)

    """
    oriCns = pm.orientConstraint(driver, driven, maintainOffset=maintainOffset)
    for axis in "XYZ":
        pm.disconnectAttr(oriCns + ".constraintRotate" + axis,
                          driven + ".rotate" + axis)
    pm.connectAttr(oriCns + ".constraintRotate", driven + ".rotate", f=True)

    return oriCns

def pointCns(driver, driven, maintainOffset=False):
    """Apply point constraint

    Apply point constraint changing XYZ  default connexions by
    rotate compound connexions

    Note:
        We have found an evaluation difference in the values if the connexion
        is compound or by axis

    Arguments:
        driver (dagNode or dagNode list): Driver object.
        driven (dagNode): Driven object.
        maintainOffset (bool): Keep the offset.

    Returns:
        pyNode: Orientation constraintn node.

    Example:
        .. code-block:: python

            import mgear.core.constraints as constraints
            import pymel.core as pm
            sphere = pm.polySphere(n='sphereDriver')
            cube = pm.polyCube(n='cubeDriven')
            point_cns = constraints.pointCns(sphere[0], cube[0], True)

    """
    pointCns = pm.pointConstraint(driver, driven, maintainOffset=maintainOffset)
    for axis in "XYZ":
        pm.disconnectAttr(pointCns + ".constraintTranslate" + axis,
                          driven + ".translate" + axis)
    pm.connectAttr(pointCns + ".constraintTranslate", driven + ".translate", f=True)

    return pointCns

def pathCns(obj, curve, cnsType=False, u=0, tangent=False):
    """
    Apply a path constraint or curve constraint.

    Arguments:
        obj (dagNode): Constrained object.
        curve (Nurbscurve): Constraining Curve.
        cnsType (int): 0 for Path Constraint, 1 for Curve
            Constraint (Parametric).
        u (float): Position of the object on the curve (from 0 to 100 for path
            constraint, from 0 to 1 for Curve cns).
        tangent (bool): Keep tangent orientation option.

    Returns:
        pyNode: The newly created constraint.
    """
    node = pm.PyNode(pm.createNode("motionPath"))
    node.setAttr("uValue", u)
    node.setAttr("fractionMode", not cnsType)
    node.setAttr("follow", tangent)

    pm.connectAttr(curve.attr("worldSpace"), node.attr("geometryPath"))
    pm.connectAttr(node.attr("allCoordinates"), obj.attr("translate"))
    pm.connectAttr(node.attr("rotate"), obj.attr("rotate"))
    pm.connectAttr(node.attr("rotateOrder"), obj.attr("rotateOrder"))
    pm.connectAttr(node.attr("message"), obj.attr("specifiedManipLocation"))

    return node

def aimCns(obj,
           master,
           axis="xy",
           wupType="objectrotation",
           wupVector=[0, 1, 0],
           wupObject=None,
           maintainOffset=False):
    """Apply a direction constraint
    TODO: review function to make wupObject optional

    Arguments:
        obj (dagNode): Constrained object.
        master (dagNode): Constraining Object.
        axis (str): Define pointing axis and upvector
            axis (combination of xyz and -x-y-z).
        wupType (str): scene, object, objectrotation, vector, or none.
        wupVector (list of 3 float): world up vector. Exp: [0.0,1.0,0.0].
        wupObject (pyNode): world up object.
        maintainOffset (bool): Maintain offset.

    Returns:
        pyNode: Newly created constraint.

    """
    node = pm.aimConstraint(master,
                            obj,
                            worldUpType=wupType,
                            worldUpVector=wupVector,
                            worldUpObject=wupObject,
                            maintainOffset=maintainOffset)

    if axis == "xy":
        a = [1, 0, 0, 0, 1, 0]
    elif axis == "xz":
        a = [1, 0, 0, 0, 0, 1]
    elif axis == "yx":
        a = [0, 1, 0, 1, 0, 0]
    elif axis == "yz":
        a = [0, 1, 0, 0, 0, 1]
    elif axis == "zx":
        a = [0, 0, 1, 1, 0, 0]
    elif axis == "zy":
        a = [0, 0, 1, 0, 1, 0]

    elif axis == "-xy":
        a = [-1, 0, 0, 0, 1, 0]
    elif axis == "-xz":
        a = [-1, 0, 0, 0, 0, 1]
    elif axis == "-yx":
        a = [0, -1, 0, 1, 0, 0]
    elif axis == "-yz":
        a = [0, -1, 0, 0, 0, 1]
    elif axis == "-zx":
        a = [0, 0, -1, 1, 0, 0]
    elif axis == "-zy":
        a = [0, 0, -1, 0, 1, 0]

    elif axis == "x-y":
        a = [1, 0, 0, 0, -1, 0]
    elif axis == "x-z":
        a = [1, 0, 0, 0, 0, -1]
    elif axis == "y-x":
        a = [0, 1, 0, -1, 0, 0]
    elif axis == "y-z":
        a = [0, 1, 0, 0, 0, -1]
    elif axis == "z-x":
        a = [0, 0, 1, -1, 0, 0]
    elif axis == "z-y":
        a = [0, 0, 1, 0, -1, 0]

    elif axis == "-x-y":
        a = [-1, 0, 0, 0, -1, 0]
    elif axis == "-x-z":
        a = [-1, 0, 0, 0, 0, -1]
    elif axis == "-y-x":
        a = [0, -1, 0, -1, 0, 0]
    elif axis == "-y-z":
        a = [0, -1, 0, 0, 0, -1]
    elif axis == "-z-x":
        a = [0, 0, -1, -1, 0, 0]
    elif axis == "-z-y":
        a = [0, 0, -1, 0, -1, 0]

    for i, name in enumerate(["aimVectorX",
                              "aimVectorY",
                              "aimVectorZ",
                              "upVectorX",
                              "upVectorY",
                              "upVectorZ"]):

        pm.setAttr(node + "." + name, a[i])

    return node

def constToSrfFol(obj, srf, name, mo=False):
    '''
    Constrains dag object to closest point on nurbs surface via follicle.
    Follicle follows point positions, not transform.
   
    obj = (node) Item to be constrained
    srf = (node) Surface that item will be constrained to
    name = (str) Name of follicle
    '''
    pntOnSrf = pm.createNode('closestPointOnSurface', ss=True)
    pm.connectAttr(srf+'.worldSpace[0]', pntOnSrf+'.inputSurface') # Connect nurbs surface to pntOnSrfPointOnSurface node
    pm.connectAttr(obj+'.translate', pntOnSrf+'.inPosition') # get world translate
    pm.disconnectAttr(obj+'.translate', pntOnSrf+'.inPosition')

    follicle  = pm.createNode("follicle", n=name+'Shape', ss=True)
    follicleT = pm.listRelatives(follicle, type='transform', p=True) # get follicle transform
    pm.rename(follicleT, name)
    pm.connectAttr(follicle+ ".outRotate", follicleT[0] + ".rotate") # follicle shape rot drives follicle transform rot
    pm.connectAttr(follicle+ ".outTranslate", follicleT[0] + ".translate") # follicle shape translate drives follicle transform translate
    pm.connectAttr(srf+'.worldInverseMatrix', follicle+'.inputWorldMatrix') # This will negate transforms and allow the follicle to be parented under the surface

    pm.connectAttr(srf+'.worldSpace[0]', follicle+'.inputSurface')
    pm.setAttr(follicle+ ".simulationMethod", 0)
    pm.setAttr(follicle+'.visibility', 0)

    pm.connectAttr(pntOnSrf+'.result.parameterU', follicle+'.parameterU')# connecting U,V param to follicle U,V param
    pm.connectAttr(pntOnSrf+'.result.parameterV', follicle+'.parameterV')

    pm.parent(obj, follicleT[0])
    pm.delete(pntOnSrf) # pntOnSrf needs to be deleted

    if mo == False:
        tra.resetTransform(obj, s=False)

    return follicleT

def constToSrfMatrix(obj, srf, translate=True, rotate=True, xAxis='v'):
    '''
    Constrains objects to closest point on nurbs surface with matrix

    obj       = (str) Item to be constrained
    srf       = (str) Surface that item will be constrained to
    translate = (bol) Constrain translation
    rotate    = (bol) Constrain rotation
    xAxis     = (str) 'u' or 'v' direction of srf to use for obj X vector
    '''

    pntOnSrf       = pm.createNode('closestPointOnSurface', n=obj+'pntOnSrf', ss=True)
    posInf         = pm.createNode('pointOnSurfaceInfo', n=obj+'posInf', ss=True)
    posMatrix      = pm.createNode('fourByFourMatrix', n=obj+'posMat', ss=True)
    posLocalDecomp = pm.createNode('decomposeMatrix', n=obj+'posLocDecomp', ss=True)

    pm.connectAttr(srf+'.worldSpace[0]', pntOnSrf+'.inputSurface')
    pm.connectAttr(srf+'.worldSpace[0]', posInf+'.inputSurface')
    pm.connectAttr(obj+'.translate', pntOnSrf+'.inPosition')
    pm.connectAttr(pntOnSrf+'.parameterU', posInf+'.parameterU')
    pm.connectAttr(pntOnSrf+'.parameterV', posInf+'.parameterV')
    pm.disconnectAttr(pntOnSrf+'.parameterU', posInf+'.parameterU')
    pm.disconnectAttr(pntOnSrf+'.parameterV', posInf+'.parameterV')
    
    # Pull away from the edge of the nurbs surface
    # Cannot limit this attr minValue, maxValue
    if pm.getAttr(posInf+'.parameterV') == 0:
        pm.setAttr(posInf+'.parameterV', 0.001)
    if pm.getAttr(posInf+'.parameterV') == 1.0999999999999999:
        pm.setAttr(posInf+'.parameterV', 1.098)
    if pm.getAttr(posInf+'.parameterU') == 0:
        pm.setAttr(posInf+'.parameterU', 0.001)
    if pm.getAttr(posInf+'.parameterU') == 1:
        pm.setAttr(posInf+'.parameterU', 0.999)

    if xAxis=='u':
        # X vector
        pm.connectAttr(posInf+'.normalizedTangentUX', posMatrix+'.in00')
        pm.connectAttr(posInf+'.normalizedTangentUY', posMatrix+'.in01')
        pm.connectAttr(posInf+'.normalizedTangentUZ', posMatrix+'.in02')
        # Y vector
        pm.connectAttr(posInf+'.normalizedNormalX', posMatrix+'.in10')
        pm.connectAttr(posInf+'.normalizedNormalY', posMatrix+'.in11')
        pm.connectAttr(posInf+'.normalizedNormalZ', posMatrix+'.in12')
        # Z vector
        pm.connectAttr(posInf+'.normalizedTangentVX', posMatrix+'.in20')
        pm.connectAttr(posInf+'.normalizedTangentVY', posMatrix+'.in21')
        pm.connectAttr(posInf+'.normalizedTangentVZ', posMatrix+'.in22')

    if xAxis=='v':
        # X vector
        pm.connectAttr(posInf+'.normalizedTangentVX', posMatrix+'.in00')
        pm.connectAttr(posInf+'.normalizedTangentVY', posMatrix+'.in01')
        pm.connectAttr(posInf+'.normalizedTangentVZ', posMatrix+'.in02')
        # Y vector
        pm.connectAttr(posInf+'.normalizedNormalX', posMatrix+'.in10')
        pm.connectAttr(posInf+'.normalizedNormalY', posMatrix+'.in11')
        pm.connectAttr(posInf+'.normalizedNormalZ', posMatrix+'.in12')
        # Z vector
        pm.connectAttr(posInf+'.normalizedTangentUX', posMatrix+'.in20')
        pm.connectAttr(posInf+'.normalizedTangentUY', posMatrix+'.in21')
        pm.connectAttr(posInf+'.normalizedTangentUZ', posMatrix+'.in22')

    pm.connectAttr(posInf+'.positionX', posMatrix+'.in30')
    pm.connectAttr(posInf+'.positionY', posMatrix+'.in31')
    pm.connectAttr(posInf+'.positionZ', posMatrix+'.in32')

    # Trying to skip the posMultMat node in above comment out block
    pm.connectAttr(posMatrix+'.output', posLocalDecomp+'.inputMatrix')
    if translate == True:
        pm.connectAttr(posLocalDecomp+'.outputTranslate', obj+'.translate')
    if rotate == True:
        pm.connectAttr(posLocalDecomp+'.outputRotate', obj+'.rotate')

    # Connect U, V if they exist
    if 'U' in pm.listAttr(obj):
        if pm.getAttr(posInf+'.parameterU') > 1.0: # I think I'm getting rounding errors creating values above 1.0
            pm.setAttr(obj+'.U', 1.0)
        else:
            if pm.getAttr(posInf+'.parameterU') < 0:
                pos = 0
            else:
                pos = pm.getAttr(posInf+'.parameterU')
            pm.setAttr(obj+'.U', pos)
        pm.connectAttr(obj+'.U', posInf+'.parameterU')

    if 'V' in pm.listAttr(obj):
        if pm.getAttr(posInf+'.parameterV') > 1.0: # I think I'm getting rounding errors creating values above 1.0
            pm.setAttr(obj+'.V', 1.0)
        else:
            if pm.getAttr(posInf+'.parameterV') < 0:
                pos = 0
            else:
                pos = pm.getAttr(posInf+'.parameterV')
            pm.setAttr(obj+'.V', pos)
        pm.connectAttr(obj+'.V', posInf+'.parameterV')

    pm.delete(pntOnSrf)

    return posInf


def consToCrvParametric(crvNode, consTo, translate=True, rotate=True, upType=4, inverseUp=0, 
                        inverseFront=0, frontAxis=0, upAxis=2, upObj=None):
    '''
    Constrain items to curve by motionPath nodes.
    Objects do not need to be placed on top of curve.
    This function gets closest point on curve to make constraint.

    crvNode    = (str) Curve to constrain items to
    consTo     = ([]) Items that will be constrained to curve
    upType     = (Int) 1=Object, 2=Object Rototation, 3=Vector, 4=Normal
    '''

    # # If passing a single obj for constraint
    if type(consTo) != list:
        consTo = [consTo]

    pthNodes = []
    for obj in consTo:
        pos=pm.xform(obj, q=True, ws=True, t=True)
        uParam = curve.getUParam(pos, crvNode)
        motPth = pm.createNode('motionPath', n=obj+'_motPath', ss=True)
        pm.connectAttr(crvNode+'.worldSpace[0]', motPth+'.geometryPath')
        if translate == True:
            pm.connectAttr(motPth+'.allCoordinates', obj+'.translate')
        if rotate == True:
            pm.connectAttr(motPth+'.rotate', obj+'.rotate')
        pm.setAttr(motPth+'.uValue', uParam)

        if upType in [1, 2]:
            pm.setAttr(motPth+'.worldUpType', upType)
            if pm.objExists(upObj):
                pm.connectAttr(upObj+'.worldMatrix[0]', motPth+'.worldUpMatrix')
            else:
                raise ValueError('Object {} does not exist'.format(upObj))
        else:
            pm.setAttr(motPth+'.worldUpType', upType)

        pm.setAttr(motPth+'.inverseUp', inverseUp)
        pm.setAttr(motPth+'.inverseFront', inverseFront)
        pm.setAttr(motPth+'.frontAxis', frontAxis)
        pm.setAttr(motPth+'.upAxis', upAxis)

        pthNodes.append(motPth)

    return pthNodes