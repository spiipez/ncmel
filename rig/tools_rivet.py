# System modules.
from imp import reload
import re

# Maya modules.
import maya.cmds as mc

# ncscript modules.
from ncTools.rig import node
from ncTools.rig import util
reload(node)
reload(util)

def rivet_on_surface(name, side, nurbsurface, objsticky, paramuv, aimvec, upvec):
    ''' Create rivet attach on surface from uv parameter. 
    
            Args :
                name (str) = Name
                side (str) = L, R
                nurbsurface (str) = Surface name
                objsticky (str) = Object name
                paramuv (list) = [0,0]
                aimvec (str) = x, y or z
                upvec (str) = x, y or z
            Return :
                posi, cross, fbf_mtx, mult_mtx, dec_mtx, qte
    '''
    nurbsurface = util.register_node(nurbsurface)
    objsticky = util.register_node(objsticky)
    side = util.set_side(side)
    posi = node.PointOnSurfaceInfo('{}{}Posi'.format(name, side))
    cross = node.VectorProduct('{}{}Cross'.format(name, side))
    fbf_mtx = node.FourByFourMatrix('{}Comp{}FbfMtx'.format(name, side))
    mult_mtx = node.MultMatrix('{}{}MulMtx'.format(name, side))
    dec_mtx = node.DecomposeMatrix('{}{}DcmMtx'.format(name, side))
    qte = node.QuatToEuler('{}{}Qte'.format(name, side))

    cross.attr("operation").value = 2
    posi.attr('turnOnPercentage').value = 1
    posi.attr('parameterU').value = paramuv[0]
    posi.attr('parameterV').value = paramuv[1]

    nurbsurface.shape.attr('worldSpace[0]') >> posi.attr('inputSurface')
    posi.attr('normalizedTangentV') >> cross.attr('input1')
    posi.attr('normalizedNormal') >> cross.attr('input2')
    fbf_mtx.attr('output') >> mult_mtx.attr('matrixIn').last()
    objsticky.attr('parentInverseMatrix[0]') >> mult_mtx.attr('matrixIn').last()
    mult_mtx.attr('matrixSum') >> dec_mtx.attr('inputMatrix')
    objsticky.attr('ro') >> dec_mtx.attr('inputRotateOrder')
    objsticky.attr('ro') >> qte.attr('inputRotateOrder')
    dec_mtx.attr('outputQuat') >> qte.attr('inputQuat')
    dec_mtx.attr('outputTranslate') >> objsticky.attr('t')
    qte.attr('outputRotate') >> objsticky.attr('r')

    vtpd = 'xyz'
    for j in (aimvec, upvec):
        vtpd = vtpd.replace(j,'')

    vct = 'xyz'
    for ix, ax in enumerate('XYZ'):
        aim_fbf = str(vct.index(aimvec)) + str(ix)
        up_fbf = str(vct.index(upvec)) + str(ix)
        vtpd_fbf = str(vct.index(vtpd)) + str(ix)

        posi.attr('normalizedTangentV{}'.format(ax)) >> fbf_mtx.attr('in{}'.format(aim_fbf))
        posi.attr('normalizedNormal{}'.format(ax)) >> fbf_mtx.attr('in{}'.format(up_fbf))
        cross.attr('output{}'.format(ax)) >> fbf_mtx.attr('in{}'.format(vtpd_fbf))
        posi.attr('position{}'.format(ax)) >> fbf_mtx.attr('in3{}'.format(ix))

    return posi, cross, fbf_mtx, mult_mtx, dec_mtx, qte

