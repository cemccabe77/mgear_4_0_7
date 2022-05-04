"""Nvigate the DAG hierarchy"""


import maya.cmds as cmds
import pymel.core as pm

#############################################
# DAG
#############################################


def getTopParent(node):
    """Returns the first parent of the hierarchy.

    usually the 'Model' in Softimage terminology

    Arguments:
        node (dagNode): The input node to search.

    Returns:
        dagNode: The top parent of the input node

    """
    return node.getParent(generations=-1)


def getShapes(node):
    """Returns the shape of the dagNode

    Arguments:
        node (dagNode): The input node to search the shape

    Returns:
        list: The shapes of the node

    """
    return node.listRelatives(shapes=True)


def findChild(node, name):
    """Returns the first child of input node, with a matching name.

    Arguments:
        node (dagNode): The input node to search
        name (str): The name to search

    Returns:
        dagNode: The first child

    >>>  parent = dag.findChild(self.model,
                                mgear.string.convertRLName(
                                    comp_guide.root.name()))

    """
    # return __findChildren(node, name, True)
    return __findChild(node, name)


def findChildren(node, name):
    """Returns all the children  of input node, with a matching name.

    Arguments:
        node (dagNode): The input node to search
        name (str): The name to search

    Returns:
        dagNode list: The children dagNodes

    """
    return __findChildren(node, name, False)


def findChildrenPartial(node, name):
    """
    Returns the children of input node, with a partial matching name.

    Arguments:
        node (dagNode): The input node to search
        name (str): The name to search

    Returns:
        dagNode list: The children dagNodes

    """
    return __findChildren(node, name, False, True)


def __findChildren(node, name, firstOnly=False, partialName=False):

    if partialName:
        children = [item for item
                    in node.listRelatives(allDescendents=True,
                                          type="transform")
                    if item.name().split("|")[-1].split("_")[-1] == name]
    else:
        children = [item for item
                    in node.listRelatives(allDescendents=True,
                                          type="transform")
                    if item.name().split("|")[-1] == name]
    if not children:
        return False
    if firstOnly:
        return children[0]

    return children


def __findChild(node, name):
    """This find children function will stop search after first
     child found.child

    This is a faster version of __findchildren

    Arguments:
        node (dagNode): The input node to search
        name (str): The name to search

    Returns:
        dagNode: Children node
    """
    try:
        for item in cmds.listRelatives(node.name(),
                                       allDescendents=True,
                                       type="transform"):
            if item.split("|")[-1] == name:
                return pm.PyNode(item)
    except pm.MayaNodeError:
        for item in node.listRelatives(allDescendents=True,
                                       type="transform"):
            if item.split("|")[-1] == name:
                return item

    return False


def __findChildren2(node, name, firstOnly=False, partialName=False):
    """This function is using Maya cmds instead of PyMel

    Arguments:
        node (TYPE): Description
        name (TYPE): Description
        firstOnly (bool, optional): Description
        partialName (bool, optional): Description

    Returns:
        TYPE: Description
    """
    oName = node.name()
    if partialName:
        children = [item for item
                    in cmds.listRelatives(oName, allDescendents=True,
                                          type="transform")
                    if item.split("|")[-1].split("_")[-1] == name]
    else:
        children = [item for item
                    in cmds.listRelatives(oName, allDescendents=True,
                                          type="transform")
                    if item.split("|")[-1] == name]
    if not children:
        return False
    if firstOnly:
        return pm.PyNode(children[0])

    return [pm.PyNode(x) for x in children]


def findComponentChildren(node, name, sideIndex):
    """Returns the component children of input component root.

    Note:
        This method is specific to work with shifter guides naming conventions

    Arguments:
        node (dagNode): The input node to search
        name (str): The name to search
        sideIndex (str): the side

    Returns:
        dagNode list: The children dagNodes

    >>> objList =  dag.findComponentChildren(self.parent,
                                             oldName,
                                             oldSideIndex)

    """
    children = []
    for item in node.listRelatives(allDescendents=True,
                                   type="transform"):
        checkName = item.name().split("|")[-1].split("_")
        if checkName[0] == name and checkName[1] == sideIndex:
            children.append(item)

    return children


def findComponentChildren2(node, name, sideIndex):
    """Returns the component children of input component root.

    This function is using Maya cmds instead of PyMel

    Note:
        This method is specific to work with shifter guides naming conventions

    Arguments:
        node (dagNode): The input node to search
        name (str): The name to search
        sideIndex (str): the side

    Returns:
        dagNode list: The children dagNodes

    >>> objList =  dag.findComponentChildren(self.parent,
                                             oldName,
                                             oldSideIndex)

    """
    children = []
    for item in cmds.listRelatives(node.name(), allDescendents=True,
                                   fullPath=True, type="transform"):
        checkName = item.split("|")[-1].split("_")
        if checkName[0] == name and checkName[1] == sideIndex:
            children.append(item)

    return [pm.PyNode(x) for x in children]


def findComponentChildren3(node, name, sideIndex):
    """Returns the component children of input component root.

    This function is using Maya cmds instead of PyMel

    Note:
        This method is specific to work with shifter guides naming conventions

    Arguments:
        node (dagNode): The input node to search
        name (str): The name to search
        sideIndex (str): the side

    Returns:
        dagNode list: The children dagNodes

    >>> objList =  dag.findComponentChildren(self.parent,
                                             oldName,
                                             oldSideIndex)

    """
    children = []
    for item in cmds.listRelatives(node.name(), allDescendents=True,
                                   fullPath=True, type="transform"):
        checkName = item.split("|")[-1]
        in_name = "_".join([name, sideIndex])

        if in_name in checkName:
            children.append(item)

    return [pm.PyNode(x) for x in children]
