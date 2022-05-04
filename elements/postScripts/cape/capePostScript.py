from math import pow,sqrt
from collections import OrderedDict

'''
Build mGear rig with cape components

Run buildMembraine() to build nurbs surfaces.


______
I ended up converting the smooth srf to poly to paint proper base weights
cmds.nurbsToPoly("cape_C0_membraineN1_drvrebuiltSurface1", uss=1, ch=1, ft=0.01, d=0.1, pt=1, f=1, 
                                        mrt=0, mel=0.001, ntr=0, vn=3, pc=200, chr=0.9, un=3, 
                                        vt=1, ut=1, ucr=0, cht=0.2, mnd=1, es=0, uch=0)
Then transfer the weights to n2
______




Duplicate smooth nurb surf (n2)

Build strap ik ctls on duplicate surface (n3)
 - remove the connection between n3 dorito srf and n3 drv (transformGeo)
 - delete export and delete skincluster on d3 dorito srf
 - orient ctlRef for each controller to align with cape
 - import skincluster on n3 dorito srf, and match transform from drv to dor
 - break connections on ctlRef rotations. Matrix constrain ctlRef rot to mGear fk ctl

Bind cape skin to dor srf joints
 - create inverted shape for draped blendshape (one bs node per shape)
 - connect bs as pre-deformation, driven by mGear ctl ori Y (paint L & R weight maps)

Add sine wave deformer on n2 surface

Drive n3 with n2 using match point position


'''

def buildMembraine():
    capeDict = OrderedDict()

    capeDict['capeSecondary_R0_0_jnt'] = '.cv[0][0]'
    capeDict['capeSecondary_R0_1_jnt'] = '.cv[0][1]'
    capeDict['capeSecondary_R0_2_jnt'] = '.cv[0][2]'
    capeDict['capeSecondary_R0_3_jnt'] = '.cv[0][3]'
    capeDict['capeSecondary_R0_4_jnt'] = '.cv[0][4]'
    capeDict['capeSecondary_R0_4_end'] = '.cv[0][5]'

    capeDict['capePrimary_C0_0_jnt'] = '.cv[1][0]'
    capeDict['capePrimary_C0_1_jnt'] = '.cv[1][1]'
    capeDict['capePrimary_C0_2_jnt'] = '.cv[1][2]'
    capeDict['capePrimary_C0_3_jnt'] = '.cv[1][3]'
    capeDict['capePrimary_C0_4_jnt'] = '.cv[1][4]'
    capeDict['capePrimary_C0_4_end'] = '.cv[1][5]'

    capeDict['capeSecondary_L0_0_jnt'] = '.cv[2][0]'
    capeDict['capeSecondary_L0_1_jnt'] = '.cv[2][1]'
    capeDict['capeSecondary_L0_2_jnt'] = '.cv[2][2]'
    capeDict['capeSecondary_L0_3_jnt'] = '.cv[2][3]'
    capeDict['capeSecondary_L0_4_jnt'] = '.cv[2][4]'
    capeDict['capeSecondary_L0_4_end'] = '.cv[2][5]'


    keyLst = []
    keyLst=(capeDict.keys())

    #Create Nurbs
    n1 = cmds.nurbsPlane(ch=1, d=1, u=2, v=5, p=(0, 0, 0), w=0.1, ax=(0, 1, 0), lr=1, n='cape_C0_membraineN1_drv')[0]

    #Move cv's to match joint pos
    for k,v in capeDict.iteritems():
        if k.endswith('_end'): # Create transforms to extend the nurbs surface past chain
            prvIdx = keyLst.index(k)-1
            dstIdx = keyLst.index(k)-2 # to get distance between
           
            prvJnt = keyLst[prvIdx]
            dstJnt = keyLst[dstIdx]

            tmpTra = cmds.createNode('transform', n='keyTemp'+k, ss=True)
            prvPos = cmds.xform(prvJnt, q=True, m=True, ws=True)
            dist = distBetween(dstJnt, prvJnt)

            cmds.xform(tmpTra, m=prvPos) # move transform into joint position
            cmds.parent(tmpTra, prvJnt)  # parent transform to joint to zero out
            
            # R side mirror option OFF        
            # if '_R0_' in k:
            #     cmds.setAttr(tmpTra+'.tx', -dist)
            # else:
            #     cmds.setAttr(tmpTra+'.tx', dist)

            # R side mirror option ON        
            cmds.setAttr(tmpTra+'.tx', dist)

            pos = cmds.xform(tmpTra, q=True, t=True, ws=True)
            cmds.xform(n1+v, t=pos, ws=True)
            cmds.delete(tmpTra)
        else:
            pos = cmds.xform(k, q=True, t=True, ws=True)
            cmds.xform(n1+v, t=pos, ws=True)

    sknJts = [] # remove '_end' entries
    [sknJts.append(i) for i in keyLst if not i.endswith('_end')]

    #Set skinweights to 100% per jnt
    cmds.skinCluster(sknJts, n1, mi=2, bm=0, sm=0, dr=4, wd=0, tsb=1, n='cape_C0_membraineN1_skn')
    for k,v in capeDict.iteritems():
        if k.endswith('_end'):
            prvIdx = keyLst.index(k)-1
            prvJnt = keyLst[prvIdx]
            cmds.skinPercent('cape_C0_membraineN1_skn', n1+v, transformValue=[(prvJnt, 1.0)])
        else:
            cmds.skinPercent('cape_C0_membraineN1_skn', n1+v, transformValue=[(k, 1.0)])

    #Convert to smooth nurbs
    n2 = cmds.rebuildSurface("cape_C0_membraineN1_drv", rt=0, kc=0, fr=0, ch=1, end=1, 
                                sv=0, su=0, kr=0, dir=2, kcp=0, tol=0.01, dv=3, du=2, rpo=0)[0]
    # prepSrf for strap rig
    cmds.reverseSurface(n1, d=3, ch=0, rpo=1)
    cmds.reverseSurface(n1, d=1, ch=0, rpo=1)
    cmds.delete(n2, ch=True)

    cmds.skinCluster(sknJts, n2, mi=2, bm=0, sm=0, dr=4, wd=0, tsb=1, n='cape_C0_membraineN2_skn')
    cmds.copySkinWeights(ss='cape_C0_membraineN1_skn', ds='cape_C0_membraineN2_skn', noMirror=True)

    #Clean up
    #cmds.parent(n1, n2, 'wingFeatherBuilder')
    cmds.setAttr(n1+'.v', 0)
    cmds.select(None)

def distBetween(obj1, obj2):
    pos1 = cmds.xform(obj1, q=True, t=True, ws=True)
    pos2 = cmds.xform(obj2, q=True, t=True, ws=True)
    # Distance formula : √((x2 - x1)2 + (y2 - y1)2 + (z2 - z1)2)
    distance = sqrt(pow(pos1[0]-pos2[0],2)+pow(pos1[1]-pos2[1],2)+pow(pos1[2]-pos2[2],2))
    return distance