def rivet_on_mesh(name, side = '', mesh = '', edge1 = '', edge2 = ''):
    ''' Create rivet attach on mesh from two edge. 
    
            Args :
                name (str) = Name.
                side (str) = L, R
                mesh (str) = Mesh name.
                edge1 (str) = "obj.e[10]"
                edge2 (str) = "obj.e[20]"
            Return :
                rvt, posi, loft, cfme_a, cfme_b, fbf_mtx, dec_mtx
    '''
    mesh = util.register_node(mesh)
    side = util.set_side(side)

    edge1_id = re.findall(r'\d+', '{}\n'.format(edge1))[-1]
    edge2_id = re.findall(r'\d+', '{}\n'.format(edge2))[-1]
    
    rvt = node.Transform('{}Rivet{}Grp'.format(name, side))

    cfme_a = node.CurveFromMeshEdge('{}A{}Cfme'.format(name, side))
    cfme_b = node.CurveFromMeshEdge('{}B{}Cfme'.format(name, side))
    cfme_a.attr('ei[0]').value = int(edge1_id)
    cfme_b.attr('ei[0]').value = int(edge2_id)
    cfme_a.attr('ihi').value = 1
    cfme_b.attr('ihi').value = 1

    mesh.shape.attr('worldMesh[0]') >> cfme_a.attr('inputMesh')
    mesh.shape.attr('worldMesh[0]') >> cfme_b.attr('inputMesh')

    loft = node.Loft('{}{}Loft'.format(name, side))
    loft.attr('u').value = True
    loft.attr('rsn').value = True

    cfme_a.attr('outputCurve') >> loft.attr('inputCurve[0]')
    cfme_b.attr('outputCurve') >> loft.attr('inputCurve[1]')

    posi = node.PointOnSurfaceInfo('{}{}Posi'.format(name, side))
    posi.attr('turnOnPercentage').value = 1
    posi.attr('parameterU').value = 0.5
    posi.attr('parameterV').value = 0.5

    loft.attr('outputSurface') >> posi.attr('inputSurface')

    fbf_mtx = node.FourByFourMatrix('{}Comp{}FbfMtx'.format(name, side))
    dec_mtx = node.DecomposeMatrix('{}{}DcmMtx'.format(name, side))

    posi.attr('positionX') >> fbf_mtx.attr('in30')
    posi.attr('positionY') >> fbf_mtx.attr('in31')
    posi.attr('positionZ') >> fbf_mtx.attr('in32')
    posi.attr('normalizedNormalX') >> fbf_mtx.attr('in20')
    posi.attr('normalizedNormalY') >> fbf_mtx.attr('in21')
    posi.attr('normalizedNormalZ') >> fbf_mtx.attr('in22')
    posi.attr('normalizedTangentVX') >> fbf_mtx.attr('in00')
    posi.attr('normalizedTangentVY') >> fbf_mtx.attr('in01')
    posi.attr('normalizedTangentVZ') >> fbf_mtx.attr('in02')
    posi.attr('normalizedTangentUX') >> fbf_mtx.attr('in10')
    posi.attr('normalizedTangentUY') >> fbf_mtx.attr('in11')
    posi.attr('normalizedTangentUZ') >> fbf_mtx.attr('in12')

    fbf_mtx.attr('output') >> dec_mtx.attr('inputMatrix')
    dec_mtx.attr('outputTranslate') >> rvt.attr('t')
    dec_mtx.attr('outputRotate') >> rvt.attr('r')

    return rvt, posi, loft, cfme_a, cfme_b, fbf_mtx, dec_mtx

def rivet_on_edge(name, side = '', mesh = '', edge = ''):
    ''' Create rivet attach on mesh from edge.
    
            Args :
                name (str) = Name.
                side (str) = L, R
                mesh (str) = Mesh name.
                edge (str) = "obj.e[10]"
            Return :
                rvt, poci, cfme
    '''
    mesh = util.register_node(mesh)
    side = util.set_side(side)

    edge_id = re.findall(r'\d+', '{}\n'.format(edge))[-1]
    
    rvt = node.Transform('{}Rivet{}Grp'.format(name, side))

    cfme = node.CurveFromMeshEdge('{}A{}Cfme'.format(name, side))
    cfme.attr('ihi').value = 1
    cfme.attr('ei[0]').value = int(edge_id)
    
    poci = node.PointOnCurveInfo('{}{}Poci'.format(name, side))
    poci.attr('turnOnPercentage').value = 1
    poci.attr('parameter').value = 0.5
    
    mesh.shape.attr('worldMesh[0]') >> cfme.attr('inputMesh')
    cfme.attr('outputCurve') >> poci.attr('inputCurve')
    poci.attr('position') >> rvt.attr('t')

    return rvt, poci, cfme

