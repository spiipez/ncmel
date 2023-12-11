# System modules.
from imp import reload

# Maya modules.
import maya.cmds as mc

# ncscript modules.
from ncTools.rig import node
from ncTools.rig import util
reload(node)
reload(util)

def joint_placer(name = '', side = '', numJnts = 8, aim = (0,1,0), upvec = (0,0,-1)):
    '''
    '''
    
    if not name:
        name = 'joint'
    
    side = util.set_side(side)
            
    curve_sel = util.register_node(mc.polyToCurve( name = 'Full_Crv', 
                                                   form = 0, 
                                                   degree = 1, 
                                                   conformToSmoothMeshPreview = 0, 
                                                   ch = False )[0])
    
    all_cvs = mc.getAttr('{}.cp'.format(curve_sel), s = 1)
    mid_point = all_cvs/2
    diff = 0
    
    if (all_cvs % 2) == 0:
        mid_point = mid_point-1
        diff = 1
        
    position_list = list()
    for i in list(range(0, all_cvs)):
        cv_posi = mc.pointPosition('{}.cv[{}]'.format(curve_sel, i))
        position_list.append(cv_posi)
    
    cuv_a = mc.curve(n = 'HalfA_Crv', degree = 1, p = position_list[0:mid_point])
    cuv_b = mc.curve(n = 'HalfB_Crv', degree = 1, p = position_list[:mid_point+diff:-1])
    
    mc.rebuildCurve(cuv_a, rt = 0, end = 1, kep = 1, d = 3, s = 0)
    mc.rebuildCurve(cuv_b, rt = 0, end = 1, kep = 1, d = 3, s = 0)

    nrb = util.register_node(mc.loft(cuv_a, cuv_b, n = 'Temp_Nrb', ch = False, d = 1)[0])
    
    animCuv = mc.createNode('animCurveTU')
    mc.setKeyframe(animCuv, t = 1, v = 0.015)
    mc.setKeyframe(animCuv, t = (numJnts/2)+1, v = 0.65)
    mc.setKeyframe(animCuv, t = numJnts, v = 0.99)
    mc.keyTangent(animCuv, e = True, a = True, t = (1,1), itt = "linear", ott = "linear")
    mc.keyTangent(animCuv, e = True, a = True, t = (numJnts,numJnts), itt = "linear", ott = "linear")
    mc.keyTangent(animCuv, e = True, a = True, t = ((numJnts/2)+1,(numJnts/2)+1), itt = "linear", ott = "linear")
    
    jnt_list = list()
    for i in list(range(1, numJnts+1)):
        v_val = mc.keyframe( animCuv, 
                             t = (i,i), 
                             q = True, 
                             eval = True) [0]

        null = node.Transform()
        posi = node.PointOnSurfaceInfo()

        posi.attr('turnOnPercentage').value = 1
        posi.attr('parameterU').value = 0.5
        posi.attr('parameterV').value = v_val
        nrb.shape.attr('worldSpace[0]') >> posi.attr('inputSurface')
        posi.attr('position') >> null.attr('t')
        
        aimcons = node.AimConstraint()
        aimcons.attr('a').value = aim
        aimcons.attr('u').value = upvec
        posi.attr('n') >> aimcons.attr('wu')
        posi.attr('tv') >> aimcons.attr('tg[0].tt')
        aimcons.attr('cr') >> null.attr('r')
        
        jnt = mc.createNode("joint", name = "{}{}{}TmpJnt".format(name, i, side))
        mc.matchTransform(jnt, null)
        mc.makeIdentity(jnt, a = True)

        if not i == 1:
            mc.parent(jnt, jnt_list[-1])

        jnt_list.append(jnt)
        mc.delete(null, posi, aimcons)

    mc.delete(curve_sel, cuv_a, cuv_b, nrb)
    mc.select(cl = True)