import sys
from mgear.core import pyqt
import pymel.core as pm
import maya.cmds as cmds
import mgear
from mgear import shifter

#cm
import sys
if sys.version_info.major == 2:
    from . import enc_catchBuild as enc
    reload(enc)
else:
    import importlib
    from . import enc_catchBuild as enc
    importlib.reload(enc)


##############################
# Helper Functions
##############################


def draw_comp(comp_type, parent=None, showUI=True):
    """Draw a new component of a given name

    Args:
        comp_type (str): Name of the component to draw
        *args: Description
    """
    guide = shifter.guide.Rig()
    if not parent and pm.selected():
        parent = pm.selected()[0]

    if parent:
        if not parent.hasAttr("isGearGuide") and not parent.hasAttr("ismodel"):
            pm.displayWarning(
                "{}: is not valid Shifter guide elemenet".format(parent))
            return

    guide.drawNewComponent(parent, comp_type, showUI)


def duplicate(sym, *args):
    """Duplicate a component by drawing a new one and setting the same
    properties values

    Args:
        sym (bool): If True, will create a symmetrical component
        *args: None

    """
    oSel = pm.selected()
    if oSel:
        root = oSel[0]
        guide = shifter.guide.Rig()
        guide.duplicate(root, sym)
    else:
        mgear.log("Select one component root to edit properties",
                  mgear.sev_error)


def build_from_selection(rebuild=False, *args):
    """Build rig from current selection

    Args:
        *args: None
    """
    # shifter.log_window()
    # rg = shifter.Rig()
    # rg.buildFromSelection()

    if not cmds.ls(sl=1):
        raise IndexError('Select guide root')

    gdeRoot = cmds.ls(sl=1)[0]

    if cmds.attributeQuery('rig_name', n=gdeRoot, ex=True)==False:
        raise TypeError('Select guide root')

    try: # Auto name rig
        import publish_path #'C:\encore\packages\mayaPublish\1.0.0\xxxx\AMD64-Windows\scripts'
        rigName = 'rig_%s' % publish_path.get_env_dict()['asset_name']
        cmds.setAttr(gdeRoot+'.rig_name', rigName, type='string')
    except: # Manually name rig
        rigName = cmds.getAttr(gdeRoot+'.rig_name')
        # if rigName == 'rig_assetName':
        #     raise NameError('Name the rig before building')
        # if not rigName.startswith('rig_'):
        #     raise NameError('Rig name needs to begin with " rig_ "')

    # Get post scripts
    postScriptLst = []
    if cmds.getAttr(gdeRoot+'.doPostCustomStep') == 1:
        if cmds.getAttr(gdeRoot+'.postCustomStep') != '':
            postAttr = cmds.getAttr(gdeRoot+'.postCustomStep')
            postScriptLst = postAttr.split(',')

    # Bypass
    if cmds.attributeQuery('bypass', n=gdeRoot, ex=True):
        bypass = cmds.getAttr(gdeRoot+'.bypass')
    else:
        bypass = True

    # Classic Channel Names
    if cmds.attributeQuery('classicChannelNames', n=gdeRoot, ex=True):
        ccn = cmds.getAttr(gdeRoot+'.classicChannelNames')
    else:
        ccn = False




    # Normal mGear build process
    if bypass == True:
        shifter.log_window()
        rg = None
        rg = shifter.Rig()
        rg.buildFromSelection(rebuild=rebuild)

    # Encore build process
    if bypass == False:
        # Set rig
        rg = None
        rg = shifter.Rig()
        rg.guide.setFromSelection()
        # Build rig
        a = None
        a = enc.PrePost(gdeRoot, rg.guide.components)
        a.preBuild(rigName)
        a.tPose()
        cmds.select(gdeRoot, r=True)


        try:
            rg.buildFromSelection(rebuild=rebuild)
            a.bindPose(rg, ccn)
            a.cleanUp(rigName)
        except:
            print('*** Build Try failed. running bindPose ***')
            a.bindPose(rg, ccn, fail=True)
            if rebuild == True:
                return 'False'
            else:
                return



    if rebuild == True:
        # Let MgearRebuild() run post scripts
        return postScriptLst, rg
    else:
        # Run post scripts
        if postScriptLst != []:
            rg.customStep(customSteps=postScriptLst)
    
    # Select deformer set members, to manually set joint radius.
    if cmds.objExists(rigName+'_deformers_grp'):
        cmds.select(rigName+'_deformers_grp', r=True)
        cmds.select('neutral_jnt', add=True)
        [cmds.setAttr(i+'.radius', 1.0) for i in cmds.ls(sl=1)]


def inspect_settings(tabIdx=0, *args):
    """Open the component or root setting UI.

    Args:
        tabIdx (int, optional): Tab index to be open when open settings
        *args: None

    Returns:
        None: None if nothing is selected
    """
    oSel = pm.selected()
    if oSel:
        root = oSel[0]
    else:
        pm.displayWarning(
            "please select one object from the componenet guide")
        return

    comp_type = False
    guide_root = False
    while root:
        if pm.attributeQuery("comp_type", node=root, ex=True):
            comp_type = root.attr("comp_type").get()
            break
        elif pm.attributeQuery("ismodel", node=root, ex=True):
            guide_root = root
            break
        root = root.getParent()
        pm.select(root)

    if comp_type:
        guide = shifter.importComponentGuide(comp_type)
        wind = pyqt.showDialog(guide.componentSettings, dockable=True)
        wind.tabs.setCurrentIndex(tabIdx)

    elif guide_root:
        module_name = "mgear.shifter.guide"
        level = -1 if sys.version_info < (3, 3) else 0
        guide = __import__(module_name, globals(), locals(), ["*"], level)
        wind = pyqt.showDialog(guide.guideSettings, dockable=True)
        wind.tabs.setCurrentIndex(tabIdx)

    else:
        pm.displayError(
            "The selected object is not part of component guide")


def extract_controls(*args):
    """Extract the selected controls from the rig to use it in the new build

    The controls shapes are stored under the controller_org group.
    The controls are renamed witht "_controlBuffer" suffix

    Args:
        *args: None
    """
    oSel = pm.selected()

    try:
        cGrp = pm.PyNode("controllers_org")
    except TypeError:
        cGrp = False
        mgear.log(
            "Not controller group in the scene or the group is not unique",
            mgear.sev_error)
    for x in oSel:
        try:
            old = pm.PyNode(cGrp.name() + "|"
                            + x.name().split("|")[-1] + "_controlBuffer")
            pm.delete(old)
        except TypeError:
            pass
        new = pm.duplicate(x)[0]
        pm.parent(new, cGrp, a=True)
        pm.rename(new, x.name() + "_controlBuffer")
        toDel = new.getChildren(type="transform")
        pm.delete(toDel)
        try:
            pm.sets("rig_*_controllers_grp", remove=new)
        except TypeError:
            pass

        try:
            pm.sets("rig_*_mocapFK_grp", remove=new)
        except TypeError:
            pass