def uvpin_on_components(mesh = '', objs = [], newTemp = False, useRotate = True, maintainOffset = True):
    ''' Create uvPin with mesh from components.
    
            Args :
                mesh (str) = Mesh name.
                objs (list) = List object name.
                newTemp (bool) = Create new temp for uvPin.
                useRotate (bool) = If you use rotate set True.
                maintainOffset (bool) = The position and rotation of the constrained object will be maintained.
            Return :
                List object
    '''
    mesh = util.register_node(mesh)
    all_shape = mesh.get_all_shapes()
    shape = False
    pin_list = list()

    #-- Get shapes node
    for shp in all_shape:
        io = shp.attr('intermediateObject').value
        if not io == 1:
            shape = shp
    
    #-- Check object types
    if util.is_mesh(shape):
        wAttr = 'worldMesh[0]'

    elif util.is_surface(shape):
        wAttr = 'worldSpace[0]'

        if components == [0]:
            components = [[0,0]]

    #-- Check exists uvPin nodes
    uvpin_node = mc.listConnections('{}.{}'.format(shape, wAttr), t = 'uvPin')
    
    if not uvpin_node:
        uvpin_node = node.UvPin('{}{}UvPin'.format(mesh.prefix, mesh.side))
        shape.attr(wAttr) >> uvpin_node.attr('deformedGeometry')
    else:
        uvpin_node = util.register_node(uvpin_node[0])

    #-- Check all connect history
    connect_list = list()
    output_connect = mc.listConnections('{}.outputMatrix'.format(uvpin_node), c = True)
    for output in output_connect:
        connect_list.append(output[0].split('.')[-1])
    
    #-- Find parameter uv and connect to object
    i = len(connect_list)
    for obj in objs:
        pin_obj = util.register_node(obj)

        prefix = pin_obj.prefix
        side = pin_obj.side

        paramU, paramV = util.find_closest_param_on_mesh(mesh, obj)
        uvpin_node.attr('coordinate[{}]'.format(i)).value = (paramU, paramV)
        
        exit = False
        while not exit:
            if 'outputMatrix[{}]'.format(i) in connect_list:
                i+=1
            else:
                exit = True

        if newTemp:
            pin_obj = node.Transform('{}{}UvPin'.format(prefix, side))
            uvpin_node.attr('outputMatrix[{}]'.format(i)) >> pin_obj.attr('offsetParentMatrix')

            if useRotate:
                mc.parentConstraint(pin_obj, obj, mo = maintainOffset)
            else:
                mc.pointConstraint(pin_obj, obj, mo = maintainOffset)
        else:
            mult = node.MultMatrix('{}{}MulMtx'.format(prefix, side))
            dec = node.DecomposeMatrix('{}{}DcmMtx'.format(prefix, side))

            uvpin_node.attr('outputMatrix[{}]'.format(i)) >> mult.attr('matrixIn[1]')
            pin_obj.attr('parentInverseMatrix[0]') >> mult.attr('matrixIn[2]')
            mult.attr('matrixSum') >> dec.attr('inputMatrix')

            if maintainOffset:
                par_obj = node.Transform()
                par_posi = uvpin_node.attr('outputMatrix[{}]'.format(i)).value
                par_obj.attr('offsetParentMatrix').value = par_posi

                parentWorldMatrix = par_obj.attr('worldInverseMatrix[0]').value
                objWorldMatrix = pin_obj.attr('worldMatrix[0]').value
                offsetValue = objWorldMatrix * parentWorldMatrix
                mult.attr('localOffset').value = offsetValue
                mc.delete(par_obj)

            dec.attr('outputTranslate') >> pin_obj.attr('t')

            if useRotate:
                dec.attr('outputRotate') >> pin_obj.attr('r')

        pin_list.append(pin_obj)
        i+=1

    return pin_list

def stick_control_to_closest_uv_on_mesh(mesh = '', controller = [], newTemp = False, useRotate = False, counter = True):
    ''' Stick controls to mesh with uvPin.
    
            Args :
                mesh (str) = Mesh name.
                controller (list) = List object controls name.
                newTemp (bool) = Create new temp for uvPin.
                useRotate (bool) = If you use rotate set True.
                constraint (bool) = Default is connections. But if you want constraint set true.
                counter (bool) = Counter controls for facial detail.
            Return :
                List pin group.
    '''
    pinGrp_list = list()
    for ctrl in controller:
        ctrl = util.register_node(ctrl)
        pinGrp = ctrl.get_parent()
        pinGrp_list.append(pinGrp)
        
        if counter:
            if not mc.listConnections('{}.offsetParentMatrix'.format(ctrl)):
                mc.connectAttr('{}.inverseMatrix'.format(ctrl), '{}.offsetParentMatrix'.format(ctrl))

    pinGrp_list = uvpin_on_components(mesh = mesh, objs = pinGrp_list, newTemp = newTemp, useRotate = useRotate, maintainOffset = True)
    return pinGrp_list

def stick_control_to_closest_vertex_on_mesh(ctrl = '', mesh = '', counter = True):
    ''' Stick controls to mesh with rivet on edge.
    
            Args :
                ctrl (str) = Controls name.
            Return :
                rvt (Dag) =
                poci (Dag) =
                cfme (Dag) =
                pntcons (Dag) =
    '''
    ctrl = util.register_node(ctrl)
    posi_grp = ctrl.get_parent()

    if counter:
        if not mc.listConnections('{}.offsetParentMatrix'.format(ctrl)):
            mc.connectAttr('{}.inverseMatrix'.format(ctrl), '{}.offsetParentMatrix'.format(ctrl))

    vtx_closet, face_closet = util.find_closest_vertex_and_face_on_mesh(mesh, ctrl)

    edges = mc.polyListComponentConversion(vtx_closet, te = True)
    edge = mc.ls(edges, fl = True)[0]

    rvt, poci, cfme = rivet_on_edge(ctrl.prefix, ctrl.side, mesh, edge)
    pntcons = util.point_constraint(rvt, posi_grp, mo = True)

    return rvt, poci, cfme, pntcons

def get_weight_value(obj, skn_name = ''):
    '''
    '''
    infs = mc.skinCluster(skn_name, q = True, inf = True)
    vtx_dict = dict()
    for inf in infs:
        val = mc.skinPercent(skn_name, obj, q = True, v = True, t = inf)
        if val > 0:
            vtx_dict[inf] = (val)
    return vtx_dict

def constraint_from_dict(obj, vtx_dict):
    for each, wgt in vtx_dict.iteritems():
        util.parent_constraint(each, obj, mo = True, w = wgt)

def vertex_constraint(obj_list = [], mesh = ''):
    '''
    '''
    if not obj_list == [] and not mesh == '':
        if mc.objExists(mesh):
            for obj in obj_list:
                if mc.objExists(obj) :
                    obj = util.register_node(obj)
                    mesh = util.register_node(mesh)
                    skn = mc.mel.eval("findRelatedSkinCluster {};".format(mesh.shape))

                    if skn:
                        vtx_closet, face_closet = util.find_closest_vertex_and_face_on_mesh(mesh, obj)
                        vtx_dict = get_weight_value(vtx_closet, skn)
                        constraint_from_dict(obj, vtx_dict)
                        obj.add_bool_tag('vertexConstraint', True)
                        obj.add_str_tag('meshConstraint', mesh)
                    else:
                        mc.warning( "SkinCluster not found. Plese check skin." )
                else :
                    print(obj)

def clear_vertex_constraint(obj_list = []):
    '''
    '''
    if not obj_list == []:
        for obj in obj_list:
            obj = util.register_node(obj)
            if hasattr(obj, 'vertexConstraint'):
                mc.delete(obj, constraints = True)
                mc.deleteAttr('{}.vertexConstraint'.format(obj))
                mc.deleteAttr('{}.meshConstraint'.format(obj))
                
def update_vertex_constraint(obj_list = []):
    '''
    '''
    if not obj_list == []:
        for obj in obj_list :
            obj = util.register_node(obj)
            if hasattr(obj, 'vertexConstraint'):
                if obj.attr('vertexConstraint').value == True:
                    mc.delete(obj, constraints = True)
                    vertex_constraint([obj], obj.attr('meshConstraint').value)
  
def clear_all_vertex_constraint():
    objs = mc.ls(dag = True, tr = True)
    clear_vertex_constraint(objs)
                
def update_all_vertex_constraint():
    objs = mc.ls(dag = True, tr = True)
    update_vertex_constraint(objs)