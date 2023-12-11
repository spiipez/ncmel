# System modules.
from imp import reload

# Maya modules.
import maya.cmds as mc
import maya.OpenMaya as om

# ncscript modules.
from ncTools.rig import core
from ncTools.rig import node
reload(core)
reload(node)


def register_node(names):
    '''
    '''
    def _register_(name):
        if is_transform(name):
            return core.Dag(name)
        else:
            return core.Node(name)
    
    if type(names) == list:
        return tuple([_register_(name) for name in names])
    else:
        return _register_(names)

def is_transform(name):
    '''
    '''
    mObj = get_MObject(name)
    if mObj.hasFn(om.MFn.kTransform):
        return True
    return False

def is_mesh(name):
    '''
    '''
    if is_transform(name):
        mObj = get_MObject(mc.listRelatives(name, s = True, ni = True, pa = True)[0])
        if mObj.hasFn(om.MFn.kMesh):
            return True
    else:
        mObj = get_MObject(name)
        if mObj.hasFn(om.MFn.kMesh):
            return True

    return False

def is_surface(name):
    '''
    '''
    if is_transform(name):
        mObj = get_MObject(mc.listRelatives(name, s = True, ni = True, pa = True)[0])
        if mObj.hasFn(om.MFn.kSurface):
            return True
    else:
        mObj = get_MObject(name)
        if mObj.hasFn(om.MFn.kSurface):
            return True

    return False

def is_curve(name):
    '''
    '''
    if is_transform(name):
        mObj = get_MObject(mc.listRelatives(name, s = True, ni = True, pa = True)[0])
        if mObj.hasFn(om.MFn.kNurbsCurve):
            return True
    else:
        mObj = get_MObject(name)
        if mObj.hasFn(om.MFn.kNurbsCurve):
            return True
        
    return False

def is_joint(name):
    '''
    '''
    mObj = get_MObject(name)
    if mObj.hasFn(om.MFn.kJoint):
        return True
    return False

def is_shape(name):
    '''
    '''
    mObj = get_MObject(name)
    if mObj.hasFn(om.MFn.kShape):
        return True
    return False

def is_equal(x, y, tolerance = 0.00001):
    '''
    '''
    return abs(x-y) < tolerance

def normalize_vector(vector = (0,0,0)):
    '''
    '''
    normal = om.MVector(vector[0],vector[1],vector[2]).normal()
    return (normal.x,normal.y,normal.z)

def dot_product(vector1 = (0.0,0.0,0.0), vector2 = (0.0,0.0,0.0)):
    '''
    '''
    vec1 = om.MVector(vector1[0], vector1[1], vector1[2])
    vec2 = om.MVector(vector2[0], vector2[1], vector2[2])
    return vec1 * vec2

def cross_product(vector1 = (0.0,0.0,0.0), vector2 = (0.0,0.0,0.0)):
    '''
    '''
    vec1 = om.MVector(vector1[0], vector1[1], vector1[2])
    vec2 = om.MVector(vector2[0], vector2[1], vector2[2])
    crossProduct = vec1 ^ vec2
    return (crossProduct.x, crossProduct.y, crossProduct.z)

def offset_vector(point1 = (0.0,0.0,0.0), point2 = (0.0,0.0,0.0)):
    '''
    '''
    pnt1 = om.MPoint(point1[0], point1[1], point1[2], 1.0)
    pnt2 = om.MPoint(point2[0], point2[1], point2[2], 1.0)
    vec = pnt2 - pnt1
    return (vec.x, vec.y, vec.z)

def distance_between(point1 = [0.0,0.0,0.0], point2 = [0.0,0.0,0.0]):
    '''
    '''
    pnt1 = om.MPoint(point1[0], point1[1], point1[2], 1.0)
    pnt2 = om.MPoint(point2[0], point2[1], point2[2], 1.0)
    return om.MVector(pnt1-pnt2).length()

def average_position(pos1 = (0.0,0.0,0.0), pos2 = (0.0,0.0,0.0), weight = 0.5):
    '''
    '''
    return (pos1[0]+((pos2[0]-pos1[0])*weight),
            pos1[1]+((pos2[1]-pos1[1])*weight),
            pos1[2]+((pos2[2]-pos1[2])*weight))

def get_MObject(name):
    ''' Get om.MObject from name

            Args: 
                name (str): Name of object
            Return:
                om.MObject
    '''
    if not mc.objExists(name):
        raise Exception('Object "'+ name +'" does not exist !!')
    
    mSel = om.MSelectionList()
    mSel.add(str(name))
    mObj = om.MObject()
    mSel.getDependNode(0, mObj)
    return mObj

def get_MDagPath(name):
    ''' Get om.MDagPath from name

            Args: 
                name (str): Name of object
            Return:
                om.MDagPath
    '''
    if not mc.objExists(name):
        raise Exception('Object "'+ name +'" does not exist !!')
    
    mObj = get_MObject(str(name))

    if not mObj.hasFn(om.MFn.kDagNode):
        return None

    mDagPath = om.MDagPath().getAPathTo(mObj)
    return mDagPath

def get_position(object):
    '''
    '''
    pos = list()
    mObj = get_MObject(object)

    if mObj.hasFn(om.MFn.kTransform):
        try: pos = mc.xform(object, q = True, ws = True, rp = True)
        except: pass

    if not pos:
        try: pos = mc.pointPosition(object)
        except: pass
    
    if not pos:
        try: pos = mc.xform(object, q = True, ws = True, rp = True)
        except: pass

    if not pos:
        raise Exception('Invalid point value supplied! Unable to determine type of point "'+str(object)+'"!')
        
    return pos

def get_MPoint(point):
    ''' Get om.MPoint from name

            Args: 
                point (str): Name of object
            Return:
                om.MPoint
    '''
    if type(point) == om.MPoint: 
        return point
    pos = get_position(point)
    mPoint = om.MPoint(pos[0], pos[1], pos[2], 1.0)
    return mPoint

def get_MPointArray(geometry, worldSpace = True):
    '''
    '''
    if geometry and not mc.objExists(geometry):
        raise Exception('Object "'+geometry+'" does not exist!')
    
    point_list = om.MPointArray()
    if get_MObject(geometry).hasFn(om.MFn.kTransform):
        try: geometry = mc.listRelatives(geometry, s = True, ni = True, pa = True)[0]
        except: raise Exception('Object "'+geometry+'" contains no valid geometry!')

    if worldSpace:
        shapeObj = get_MDagPath(geometry)
        mSpace = om.MSpace.kWorld
    else:
        shapeObj = get_MObject(geometry)
        mSpace = om.MSpace.kObject

    shapeType = mc.objectType(geometry)
    if shapeType == 'mesh':
        meshFn = om.MFnMesh(shapeObj)
        meshFn.getPoints(point_list, mSpace)

    elif shapeType == 'nurbsCurve':
        curveFn = om.MFnNurbsCurve(shapeObj)
        curveFn.getCVs(point_list, mSpace)

    elif shapeType == 'nurbsSurface':
        surfaceFn = om.MFnNurbsSurface(shapeObj)
        surfaceFn.getCVs(point_list, mSpace)

    return point_list

def get_postion_all_components(geometry, worldSpace = True):
    '''
    '''
    components = []
    mPtArray = get_MPointArray(geometry, worldSpace)
    
    for i in range(mPtArray.length()):
        components.append([mPtArray[i][0], mPtArray[i][1], mPtArray[i][2]])
    
    return components

def get_all_components(geometry):
    '''
    '''
    if geometry and not mc.objExists(geometry):
        raise Exception('Object "'+geometry+'" does not exist!')
    
    mSel = om.MSelectionList()
    mSel.add(geometry)
    mDagPath = om.MDagPath()
    mSel.getDagPath(0, mDagPath)
    mDagPath.extendToShape()

    components = None
    if mDagPath.hasFn(om.MFn.kMesh):
        fn_mesh = om.MFnMesh(mDagPath)
        num_vertices = fn_mesh.numVertices()

        components = '{}.vtx[0:{}]'.format(mDagPath.partialPathName(), num_vertices-1)
    
    elif mDagPath.hasFn(om.MFn.kNurbsCurve):
        fn_curve = om.MFnNurbsCurve(mDagPath)
        spans = fn_curve.numSpans()
        degree = fn_curve.degree()
        form = fn_curve.form()
        num_cvs = spans + degree

        if form == 3:
            num_cvs -= degree

        components = '{}.cv[0:{}]'.format(mDagPath.partialPathName(), num_cvs - 1)
    
    elif mDagPath.hasFn(om.MFn.kNurbsSurface):
        fn_nurbs = om.MFnNurbsSurface(mDagPath)
        spans_u = fn_nurbs.numSpansInU()
        degree_u = fn_nurbs.degreeU()
        spans_v = fn_nurbs.numSpansInV()
        degree_v = fn_nurbs.degreeV()
        form_u = fn_nurbs.formInU()
        form_v = fn_nurbs.formInV()

        num_u = spans_u + degree_u
        if form_u == 3:
            num_u -= degree_u

        num_v = spans_v + degree_v
        if form_v == 3:
            num_v -= degree_v

        components = '{}.cv[0:{}][0:{}]'.format(mDagPath.partialPathName(),num_u - 1,num_v - 1)

    return mc.ls(components, fl = True)

def get_MBoundingBox(geometry, worldSpace = True):
    '''
    '''
    if geometry and not mc.objExists(geometry):
        raise Exception('Object "'+geometry+'" does not exist!')
    
    mDagPath = get_MDagPath(geometry)
    mDagNode = om.MFnDagNode(mDagPath)
    mBbox = mDagNode.boundingBox()

    if worldSpace:
        mBbox.transformUsing(mDagPath.exclusiveMatrix())
    else:
        mBbox.transformUsing(mDagNode.transformationMatrix().inverse())
    
    return mBbox

def get_boundingBox(geometry, worldSpace = True):
    '''
    '''
    if geometry and not mc.objExists(geometry):
        raise Exception('Object "'+geometry+'" does not exist!')
    
    mDagPath = om.MDagPath()
    mSel = om.MSelectionList()
    bbox = om.MBoundingBox()
    shapes = mc.ls(mc.listRelatives(geometry, ad = True, pa = True), noIntermediate = True, geometry = True, visible = True)
    
    for shape in shapes:
        mSel.clear()
        om.MGlobal.getSelectionListByName(shape, mSel)
        mSel.getDagPath(0,mDagPath)
        bboxShape = om.MFnDagNode(mDagPath).boundingBox()

        if worldSpace:
            bboxShape.transformUsing(mDagPath.inclusiveMatrix())

        bbox.expand(bboxShape)

    min_bb = bbox.min()
    max_bb = bbox.max()

    return [min_bb.x, min_bb.y, min_bb.z, max_bb.x, max_bb.y, max_bb.z]

def get_boundingBox_center(geometry, worldSpace = True):
    '''
    '''
    bbox = get_MBoundingBox(geometry, worldSpace = worldSpace)
    bbct = bbox.center()
    return [bbct[0], bbct[1], bbct[2]]

def get_boundingBox_scale(geometry, worldSpace = True):
    '''
    '''
    bb_min = get_MBoundingBox(geometry, worldSpace).min()
    bb_max = get_MBoundingBox(geometry, worldSpace).max()
    scale = [bb_max[i]-bb_min[i] for i in range(3)]
    return scale

def compare_boundingBox(geometryA, geometryB, tol = 0.001):
    '''
    '''
    geoA = register_node(geometryA)
    geoB = register_node(geometryB)

    visA = geoA.attr('v').value
    visB = geoB.attr('v').value

    geoA.attr('v').value = 1
    geoB.attr('v').value = 1

    for __aa, __bb in ([get_boundingBox_center(geometryA), get_boundingBox_center(geometryB)],
                     [get_boundingBox_scale(geometryA), get_boundingBox_scale(geometryB)],
                     [get_boundingBox(geometryA), get_boundingBox(geometryB)]):

        for valA, valB in zip(__aa, __bb):
            if not ((valA - tol) <= valB <= (valA + tol)):
                geoA.attr('v').value = visA
                geoB.attr('v').value = visB
                return False
    return True

def get_MfnMesh(obj):
    ''' Return MFnMesh of the given object name.

            Args :
                obj (str) = Object name.
            Return :
                OpenMaya.MFnMesh of the object.
    '''
    try:
        mSel = om.MSelectionList()
        mSel.add(obj)
        mDagPath = om.MDagPath()
        mSel.getDagPath(0, mDagPath)
        return om.MFnMesh(mDagPath)
    except:
        om.MGlobal.displayError('OpenMaya.MDagPath() failed on {}.'.format(obj))
        return None

def get_mesh_data(mesh):
    '''
    '''
    meshDag = get_MDagPath(mesh)
    meshMfn = om.MFnMesh(meshDag)

    data = dict()
    data['edges'] = meshMfn.numEdges()
    data['faces'] =  meshMfn.numPolygons()
    data['vertices'] = meshMfn.numVertices()
    data['faceVertices'] = meshMfn.numFaceVertices()
    data['centerPivot'] = mc.objectCenter(mesh, gl = True)
    data['pivot'] = mc.xform(mesh, q = True, ws = True, rp = True)

    return data

def compare_mesh(meshA, meshB, tol = 0.001):
    '''
    '''
    dataA = get_mesh_data(meshA)
    dataB = get_mesh_data(meshB)

    if not compare_boundingBox(meshA, meshB):
        return False

    for poly in ('faces', 'vertices'):
        if not dataA[poly] == dataB[poly]:
            return False
        
    for piv in ('pivot', 'centerPivot'):
        if not ((dataA[piv] - tol) <= dataB[piv] <= (dataA[piv] + tol)):
            return False
    return True

def get_MfnCurve(curve):
    '''
    '''
    try:
        mSel = om.MSelectionList()
        mSel.add(curve)
        curveDag = om.MDagPath()
        mSel.getDagPath(0, curveDag)
        return om.MFnNurbsCurve(curveDag)
    except:
        om.MGlobal.displayError('OpenMaya.MDagPath() failed on {}.'.format(curve))
        return None
    
def get_curve_data(curve):
    '''
    '''
    curveDag = get_MDagPath(curve)
    curveMfn = om.MFnNurbsCurve(curveDag)

    cuv_data = dict()
    cuv_data['degree'] = int(curveMfn.degree())
    cuv_data['form'] = int(curveMfn.form())-1
    cuv_data['spans'] = int(curveMfn.numSpans())

    knots = om.MDoubleArray()
    curveMfn.getKnots(knots)
    cuv_data['knots'] = [int(ix) for ix in knots]

    cvs = om.MPointArray()
    curveMfn.getCVs(cvs, om.MSpace.kObject)
    cuv_data['cvs'] = [(cvs[ix].x, cvs[ix].y, cvs[ix].z) for ix in range(cvs.length())]
    cuv_data['num_knots'] = curveMfn.numKnots()
    return cuv_data

def build_curve_from_data(curve_data, transform):
    '''
    '''
    shape = node.NurbsCurve('{}Shape'.format(transform), p = transform)
    values = ['{}.cc'.format(shape),
              curve_data['degree'],
              curve_data['spans'],
              curve_data['form'],
              False, 3,
              curve_data['knots'],
              curve_data['num_knots'],
              len(curve_data['cvs'])]
    
    values += curve_data['cvs']
    mc.setAttr(*values, type = 'nurbsCurve')

def get_param_from_curve(curve, value):
    '''
    '''
    if not is_curve(curve):
        raise Exception('Object '+curve+' is not a valid nurbs curve!')

    lenght = mc.arclen(curve)
    if value > lenght:
        print('Input length is greater than actual curve length. Returning maximum U value!')
        return mc.getAttr(curve+'.maxValue')
    
    curveMfn = get_MfnCurve(curve)
    param = curveMfn.findParamFromLength(lenght * value)
    return param

def get_point_at_param(curve, param):
    '''
    '''
    if not is_curve(curve):
        raise Exception('Object '+curve+' is not a valid nurbs curve!')
    
    curveMfn = get_MfnCurve(curve)
    mPoint = om.MPoint()
    curveMfn.getPointAtParam(param, mPoint)
    return [mPoint.x, mPoint.y, mPoint.z]
    
def create_joint_to_ep_curve(name, curve, side = '', skip = 0):
    '''
    '''
    if side == str():
        side = '_'

    cuv = get_curve_data(curve)
    spans = cuv['spans']
    jnt_list = list()

    ep = 0
    count = 1
    while ep <= spans:
        posi = get_position('{}.ep[{}]'.format(curve, ep))
        jnt = joint('{}{}{}Jnt'.format(name, count, side))
        jnt.attr('t').value = posi
        jnt_list.append(jnt)
        ep+=(skip+1)
        count+=1

    return jnt_list

def create_ep_curve_to_joint(name, joint_list, rebuild = False):
    '''
    '''
    size = len(joint_list)
    position = [mc.xform(joint_list[i], q = True, ws = True, t = True) for i in range(0,size)]
    cuv = mc.curve(n = name, ep = position)

    if rebuild:
        mc.rebuildCurve(cuv, rt = 0, s = True)

    return cuv

def find_closest_vertex_and_face_on_mesh(mesh = '', obj = ''):
    ''' Get the cloest vertex on a geo from position given.

            Args :
                mesh (str) = Transform or Mesh to get cloest vertex from position.
                obj (str) = The position to calculate. Transform (ex. locator, grp) or vertex (ex. "obj.vtx[0]")
            Return :
                List closest vertex and face as PyNode.
    '''
    meshMfn = get_MfnMesh(obj = mesh)
    position = mc.xform(obj, q = True, rotatePivot = True, worldSpace = True)
    pointA = om.MPoint(*position)
    pointOnMesh = om.MPoint()

    util = om.MScriptUtil()
    util.createFromInt(0)
    idPointer = util.asIntPtr()

    meshMfn.getClosestPoint(pointA, pointOnMesh, om.MSpace.kWorld, idPointer) 
    fid = util.getInt(idPointer)

    faceVerts = om.MIntArray()
    meshMfn.getPolygonVertices(fid, faceVerts)

    dists = []
    for vi in range(faceVerts.length()):
        vtxPt = om.MPoint()
        vid = faceVerts[vi]
        meshMfn.getPoint(vid, vtxPt, om.MSpace.kWorld)
        distVec = pointA - vtxPt
        dists.append(distVec.length())

    closestVid = faceVerts[dists.index(min(dists))]
    closestVtx = '{}.vtx[{}]'.format(mesh, closestVid)
    closestFace = '{}.f[{}]'.format(mesh, fid)

    return [closestVtx, closestFace]

def find_closest_param_on_mesh(mesh = '', obj = ''):
    ''' Get the cloest uv on a geo from position given.
    
            Args :
                mesh (str) = Transform or Mesh to get cloest vertex from position.
                obj (str) = The position to calculate. Transform (ex. locator, grp) or vertex (ex. "obj.vtx[0]")
            Return :
                List closest u and v.
    '''
    meshMfn = get_MfnMesh(obj = mesh)
    position = mc.xform(obj, q = True, translation = True, worldSpace = True)
    mPoint = om.MPoint(*position)

    pArray = [0.0, 0.0]
    pointUtil = om.MScriptUtil()
    pointUtil.createFromList(pArray, 2)
    uvPoint = pointUtil.asFloat2Ptr()

    uvSetNames = []
    meshMfn.getUVSetNames(uvSetNames)

    meshMfn.getUVAtPoint(mPoint, uvPoint, om.MSpace.kWorld, uvSetNames[0])
    u = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 0)
    v = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 1)

    return [u,v]

def find_parallel_edges_from_point_on_mesh(closestVtx = '', closestFace = ''):
    ''' Convert closest vertex and closest face to parallel edges.
        Work with definition find_closest_vertex_and_face_on_mesh.
    
            Args :
                closestVtx (str) = "obj.vtx[10]"
                closestFace (str) = "obj.f[100]"
            Return :
                List two edge id.
    '''
    mesh = closestFace.node()
    closestFaceEdges = [mesh.e[i] for i in closestFace.getEdges()]
    closestVertEdges = closestVtx.connectedEdges()

    conEdgesOnFace = [e for e in closestVertEdges if e in closestFaceEdges]

    e1 = conEdgesOnFace[0]
    e1Con = conEdgesOnFace[1]

    parallelEdges = [i for i in closestFaceEdges if i not in (e1, e1Con)]
    if len(parallelEdges) == 1:  # it's a triangle
        e2 = e1Con
    else:
        e2s = [e for e in parallelEdges if e not in e1.connectedEdges()]
        e2 = e2s[0]

    return [e1,e2]

def find_closest_param_and_point_on_surface(nurbsSurface = '', obj = ''):
    ''' Get the cloest uv on a surface from position given.
    
            Args :
                nurbsSurface (str) = NurbsSurface name.
                obj (str) = The position to calculate (ex. locator, grp, joint, ctrl)
            Return :
                List closest u and v.
    '''
    pos = get_position(obj)
    nurbDag = get_MDagPath(nurbsSurface)
    nurbDag.extendToShape()
    nurbMfn = om.MFnNurbsSurface(nurbDag)
    mPoint = om.MPoint(*pos)
    closest_point = nurbMfn.closestPoint(mPoint)

    paramUtil = om.MScriptUtil()
    paramuPtr = paramUtil.asDoublePtr()
    paramvPtr = paramUtil.asDoublePtr()
    nurbMfn.getParamAtPoint(closest_point, paramuPtr, paramvPtr)
    param_u = paramUtil.getDouble(paramuPtr) 
    param_v = paramUtil.getDouble(paramvPtr)

    point = om.MPoint()
    nurbMfn.getPointAtParam(param_u, param_v, point)

    return [param_u, param_v] , [point.x, point.y, point.z]

def find_closest_param_and_point_on_curve(curve, object):
    '''
    '''
    pos = get_position(object)
    curveMfn = get_MfnCurve(curve)
    mPoint = om.MPoint(*pos)

    paramUtil = om.MScriptUtil()
    paramUtil.createFromDouble(0.0)
    paramPtr = paramUtil.asDoublePtr()
    curveMfn.closestPoint(mPoint, paramPtr, 0.001, om.MSpace.kWorld)
    param = paramUtil.getDouble(paramPtr)

    point = om.MPoint()
    curveMfn.getPointAtParam(param, point)

    return param , [point.x, point.y, point.z]

def find_position_normal_and_tangent_on_surface(surface, param_u, param_v):
    '''
    '''
    mSel = om.MSelectionList()
    mSel.add(surface)
    nrbDag = om.MDagPath()
    mSel.getDagPath(0, nrbDag)

    nrbDag.extendToShape()
    nurbMfn = om.MFnNurbsSurface(nrbDag)

    point = om.MPoint()
    nurbMfn.getPointAtParam(param_u, param_v, point)

    normal = nurbMfn.normal(param_u, param_v, om.MSpace.kWorld)
    
    tangent_u = om.MVector()
    tangent_v = om.MVector()
    nurbMfn.getTangents(param_u, param_v, tangent_u, tangent_v, om.MSpace.kWorld)

    return mvec_to_tuple(point), mvec_to_tuple(normal), mvec_to_tuple(tangent_u), mvec_to_tuple(tangent_v)

def set_position_and_normal_on_surface(object, surface, param_u, param_v, aim, upvec, target_translate, world_up):
    '''
    '''
    mSel = om.MSelectionList()
    mSel.add(surface)
    nrbDag = om.MDagPath()
    mSel.getDagPath(0, nrbDag)
    nrbDag.extendToShape()

    nrbMfn = om.MFnNurbsSurface(nrbDag)

    point = om.MPoint()
    nrbMfn.getPointAtParam(param_u, param_v, point)

    normal = nrbMfn.normal(param_u, param_v, om.MSpace.kWorld)
    
    tangent_u = om.MVector()
    tangent_v = om.MVector()
    nrbMfn.getTangents(param_u, param_v, tangent_u, tangent_v, om.MSpace.kWorld)

    tt = mvec_to_tuple(normal)
    if target_translate == 'u':
        tt = mvec_to_tuple(tangent_u)
    elif target_translate == 'v':
        tt = mvec_to_tuple(tangent_v)

    wu = mvec_to_tuple(normal)
    if world_up == 'u':
        wu = mvec_to_tuple(tangent_u)
    elif world_up == 'v':
        wu = mvec_to_tuple(tangent_v)

    obj = register_node(object)
    obj.attr('t').value = [point.x, point.y, point.z]
    aimcon = create('aimConstraint')
    aimcon.attr('cr') >> obj.attr('r')
    aimcon.attr('aimVector').value = aim
    aimcon.attr('upVector').value = upvec
    aimcon.attr('tg[0].tt').value = tt
    aimcon.attr('worldUpVector').value = wu
    mc.delete(aimcon)

def expand_curve(curve = '', axis = 'x', offset = 0.1):
    '''
    '''
    cuv_list = list()
    for i in (1, -1):
        curve = mc.duplicate(curve)[0]
        mc.setAttr('{}.t{}'.format(curve, axis), offset*i)
        cuv_list.append(curve)
    return cuv_list

def calculate_uv_parameter(numJnt, offset = None):
    ''' Calculate UV value for Ribbon 
    '''
    param_list = list()
    
    if offset == None:
        offset = (.5/numJnt)
    
    uv = (1.0 -(offset*2))
    numJnt = numJnt
    step = uv/(numJnt-1)
    param = offset 
    
    for i in range(numJnt):
        param_list.append(param)
        param += step
    return param_list

def reset_point_of_mesh(mesh_shape):
    '''
    '''
    mDagPath = get_MDagPath(mesh_shape)
    mObj = mDagPath.node()
    meshMfn = om.MFnMesh(mObj)
    pntsPlug = meshMfn.findPlug('pnts', False)

    for i in range(meshMfn.numVertices()):
        pnts_plug_element = pntsPlug.elementByLogicalIndex(i)
        for num in range(3):
            pnts_plug_element.child(num).setFloat(0)
    return True

def get_deformers(obj, deformers):
    '''
    '''
    deformers = []
    if deformers:
        listDef = [deformers]
    else :
        listDef = ['skinCluster', 'tweak', 'cluster']
    
    for df in listDef:
        try :
            def_node = mc.listConnections(obj, type = df)
            def_set = mc.listConnections(def_node, type = 'objectSet')
            
            deformers.append(def_node)
            deformers.append(def_set)
        except TypeError:
            continue
    return deformers

def duplicate_and_clean(object):
    '''
    '''
    dupp = register_node(mc.duplicate(object, rr = True)[0])
    shapes = dupp.get_all_shapes()
    
    for attr in ('t', 'r', 's', 'v'):
        dupp.attr(attr).lock = False
        dupp.attr(attr).hide = False

    if not shapes:
        return dupp

    for shp in shapes:
        if shp.attr('intermediateObject').value:
            mc.delete(shp)

    return dupp

def get_orig_shape(object):
    '''
    '''
    obj = register_node(object)
    shapes = obj.get_all_shapes()

    origShpsDct = dict()
    origShpsDct['used'] = list()
    origShpsDct['unused'] = list()

    for shp in shapes:
        if shp.attr('intermediateObject').value:
            ins = shp.attr('inMesh').get_input()
            outs_mesh = shp.attr('outMesh').get_output()
            outs_worldMesh = shp.attr('worldMesh').get_output()
            
            if not ins and (outs_mesh or outs_worldMesh):
                origShpsDct['used'] += [shp]
            elif not ins and not outs_mesh and not outs_worldMesh:
                origShpsDct['unused'] += [shp]

    return origShpsDct

def counter_controls(controller):
    ''' Add multiplyDivide for counter controls.
    
            Args :
                ctrl (str) = Controls name.
            Return :
                MultiplyDivide node.
    '''
    ctrl = register_node(ctrl)
    inv_grp = register_node(ctrl.get_parent())

    mdv = node.MultiplyDivide()
    mdv.attr('i2').value = [-1]*3

    ctrl.attr('t') >> mdv.attr('i1')
    mdv.attr('o') >> inv_grp.attr('t')

    prefix = ctrl.prefix
    side = ctrl.side
    mdv.name = '{}{}Inv'.format(prefix, side)

    return mdv

def curve_guide(start_obj, end_obj):
    '''
    '''
    side = start_obj.side
    prefix = start_obj.prefix

    cuv = register_node(mc.curve(d = 1, p = [( 0,0,0 ),( 0,0,0 )]))
    cuv.name = '{}Line{}Crv'.format(prefix, side)
    grp = group(cuv)

    mc.rename(mc.cluster('{}.cv[0]'.format(cuv), wn = (start_obj, start_obj))[0], '{}St{}Clstr'.format(prefix, side))
    mc.rename(mc.cluster('{}.cv[1]'.format(cuv), wn = (end_obj, end_obj))[0], '{}En{}Clstr'.format(prefix, side))

    mc.rename(mc.listRelatives(start_obj, shapes = True, f = True)[-1],'{}St{}ClstrHandleShape'.format(prefix, side))
    mc.rename(mc.listRelatives(end_obj, shapes = True, f = True)[-1],'{}En{}ClstrHandleShape'.format(prefix, side))

    cuv.attr('overrideEnabled').value = 1
    cuv.attr('overrideDisplayType').value = 2
    cuv.attr('inheritsTransform').value = 0
    cuv.lhtrs()

    mc.select(cl = True)
    return cuv, grp

def unlock_trs(dag_object = '', attr_list = 'trs'):
    '''
    '''
    attr_lock = list()
    for __attr in attr_list:
        for __chld in ('xyz'):
            attr_chld = __attr + __chld
            if dag_object.attr(attr_chld).lock:
                dag_object.attr(attr_chld).lock = False
                attr_lock.append(attr_chld)
    return attr_lock

def parent_constraint(*args, **kwargs):
    '''
    '''
    target = register_node(args[-1])
    attr_unlock = unlock_trs(target, 'tr')

    parcons = register_node(mc.parentConstraint(*args, **kwargs)[0])
    parcons.attr('interpType').value = 2
    
    for __attr in attr_unlock:
        target.attr(__attr).lock = True

    return parcons

def point_constraint(*args, **kwargs):
    '''
    '''
    target = register_node(args[-1])
    attr_unlock = unlock_trs(target, 't')

    pntcons = register_node(mc.pointConstraint(*args, **kwargs)[0])
    
    for __attr in attr_unlock:
        target.attr(__attr).lock = True

    return pntcons

def orient_constraint(*args, **kwargs):
    '''
    '''
    target = register_node(args[-1])
    attr_unlock = unlock_trs(target, 'r')

    oricons = register_node(mc.orientConstraint(*args, **kwargs)[0])
    oricons.attr('interpType').value = 2
    
    for __attr in attr_unlock:
        target.attr(__attr).lock = True

    return oricons

def scale_constraint(*args, **kwargs):
    '''
    '''
    return register_node(mc.scaleConstraint(*args, **kwargs)[0])

def aim_constraint(*args, **kwargs):
    '''
    '''
    return register_node(mc.aimConstraint(*args, **kwargs)[0])

def trs_constraint(*args, **kwargs):
    par_cons = parent_constraint(*args, **kwargs)
    scl_cons = scale_constraint(*args, **kwargs)
    return par_cons, scl_cons

def remove_connected_constraints(obj):
    '''
    '''
    mc.delete(mc.listConnections(obj, s = True, d = False, type = 'constraint'))

def mvec_to_tuple(mvec):
    '''
    '''
    return (mvec.x, mvec.y, mvec.z)

def connect_trs(dagA, dagB):
    '''
    '''
    for attr in ('t', 'r', 's'):
        dagA.attr(attr) >> dagB.attr(attr)

def get_local_offset_matrix(dag, target):
    '''
    '''
    dag_world_inverse = dag.attr('worldInverseMatrix[0]').value
    target_world = target.attr('worldMatrix[0]').value
    multiply_list = [target_world[i] * dag_world_inverse[i] for i in range(len(dag_world_inverse))]
    return multiply_list

def get_local_offset(dag, target):
    '''
    '''
    pars = create('transform')
    trgt = create('transform')
    pars.snap(dag)
    trgt.snap(target)
    mc.parent(trgt, pars)
    value = trgt.attr('t').value
    mc.delete(pars)
    return value
    
def curve_param(shape = ''):
    '''
    '''
    param = { 'defualt'     : [(0.5234,0.0,-0.9065),(0.0,0.0,-1.0467),(-0.5234,0.0,-0.9065),(-0.9065,0.0,-0.5234),(-1.0467,0.0,-0.0),(-0.9065,0.0,0.5234),(-0.5234,0.0,0.9065),(0.0,0.0,1.0467),(0.5234,0.0,0.9065),(0.9065,0.0,0.5234),(1.0467,0.0,0.0),(0.9065,0.0,-0.5234),(0.5234,0.0,-0.9065),(0.0,0.0,-1.0467),(-0.5234,0.0,-0.9065)],    
              'sphere'      : [(0,1.250064,0),(0,1,0),(1.93883e-007,0.92388,-0.382683),(3.58248e-007,0.707107,-0.707107),(4.68074e-007,0.382683,-0.923879),(5.06639e-007,0,-1),(0,0,-1.250064),(5.06639e-007,0,-1),(4.68074e-007,-0.382683,-0.923879),(3.58248e-007,-0.707107,-0.707107),(1.93883e-007,-0.92388,-0.382683),(0,-1,0),(0,-1.250064,0),(0,-1,0),(-5.70243e-008,-0.92388,0.382683),(-1.05367e-007,-0.707107,0.707107),(-1.37669e-007,-0.382683,0.92388),(-1.49012e-007,0,1),(0,0,1.250064),(-1.49012e-007,0,1),(-1.37669e-007,0.382683,0.92388),(-1.05367e-007,0.707107,0.707107),(-5.70243e-008,0.92388,0.382683),(0,1,0),(0.382683,0.92388,0),(0.707107,0.707107,0),(0.92388,0.382683,0),(1,0,0),(1.250064,0,0),(1,0,0),(0.92388,-0.382683,0),(0.707107,-0.707107,0),(0.382683,-0.92388,0),(0,-1,0),(0,-1.250064,0),(0,-1,0),(-0.382683,-0.92388,-1.36858e-007),(-0.707107,-0.707107,-2.52881e-007),(-0.92388,-0.382683,-3.30405e-007),(-1,0,-3.57628e-007),(-1.250064,0,0),(-1,0,-3.57628e-007),(-0.92388,0,0.382683),(-0.707107,0,0.707107),(-0.382684,0,0.923879),(-1.49012e-007,0,1),(0.382683,0,0.92388),(0.707107,0,0.707107),(0.92388,0,0.382683),(1,0,0),(0.92388,0,-0.382683),(0.707107,0,-0.707106),(0.382684,0,-0.923879),(5.06639e-007,0,-1),(-0.382683,0,-0.92388),(-0.707106,0,-0.707107),(-0.923879,0,-0.382684),(-1,0,-3.57628e-007),(-0.92388,0.382683,-3.30405e-007),(-0.707107,0.707107,-2.52881e-007),(-0.382683,0.92388,-1.36858e-007),(0,1,0)],
              'sphere2'     : [(0,0.671954,0),(-0.475143,0.475143,-7.08019e-08),(-0.671954,0,-1.00129e-07),(-0.475143,-0.475143,-7.08019e-08),(0,-0.671954,0),(-0.237572,-0.475143,0.411486),(-0.335977,0,0.581929),(-0.237572,0.475143,0.411486),(0,0.671954,0),(0.237572,0.475143,0.411486),(0.335977,0,0.581929),(0.237572,-0.475143,0.411486),(0,-0.671954,0),(0.475143,-0.475143,0),(0.671954,0,0),(0.475143,0.475143,0),(0,0.671954,0),(0.237572,0.475143,-0.411486),(0.335977,0,-0.581929),(0.237572,-0.475143,-0.411486),(0,-0.671954,0),(-0.237572,-0.475143,-0.411486),(-0.335977,0,-0.581929),(-0.237572,0.475143,-0.411486),(0,0.671954,0),(0.237572,0.475143,0.411486),(0.475143,0.475143,0),(0.237572,0.475143,-0.411486),(-0.237572,0.475143,-0.411486),(-0.475143,0.475143,-7.08019e-08),(-0.237572,0.475143,0.411486),(0.237572,0.475143,0.411486),(0.335977,0,0.581929),(0.671954,0,0),(0.335977,0,-0.581929),(-0.335977,0,-0.581929),(-0.671954,0,-1.00129e-07),(-0.335977,0,0.581929),(0.335977,0,0.581929),(0.237572,-0.475143,0.411486),(0.475143,-0.475143,0),(0.237572,-0.475143,-0.411486),(-0.237572,-0.475143,-0.411486),(-0.475143,-0.475143,-7.08019e-08),(-0.237572,-0.475143,0.411486),(0.237572,-0.475143,0.411486)],
              'cylinder'    : [(-2.98023e-008,0.5,1),(0.309017,0.5,0.951057),(0.587785,0.5,0.809017),(0.809017,0.5,0.587785),(0.951057,0.5,0.309017),(1,0.5,0),(0.951057,0.5,-0.309017),(0.809018,0.5,-0.587786),(0.587786,0.5,-0.809017),(0.309017,0.5,-0.951057),(0,0.5,-1),(-0.309017,0.5,-0.951057),(-0.587785,0.5,-0.809017),(-0.809017,0.5,-0.587785),(-0.951057,0.5,-0.309017),(-1,0.5,0),(-0.951057,0.5,0.309017),(-0.809017,0.5,0.587785),(-0.587785,0.5,0.809017),(-0.309017,0.5,0.951057),(-2.98023e-008,0.5,1),(-2.98023e-008,-0.5,1),(0.309017,-0.5,0.951057),(0.587785,-0.5,0.809017),(0.698401,-0.5,0.698401),(0.698401,0.5,0.698401),(0.698401,-0.5,0.698401),(0.809017,-0.5,0.587785),(0.951057,-0.5,0.309017),(1,-0.5,0),(1,0.5,0),(1,-0.5,0),(0.951057,-0.5,-0.309017),(0.809018,-0.5,-0.587786),(0.698402,-0.5,-0.698402),(0.698402,0.5,-0.698402),(0.698402,-0.5,-0.698402),(0.587786,-0.5,-0.809017),(0.309017,-0.5,-0.951057),(0,-0.5,-1),(0,0.5,-1),(0,-0.5,-1),(-0.309017,-0.5,-0.951057),(-0.587785,-0.5,-0.809017),(-0.698401,-0.5,-0.698401),(-0.698401,0.5,-0.698401),(-0.698401,-0.5,-0.698401),(-0.809017,-0.5,-0.587785),(-0.951057,-0.5,-0.309017),(-1,-0.5,0),(-1,0.5,0),(-1,-0.5,0),(-0.951057,-0.5,0.309017),(-0.809017,-0.5,0.587785),(-0.698401,-0.5,0.698401),(-0.698401,0.5,0.698401),(-0.698401,-0.5,0.698401),(-0.587785,-0.5,0.809017),(-0.309017,-0.5,0.951057),(-2.98023e-008,-0.5,1),(-2.98023e-008,0.5,1)],
              'halfCylinder': [(1.016543,0.166667,0.314921),(1,0.166667,0),(0.951057,0.166667,-0.309017),(0.809018,0.166667,-0.587786),(0.587786,0.166667,-0.809017),(0.309017,0.166667,-0.951057),(0,0.166667,-1),(-0.309017,0.166667,-0.951057),(-0.587785,0.166667,-0.809017),(-0.809017,0.166667,-0.587785),(-0.951057,0.166667,-0.309017),(-1,0.166667,0),(-1.016544,0.166667,0.314921),(-1.016544,-0.166667,0.314921),(-1,-0.166667,0),(-0.951057,-0.166667,-0.309017),(-0.951057,0.166667,-0.309017),(-0.951057,-0.166667,-0.309017),(-0.809017,-0.166667,-0.587785),(-0.587785,-0.166667,-0.809017),(-0.587785,0.166667,-0.809017),(-0.587785,-0.166667,-0.809017),(-0.309017,-0.166667,-0.951057),(0,-0.166667,-1),(0,0.166667,-1),(0,-0.166667,-1),(0.309017,-0.166667,-0.951057),(0.587786,-0.166667,-0.809017),(0.587786,0.166667,-0.809017),(0.587786,-0.166667,-0.809017),(0.809018,-0.166667,-0.587786),(0.951057,-0.166667,-0.309017),(0.951057,0.166667,-0.309017),(0.951057,-0.166667,-0.309017),(1,-0.166667,0),(1.016543,-0.166667,0.314921),(1.016543,0.166667,0.314921)],
              'hexagon'     : [(-3.50988e-07,0,-1.000001),(0.866026,0,-0.500001),(0.866024,0,0.5),(-5e-07,0,1),(-0.866026,0,0.5),(-0.866026,0,-0.5),(-3.50988e-07,0,-1.000001)],
              'hexagon2'    : [(-5e-07,0.244444,1),(-5e-07,-0.244444,1),(0.866024,-0.244444,0.5),(0.866024,0.244444,0.5),(0.866026,0.244444,-0.500001),(0.866026,-0.244444,-0.500001),(-3.50988e-07,-0.244444,-1.000001),(-3.50988e-07,0.244444,-1.000001),(-0.866026,0.244444,-0.5),(-0.866026,-0.244444,-0.5),(-0.866026,-0.244444,0.5),(-0.866026,0.244444,0.5),(-5e-07,0.244444,0.999999),(0.866024,0.244444,0.5),(0.866024,-0.244444,0.5),(0.866026,-0.244444,-0.500001),(0.866026,0.244444,-0.500001),(-3.50988e-07,0.244444,-1.000001),(-3.50988e-07,-0.244444,-1.000001),(-0.866026,-0.244444,-0.5),(-0.866026,0.244444,-0.5),(-0.866026,0.244444,0.5),(-0.866026,-0.244444,0.5),(-5e-07,-0.244444,0.999999)],
              'octagon'     : [(0,0,-1),(0.707107,0,-0.707107),(1,0,0),(0.707107,0,0.707107),(0,0,1),(-0.707107,0,0.707107),(-1,0,0),(-0.707107,0,-0.707107),(0,0,-1)],
              'octagon2'    : [(0,-0.248316,1),(0.707107,-0.248316,0.707107),(0.707107,0.248316,0.707107),(1,0.248316,0),(1,-0.248316,0),(0.707107,-0.248316,-0.707107),(0.707107,0.248316,-0.707107),(0,0.248316,-1),(0,-0.248316,-1),(-0.707107,-0.248316,-0.707107),(-0.707107,0.248316,-0.707107),(-1,0.248316,0),(-1,-0.248316,0),(-0.707107,-0.248316,0.707107),(-0.707107,0.248316,0.707107),(0,0.248316,1),(0.707107,0.248316,0.707107),(0.707107,-0.248316,0.707107),(1,-0.248316,0),(1,0.248316,0),(0.707107,0.248316,-0.707107),(0.707107,-0.248316,-0.707107),(0,-0.248316,-1),(0,0.248316,-1),(-0.707107,0.248316,-0.707107),(-0.707107,-0.248316,-0.707107),(-1,-0.248316,0),(-1,0.248316,0),(-0.707107,0.248316,0.707107),(-0.707107,-0.248316,0.707107),(0,-0.248316,1),(0,0.248316,1)],
              'gear'        : [(0.8,0,0),(0.801101,0,-0.123621),(0.989358,0,-0.18479),(0.909024,0,-0.432032),(0.720767,0,-0.370864),(0.575441,0,-0.570887),(0.691791,0,-0.731028),(0.481474,0,-0.883832),(0.365124,0,-0.723691),(0.129983,0,-0.800093),(0.129983,0,-1),(-0.129983,0,-1),(-0.129983,0,-0.800093),(-0.365125,0,-0.723691),(-0.481474,0,-0.883832),(-0.691791,0,-0.731028),(-0.575441,0,-0.570887),(-0.720767,0,-0.370864),(-0.909024,0,-0.432032),(-0.989358,0,-0.18479),(-0.801101,0,-0.123621),(-0.8,0,0),(-0.801101,0,0.123621),(-0.989358,0,0.18479),(-0.909024,0,0.432032),(-0.720767,0,0.370864),(-0.575441,0,0.570887),(-0.691791,0,0.731028),(-0.481474,0,0.883832),(-0.365124,0,0.723691),(-0.129983,0,0.800093),(-0.129983,0,1),(0.129983,0,1),(0.129983,0,0.800093),(0.365124,0,0.723691),(0.481474,0,0.883832),(0.691791,0,0.731028),(0.575441,0,0.570887),(0.720767,0,0.370864),(0.909024,0,0.432032),(0.989358,0,0.18479),(0.801101,0,0.123621),(0.8,0,0),(0.488889,0,0),(0.488771,0,-0.0774137),(0.440926,0,-0.224663),(0.349921,0,-0.349921),(0.224663,0,-0.440927),(0.0774136,0,-0.488771),(-0.0774137,0,-0.488771),(-0.224663,0,-0.440926),(-0.349921,0,-0.349921),(-0.440926,0,-0.224663),(-0.488771,0,-0.0774137),(-0.488889,0,0),(-0.8,0,0),(-0.488889,0,0),(-0.488771,0,0.0774138),(-0.440926,0,0.224663),(-0.349921,0,0.349921),(-0.224663,0,0.440926),(-0.0774137,0,0.488771),(0.0774137,0,0.488771),(0.224663,0,0.440926),(0.349921,0,0.349921),(0.440926,0,0.224663),(0.488771,0,0.0774137),(0.488889,0,0)],
              'wing'        : [(0,0.122759,-2.916459),(0.0571398,0.127257,-2.916459),(0.112873,0.140637,-2.916459),(0.165826,0.162571,-2.916459),(0.214697,0.192519,-2.916459),(0.258281,0.229743,-2.916459),(0.295505,0.273327,-2.916459),(0.325452,0.322197,-2.916459),(0.347387,0.375151,-2.916459),(0.360767,0.430883,-2.916459),(0.365264,0.488023,-2.916459),(0.360767,0.545163,-2.916459),(0.347387,0.600896,-2.916459),(0.325452,0.653849,-2.916459),(0.295505,0.70272,-2.916459),(0.258281,0.746304,-2.916459),(0.214697,0.783528,-2.916459),(0.165826,0.813476,-2.916459),(0.112873,0.83541,-2.916459),(0.0571398,0.84879,-2.916459),(0,0.853287,-2.916459),(-0.0571398,0.84879,-2.916459),(-0.112873,0.83541,-2.916459),(-0.165826,0.813476,-2.916459),(-0.214697,0.783528,-2.916459),(-0.258281,0.746304,-2.916459),(-0.295505,0.70272,-2.916459),(-0.325452,0.653849,-2.916459),(-0.347387,0.600896,-2.916459),(-0.360767,0.545163,-2.916459),(-0.365264,0.488023,-2.916459),(-0.360767,0.430883,-2.916459),(-0.347387,0.375151,-2.916459),(-0.325452,0.322197,-2.916459),(-0.295505,0.273327,-2.916459),(-0.258281,0.229743,-2.916459),(-0.214697,0.192519,-2.916459),(-0.165826,0.162571,-2.916459),(-0.112873,0.140637,-2.916459),(-0.0571398,0.127257,-2.916459),(0,0.122759,-2.916459),(0,0.0123403,-2.916459),(0.0744132,0.0181971,-2.916459),(0.146994,0.0356218,-2.916459),(0.215955,0.0641868,-2.916459),(0.279599,0.103188,-2.916459),(0.336359,0.151665,-2.916459),(0.384836,0.208424,-2.916459),(0.423836,0.272068,-2.916459),(0.452401,0.341029,-2.916459),(0.456272,0.357529,-2.916607),(0.73085,0.368992,-2.916609),(1.155425,0.368992,-2.916609),(1.504183,0.300144,-2.916608),(1.873159,0.123101,-2.916608),(2.19159,-0.10804,-2.916608),(2.449367,-0.353931,-2.916608),(2.439648,-0.163295,-2.916607),(2.445447,0.139749,-2.916608),(2.46243,0.445513,-2.916608),(2.501708,0.760788,-2.916607),(2.562491,1.03607,-2.916608),(2.533029,0.75224,-2.916608),(2.512403,0.439675,-2.916608),(2.499802,0.142655,-2.916608),(2.499961,-0.162152,-2.916608),(2.50965,-0.339045,-2.916608),(2.540348,-0.353931,-2.916608),(2.597774,-0.112159,-2.916608),(2.747581,0.172277,-2.916608),(2.904269,0.354243,-2.916609),(3.111502,0.536202,-2.916607),(3.379389,0.664068,-2.916609),(3.662438,0.723076,-2.916609),(3.955598,0.703411,-2.916608),(4.248756,0.600134,-2.916608),(4.299301,0.605053,-2.916608),(4.053991,0.895076,-2.916608),(3.853741,1.211841,-2.916609),(3.68066,1.534294,-2.916608),(3.479258,2.010749,-2.91661),(3.382839,2.302032,-2.916609),(3.360927,2.423434,-2.916608),(3.519124,2.032771,-2.916606),(3.748934,1.576417,-2.916608),(3.954285,1.258058,-2.916608),(4.14873,0.982466,-2.916608),(4.375118,0.68866,-2.916609),(4.415554,0.67882,-2.916608),(4.338097,0.944418,-2.916609),(4.298544,1.338891,-2.916607),(4.357873,1.723727,-2.916608),(4.575418,2.108582,-2.916607),(4.792962,2.320233,-2.916608),(5.129167,2.522286,-2.916609),(5.513192,2.625657,-2.916608),(5.682916,2.666604,-2.916609),(4.446869,2.907122,-2.916609),(3.131715,3.176526,-2.916609),(2.993278,3.215008,-2.916608),(2.894394,3.186143,-2.916608),(2.835064,3.080308,-2.916608),(2.815287,2.907122,-2.916609),(2.706515,2.426069,-2.916606),(2.528524,1.973879,-2.916608),(2.360422,1.704494,-2.916608),(2.152766,1.406223,-2.916607),(1.94511,1.19457,-2.916608),(1.668236,0.99252,-2.916607),(1.430915,0.848206,-2.916609),(1.183705,0.732751,-2.916607),(0.837612,0.636542,-2.916608),(0.458201,0.607681,-2.916608),(0.452401,0.635017,-2.916459),(0.423836,0.703979,-2.916459),(0.384836,0.767623,-2.916459),(0.336359,0.824382,-2.916459),(0.279599,0.872859,-2.916459),(0.215955,0.91186,-2.916459),(0.146994,0.940425,-2.916459),(0.0744132,0.95785,-2.916459),(0,0.963706,-2.916459),(0,0.853287,-2.916459),(0,0.963706,-2.916459),(-0.0744132,0.95785,-2.916459),(-0.146994,0.940425,-2.916459),(-0.215955,0.91186,-2.916459),(-0.279599,0.872859,-2.916459),(-0.336359,0.824382,-2.916459),(-0.384836,0.767623,-2.916459),(-0.423836,0.703979,-2.916459),(-0.452401,0.635017,-2.916459),(-0.458201,0.607681,-2.916608),(-0.837612,0.636542,-2.916608),(-1.183705,0.732751,-2.916607),(-1.430915,0.848206,-2.916609),(-1.668236,0.99252,-2.916607),(-1.94511,1.19457,-2.916608),(-2.152766,1.406223,-2.916607),(-2.360422,1.704494,-2.916608),(-2.528524,1.973879,-2.916608),(-2.706515,2.426069,-2.916606),(-2.815287,2.907122,-2.916609),(-2.835064,3.080308,-2.916608),(-2.894394,3.186143,-2.916608),(-2.993278,3.215008,-2.916608),(-3.131715,3.176526,-2.916609),(-4.446869,2.907122,-2.916609),(-5.682916,2.666604,-2.916609),(-5.513192,2.625657,-2.916608),(-5.129167,2.522286,-2.916609),(-4.792962,2.320233,-2.916608),(-4.575418,2.108582,-2.916607),(-4.357873,1.723727,-2.916608),(-4.298544,1.338891,-2.916607),(-4.338097,0.944418,-2.916609),(-4.415554,0.67882,-2.916608),(-4.375118,0.68866,-2.916609),(-4.14873,0.982466,-2.916608),(-3.954285,1.258058,-2.916608),(-3.748934,1.576417,-2.916608),(-3.519124,2.032771,-2.916606),(-3.360927,2.423434,-2.916608),(-3.382839,2.302032,-2.916609),(-3.479258,2.010749,-2.91661),(-3.68066,1.534294,-2.916608),(-3.853741,1.211841,-2.916609),(-4.053991,0.895076,-2.916608),(-4.299301,0.605053,-2.916608),(-4.248756,0.600134,-2.916608),(-3.955598,0.703411,-2.916608),(-3.662438,0.723076,-2.916609),(-3.379389,0.664068,-2.916609),(-3.111502,0.536202,-2.916607),(-2.904269,0.354243,-2.916609),(-2.747581,0.172277,-2.916608),(-2.597774,-0.112159,-2.916608),(-2.540348,-0.353931,-2.916608),(-2.50965,-0.339045,-2.916608),(-2.499961,-0.162152,-2.916608),(-2.499802,0.142655,-2.916608),(-2.512403,0.439675,-2.916608),(-2.533029,0.75224,-2.916608),(-2.562491,1.03607,-2.916608),(-2.501708,0.760788,-2.916607),(-2.46243,0.445513,-2.916608),(-2.445447,0.139749,-2.916608),(-2.439648,-0.163295,-2.916607),(-2.449367,-0.353931,-2.916608),(-2.19159,-0.10804,-2.916608),(-1.873159,0.123101,-2.916608),(-1.504183,0.300144,-2.916608),(-1.155425,0.368992,-2.916609),(-0.73085,0.368992,-2.916609),(-0.456272,0.357529,-2.916607),(-0.452401,0.341029,-2.916459),(-0.423836,0.272068,-2.916459),(-0.384836,0.208424,-2.916459),(-0.336359,0.151665,-2.916459),(-0.279599,0.103188,-2.916459),(-0.215955,0.0641868,-2.916459),(-0.146994,0.0356218,-2.916459),(-0.0744132,0.0181971,-2.916459),(0,0.0123403,-2.916459)],
              'stick'       : [(0,0,0),(0,2.403515,0),(0,2.350383,0),(0.0366249,2.348464,0),(0.0728487,2.342726,0),(0.108274,2.333234,0),(0.142513,2.32009,0),(0.175191,2.303441,0),(0.20595,2.283465,0),(0.234452,2.260385,0),(0.260385,2.234452,0),(0.283465,2.20595,0),(0.303441,2.175191,0),(0.32009,2.142513,0),(0.333234,2.108274,0),(0.342726,2.072849,0),(0.348464,2.036625,0),(0.350383,2,0),(0.348464,1.963375,0),(0.342726,1.927151,0),(0.333234,1.891726,0),(0.32009,1.857487,0),(0.303441,1.824809,0),(0.283465,1.79405,0),(0.260385,1.765548,0),(0.234452,1.739615,0),(0.20595,1.716535,0),(0.175191,1.696559,0),(0.142513,1.67991,0),(0.108274,1.666766,0),(0.0728487,1.657274,0),(0.0366249,1.651536,0),(0,1.649617,0),(-0.0366249,1.651536,0),(-0.0728487,1.657274,0),(-0.108274,1.666766,0),(-0.142513,1.67991,0),(-0.175191,1.696559,0),(-0.20595,1.716535,0),(-0.234452,1.739615,0),(-0.260385,1.765548,0),(-0.283465,1.79405,0),(-0.303441,1.824809,0),(-0.32009,1.857487,0),(-0.333234,1.891726,0),(-0.342726,1.927151,0),(-0.348464,1.963375,0),(-0.350383,2,0),(-0.403515,2,0),(0.403515,2,0),(-0.350383,2,0),(-0.348464,2.036625,0),(-0.342726,2.072849,0),(-0.333234,2.108274,0),(-0.32009,2.142513,0),(-0.303441,2.175191,0),(-0.283465,2.20595,0),(-0.260385,2.234452,0),(-0.234452,2.260385,0),(-0.20595,2.283465,0),(-0.175191,2.303441,0),(-0.142513,2.32009,0),(-0.108274,2.333234,0),(-0.0728487,2.342726,0),(-0.0366249,2.348464,0),(0,2.350383,0)],
              'stickSphere' : [(0,0,0),(0,1.647774,0),(0,1.674585,0.134791),(0,1.750939,0.249062),(0,1.865209,0.325415),(0,2,0.352226),(0,2.134791,0.325415),(0,2.249062,0.249062),(0,2.325415,0.134791),(0,2.352227,0),(0,2.325415,-0.134791),(0,2.249062,-0.249062),(0,2.134791,-0.325415),(0,2,-0.352226),(0,1.865209,-0.325415),(0,1.750939,-0.249062),(0,1.674585,-0.134791),(0,1.647774,0),(0.134791,1.674585,0),(0.249062,1.750939,0),(0.325415,1.865209,0),(0.352226,2,0),(0.325415,2.134791,0),(0.249062,2.249062,0),(0.134791,2.325415,0),(0,2.352227,0),(-0.134791,2.325415,0),(-0.249062,2.249062,0),(-0.325415,2.134791,0),(-0.352226,2,0),(-0.325415,1.865209,0),(-0.249062,1.750939,0),(-0.134791,1.674585,0),(0,1.647774,0),(0,1.674585,0.134791),(0,1.750939,0.249062),(0,1.865209,0.325415),(0,2,0.352226),(0.249062,2,0.249062),(0.352226,2,0),(0.249062,2,-0.249062),(0,2,-0.352226),(-0.249062,2,-0.249062),(-0.352226,2,0),(-0.249062,2,0.249062),(0,2,0.352226)],
              'stickSquare' : [(0,0,0),(0,1.65,0),(-0.35,1.65,0),(-0.35,2.35,0),(0.35,2.35,0),(0.35,1.65,0),(0,1.65,0)],
              'stickCircle' : [(0,0,0),(0,1.649617,0),(-0.0366249,1.651536,0),(-0.0728487,1.657274,0),(-0.108274,1.666766,0),(-0.142513,1.67991,0),(-0.175191,1.696559,0),(-0.20595,1.716535,0),(-0.234452,1.739615,0),(-0.260385,1.765548,0),(-0.283465,1.79405,0),(-0.303441,1.824809,0),(-0.32009,1.857487,0),(-0.333234,1.891726,0),(-0.342726,1.927151,0),(-0.348464,1.963375,0),(-0.350383,2,0),(-0.348464,2.036625,0),(-0.342726,2.072849,0),(-0.333234,2.108274,0),(-0.32009,2.142513,0),(-0.303441,2.175191,0),(-0.283465,2.20595,0),(-0.260385,2.234452,0),(-0.234452,2.260385,0),(-0.20595,2.283465,0),(-0.175191,2.303441,0),(-0.142513,2.32009,0),(-0.108274,2.333234,0),(-0.0728487,2.342726,0),(-0.0366249,2.348464,0),(0,2.350383,0),(0.0366249,2.348464,0),(0.0728487,2.342726,0),(0.108274,2.333234,0),(0.142513,2.32009,0),(0.175191,2.303441,0),(0.20595,2.283465,0),(0.234452,2.260385,0),(0.260385,2.234452,0),(0.283465,2.20595,0),(0.303441,2.175191,0),(0.32009,2.142513,0),(0.333234,2.108274,0),(0.342726,2.072849,0),(0.348464,2.036625,0),(0.350383,2,0),(0.348464,1.963375,0),(0.342726,1.927151,0),(0.333234,1.891726,0),(0.32009,1.857487,0),(0.303441,1.824809,0),(0.283465,1.79405,0),(0.260385,1.765548,0),(0.234452,1.739615,0),(0.20595,1.716535,0),(0.175191,1.696559,0),(0.142513,1.67991,0),(0.108274,1.666766,0),(0.0728487,1.657274,0),(0.0366249,1.651536,0),(0,1.649617,0)],
              'circle'      : [(0,0,1.277012),(0,0,1.004121),(0.31029,0,0.954976),(0.590207,0,0.812351),(0.812351,0,0.590207),(0.954976,0,0.31029),(1.004121,0,0),(1.277012,0,0),(1.004121,0,0),(0.954976,0,-0.31029),(0.812351,0,-0.590207),(0.590207,0,-0.812351),(0.31029,0,-0.954976),(0,0,-1.004121),(0,0,-1.277012),(0,0,-1.004121),(-0.31029,0,-0.954976),(-0.590207,0,-0.812351),(-0.812351,0,-0.590207),(-0.954976,0,-0.31029),(-1.004121,0,0),(-1.277012,0,0),(-1.004121,0,0),(-0.954976,0,0.31029),(-0.812351,0,0.590207),(-0.590207,0,0.812351),(-0.31029,0,0.954976),(0,0,1.004121)],
              'arrowBall'   : [(-0.101079,1.768103,0.104009),(-0.101079,1.724487,0.527368),(-0.101079,1.651794,0.791052),(-0.354509,1.651794,0.791052),(0,1.513677,1.146509),(0.354509,1.651794,0.791052),(0.101079,1.651794,0.791052),(0.101079,1.724487,0.527368),(0.101079,1.768103,0.104009),(0.527367,1.724487,0.104009),(0.791052,1.651794,0.104009),(0.791052,1.651794,0.354509),(1.146509,1.513677,0),(0.791052,1.651794,-0.354508),(0.791052,1.651794,-0.104008),(0.527367,1.724487,-0.104008),(0.101079,1.768103,-0.104008),(0.101079,1.724487,-0.527367),(0.101079,1.651794,-0.791051),(0.354509,1.651794,-0.791051),(0,1.513677,-1.146509),(-0.354509,1.651794,-0.791051),(-0.101079,1.651794,-0.791051),(-0.101079,1.724487,-0.527367),(-0.101079,1.768103,-0.104008),(-0.527367,1.724487,-0.104008),(-0.791052,1.651794,-0.104008),(-0.791052,1.651794,-0.354508),(-1.146509,1.513677,0),(-0.791052,1.651794,0.354509),(-0.791052,1.651794,0.104009),(-0.527367,1.724487,0.104009),(-0.101079,1.768103,0.104009)],
              'arrowCircle' : [(1.37739e-08,0,3.659463),(-1.045561,0,2.613902),(-0.52278,0,2.613902),(-0.47005,0,2.363794),(-0.741641,0,2.282536),(-1.410685,0,1.941641),(-1.941641,0,1.410685),(-2.282536,0,0.741641),(-2.363792,0,0.470041),(-2.613902,0,0.52278),(-2.613902,0,1.045561),(-3.659463,0,0),(-2.613902,0,-1.045561),(-2.613902,0,-0.52278),(-2.363785,0,-0.470058),(-2.282536,0,-0.741641),(-1.941641,0,-1.410685),(-1.410685,0,-1.941642),(-0.741641,0,-2.282537),(-0.470039,0,-2.363882),(-0.52278,0,-2.613902),(-1.045561,0,-2.613902),(1.37739e-08,0,-3.659463),(1.045561,0,-2.613902),(0.52278,0,-2.613902),(0.470039,0,-2.363882),(0.741641,0,-2.282537),(1.410686,0,-1.941642),(1.941642,0,-1.410686),(2.282537,0,-0.741641),(2.363785,0,-0.470058),(2.613902,0,-0.52278),(2.613902,0,-1.045561),(3.659463,0,0),(2.613902,0,1.045561),(2.613902,0,0.52278),(2.363792,0,0.470041),(2.282536,0,0.741641),(1.941641,0,1.410685),(1.410685,0,1.941641),(0.741641,0,2.282536),(0.47005,0,2.363796),(0.52278,0,2.613902),(1.045561,0,2.613902),(1.37739e-08,0,3.659463)],
              'pyramid'     : [(-0.999999,0.0754167,-0.999999),(-0.999999,0.0754167,0.999999),(0.999999,0.0754167,0.999999),(0.999999,0.0754167,-0.999999),(-0.999999,0.0754167,-0.999999),(-0.999999,-0.0695844,-0.999999),(-0.112596,-1,-0.112596),(-0.112596,-1,0.112596),(0.112596,-1,0.112596),(0.999999,-0.0695844,0.999999),(0.999999,0.0754167,0.999999),(0.999999,-0.0695844,0.999999),(-0.999999,-0.0695844,0.999999),(-0.999999,0.0754167,0.999999),(-0.999999,-0.0695844,0.999999),(-0.112596,-1,0.112596),(-0.999999,-0.0695844,0.999999),(-0.999999,-0.0695844,-0.999999),(0.999999,-0.0695844,-0.999999),(0.999999,0.0754167,-0.999999),(0.999999,-0.0695844,-0.999999),(0.112596,-1,-0.112596),(-0.112596,-1,-0.112596),(0.112596,-1,-0.112596),(0.112596,-1,0.112596),(0.112596,-1,-0.112596),(0.999999,-0.0695844,-0.999999),(0.999999,-0.0695844,0.999999)],
              'capsule'     : [(-2.011489,0,0),(-1.977023,0.261792,0),(-1.875975,0.505744,0),(-1.71523,0.71523,0),(-1.505744,0.875975,0),(-1.261792,0.977023,0),(-1,0.999999,0),(-0.5,0.999999,0),(0,1.000001,0),(0.5,1.000001,0),(1,1.000001,0),(1.261792,0.977023,0),(1.505744,0.875975,0),(1.71523,0.71523,0),(1.875975,0.505744,0),(1.977023,0.261792,0),(2.011489,0,0),(1.977023,-0.261792,0),(1.875975,-0.505744,0),(1.71523,-0.71523,0),(1.505744,-0.875975,0),(1.261792,-0.977023,0),(1,-1,0),(0.5,-1,0),(0,-1,0),(-0.5,-1,0),(-1,-1,0),(-1.261792,-0.977023,0),(-1.505744,-0.875975,0),(-1.71523,-0.71523,0),(-1.875975,-0.505744,0),(-1.977023,-0.261792,0),(-2.011489,0,0)],
              'arrowCross'  : [(-3.629392,0,-2.087399),(-3.629392,0,-1.723768),(-1.723768,0,-1.723768),(-1.723768,0,-3.629392),(-2.087399,0,-3.629392),(0,0,-5.704041),(2.087399,0,-3.629392),(1.723768,0,-3.629392),(1.723768,0,-1.723768),(3.629392,0,-1.723768),(3.629392,0,-2.087399),(5.704041,0,0),(3.629392,0,2.087399),(3.629392,0,1.723768),(1.723768,0,1.723768),(1.723768,0,3.629392),(2.087399,0,3.629392),(0,0,5.704041),(-2.087399,0,3.629392),(-1.723768,0,3.629392),(-1.723768,0,1.723768),(-3.629392,0,1.723768),(-3.629392,0,2.087399),(-5.704041,0,0),(-3.629392,0,-2.087399)],
              'triangle'    : [(-1,0,1),(-1,0,1),(-0.9,0,0.8),(-0.8,0,0.6),(-0.7,0,0.4),(-0.6,0,0.2),(-0.5,0,0),(-0.4,0,-0.2),(-0.3,0,-0.4),(-0.2,0,-0.6),(-0.1,0,-0.8),(0,0,-1),(0.1,0,-0.8),(0.2,0,-0.6),(0.3,0,-0.4),(0.4,0,-0.2),(0.5,0,0),(0.6,0,0.2),(0.7,0,0.4),(0.8,0,0.6),(0.9,0,0.8),(1,0,1),(0.8,0,1),(0.6,0,1),(0.4,0,1),(0.2,0,1),(0,0,1),(-0.2,0,1),(-0.4,0,1),(-0.6,0,1),(-0.8,0,1),(-1,0,1)],
              'drop'        : [(0,0,-2.28198),(0.585544,0,-1.569395),(1.08325,0,-1.071748),(1.413628,0,-0.588119) ,(1.531946,0,0.00057226),(1.413628,0,0.585419),(1.08325,0,1.083278),(0.585544,0,1.413621) ,(0,0,1.531949),(-0.585544,0,1.413621),(-1.08325,0,1.083277),(-1.413628,0,0.585419) ,(-1.531946,0,0.000554983),(-1.413628,0,-0.588078),(-1.08325,0,-1.071626),(-0.585544,0,-1.570833),(0,0,-2.28198)],
              'plus'        : [(-0.353457,0,-0.354546),(-0.353457,0,-2),(0.35461,0,-2),(0.35461,0,-0.354546),(2,0,-0.354546),(2,0,0.35233),(0.354602,0,0.35233),(0.354602,0,2.000578),(-0.353457,0,2.002733),(-0.353457,0,0.35233),(-2,0,0.35233),(-2,0,-0.354546),(-0.353457,0,-0.354546)],
              'daimond'     : [(0,1,0),(0,0,0.625),(0,-1,0),(0.625,0,0),(0,1,0),(0,0,-0.625),(0,-1,0),(-0.625,0,0),(0,1,0),(0.625,0,0),(0,0,-0.625),(-0.625,0,0),(0,0,0.625),(0.625,0,0)],
              'square'      : [(0,0,-1.12558),(0,0,-1),(-1,0,-1),(-1,0,0),(-1.12558,0,0),(-1,0,0),(-1,0,1),(0,0,1),(0,0,1.12558),(0,0,1),(1,0,1),(1,0,0),(1.12558,0,0),(1,0,0),(1,0,-1),(0,0,-1)],
              'cube'        : [(1,-1,1),(1,1,1),(1,1,-1),(1,-1,-1),(-1,-1,-1),(-1,1,-1),(-1,1,1),(-1,-1,1),(1,-1,1),(1,-1,-1),(-1,-1,-1),(-1,-1,1),(-1,1,1),(1,1,1),(1,1,-1),(-1,1,-1)],
              'arrowPoint'  : [(0,0,0),(1.34615e-08,0,3.273813),(4.03845e-08,0.307963,3.503176),(0,0,4.37423),(0.307963,0,3.503176),(1.34615e-08,0,3.273813),(-0.307963,2.6923e-08,3.503176),(0,0,4.37423),(-1.34615e-08,-0.307963,3.503176),(1.34615e-08,0,3.273813),(0.307963,0,3.503176),(4.03845e-08,0.307963,3.503176),(-0.307963,2.6923e-08,3.503176),(-1.34615e-08,-0.307963,3.503176),(0.307963,0,3.503176)],
              'star'        : [(-0.70686,0,0.988366),(5.96046e-08,0,-0.995175),(0.70686,0,0.988366),(-0.999885,0,-0.376983),(0.999885,0,-0.376983),(-0.70686,0,0.988366)],
              'locatorBold' : [(0,0,2,),(-0.353457,0,2.002733,),(-0.353457,0,0.35233,),(-2,0,0.35233,),(-2,0,-0.354546,),(-0.353457,0,-0.354546,),(-0.353457,0,-2,),(0.35461,0,-2,),(0.35461,0,-0.354546,),(2,0,-0.354546,),(2,0,0.35233,),(0.354602,0,0.35233,),(0.354602,0,2.000578,),(0,0,2,),(0,0.354602,2.000578,),(0,0.354602,0.35233,),(0,2,0.35233,),(0,2,-0.354546,),(0,0.35461,-0.354546,),(0,0.35461,-2,),(0,-0.353457,-2,),(0,-0.353457,-0.354546,),(0,-2,-0.354546,),(0,-2,0.35233,),(0,-0.353457,0.35233,),(0,-0.353457,2.002733,),(0,0.354602,2.000578,),(0,0.354602,0.35233,),(0,2,0.35233,),(0,2,0,),(0.35233,2,0,),(0.35233,0.354602,0,),(2.000578,0.354602,0,),(2.002733,-0.353457,0,),(0.35233,-0.353457,0,),(0.35233,-2,0,),(-0.354546,-2,0,),(-0.354546,-0.353457,0,),(-2,-0.353457,0,),(-2,0.35461,0,),(-0.354546,0.35461,0,),(-0.354546,2,0,),(0,2,0)],
              'arrow'       : [(-1,0,0),(0,0,-1),(1,0,0),(0.4,0,0),(0.4,0,1),(-0.4,0,1),(-0.4,0,0),(-1,0,0)],
              'locator'     : [(0,1,0),(0,-1,0),(0,0,0),(-1,0,0),(1,0,0),(0,0,0),(0,0,-1),(0,0,1)],
              'direction'   : [(-4,0,-5),(4,0,-5),(4,0,3),(0,0,6),(-4,0,3),(-4,0,-5)],
              'null'        : [(0,0,0),(0,0,0),(0,0,0)],
              'line'        : [(0.3,0,0),(-0.3,0,0)]}
              
    if shape in param.keys():
        return param[shape]

def create(*args, **kwargs):
    '''
    '''
    node = mc.createNode(*args, **kwargs)

    if is_transform(node):
        return register_node(node)
    else:
        return core.Node(node)

def text_curves(text):
    '''
    '''
    transform = create('transform')
    texts = mc.textCurves(f = 'MS Shell Dlg 2, 27.8pt', t = text, ch = False)
    texts_shape = mc.listRelatives(texts, ad = True, type = 'nurbsCurve')

    for i, cuvshp in enumerate(texts_shape):
        cuvshp = register_node(cuvshp)
        cuvtrnf = cuvshp.get_parent()
        cuvtrnf.set_parent()
        cuvtrnf.freeze()
        cuvshp.set_parent(transform)
        cuvshp.name = '{}_Shape{}'.format(text, i+1)
        mc.delete(cuvtrnf)
        i+=1

    mc.xform(transform, cp = True)
    cpx = transform.attr('c').value[0]
    transform.attr('tx').value = -cpx
    transform.freeze()
    mc.delete(texts)
    mc.select(cl = True)
    
    return transform

def set_side(side = ''):
    '''
    '''
    if side:
        return '_{}_'.format(side.replace('_', ''))
    else:
        return '_'

def controller(name = '', shape = '', color = '', jnt = False):
    '''
    '''
    node = 'transform'
    if jnt:
        node = 'joint'

    transform = create(node, n = 'Control')
    cuvshape = create('nurbsCurve', n = '{}Shape'.format(transform), p = transform)

    if not shape:
        values = ['{}.cc'.format(cuvshape), 3, 12, 2, False, 3,
                  [i for i in range(-2,15)], 17, 15]
        values += curve_param('defualt')
    else:
        values = ['{}.cc'.format(cuvshape), 1, len(curve_param(shape))-1, 0, False, 3, 
                  [ix for ix in range(len(curve_param(shape)))], 
                  len(curve_param(shape)), len(curve_param(shape))]
        values += curve_param(shape)

    mc.setAttr(*values, type = 'nurbsCurve')
    
    if name:
        transform.name = name

    if color:
        transform.color = color
    
    if jnt:
        transform.lock_hide('radi')
        transform.attr('drawStyle').value = 2
        
    transform.lock_hide('visibility')
    mc.select(cl = True)
    return transform

def gimbal(controller):
    '''
    '''
    ctrl = register_node(controller)
    
    transform = node.Transform('Gimbal')
    cuvdata = get_curve_data(controller)
    build_curve_from_data(cuvdata, transform)
    
    transform.name = '{}Gmbl{}'.format(ctrl.prefix, ctrl.suffix)
    transform.snap(controller)
    transform.color = 'white'
    transform.scale_shape(0.8)
    transform.lock_hide('s', 'v')

    if not ctrl.shape.attr('gimbalControl').exists:
        ctrl.shape.add_attr('gimbalControl', min = 0, max = 1)
    
    ctrl.shape.attr('gimbalControl') >> transform.shape.attr('v')
    ctrl.attr('ro') >> transform.attr('rotateOrder')

    mc.parent(transform, controller)
    mc.select(cl = True)
    return transform

def get_gimbal(controller):
    ctrl = register_node(controller)
    array = ctrl.name.split('_')
    array[0] = '{}Gmbl'.format(array[0])
    gmbl = '_'.join(array)
    
    if mc.objExists(gmbl):
        return register_node(gmbl)
    return None

def group(obj, part = ''):
    '''
    '''
    obj = register_node(obj)
    objparent = obj.get_parent()
    name = '{}{}{}{}Grp'.format(obj.prefix, obj.type, part, obj.side)
    transform = node.Transform(name)
    transform.snap_matrix(obj)
    mc.parent(obj, transform)

    if objparent:
        mc.parent(transform, objparent)

    return transform

def joint(name = 'Joint', **kwargs):
    '''
    '''
    jnt = create('joint', n = name)
    if 'position' in kwargs:
        jnt.snap_matrix(kwargs['position'])
        jnt.freeze()

    return jnt

def reset_joint_orient(joint = ''):
    mc.setAttr('{}.r'.format(joint), (0,0,0))
    mc.setAttr('{}.jo'.format(joint), (0,0,0))

def add_ikhandle(name, solve, start_joint, end_joint):
    '''
    '''
    stjnt = register_node(start_joint)
    side = stjnt.side

    ikh = mc.ikHandle( name = '{}{}Ikh'.format(name, side),
                       sol = solve,
                       sj = start_joint,
                       ee = end_joint,
                       ns = 1 )
    
    ikhlist = [register_node(k) for k in ikh]
    ikhlist[0].attr('v').value = 0
    ikhlist[1].name = '{}{}Eff'.format(name, side)

    if solve == 'ikSplineSolver':
        ikhlist[2].name = '{}{}Cuv'.format(name, side)

    mc.select(cl = True)
    return ikhlist

def copy_curve_shape(source, target, world = True):
    '''
    '''
    src = register_node(source)
    trg = register_node(target)
    srcdata = get_curve_data(source)
    trgdata = get_curve_data(target)

    match = True
    for key in srcdata.keys():
        if not srcdata[key] == trgdata[key]:
            match = False
        break
    
    if not match:
        mc.rebuildCurve( trg.shape,
                         s = srcdata['spans'],
                         d = srcdata['degree'],
                         kr = False,
                         ch = False )
    
    for ix in range(srcdata['spans']+1):
        pos = mc.xform('{}.cv[{}]'.format(src.shape, str(ix)), q = True, t = True, ws = world)
        mc.xform('{}.cv[{}]'.format(trg.shape, str(ix)), t = pos, ws = world)

def mirror_curve_shape(source, search = '', replace = '', world = True):
    '''
    '''
    src = register_node(source)
    srcdata = get_curve_data(source)

    if search in src.name:
        trgname = src.name.replace(search, replace)

        if mc.objExists(trgname):
            trg = register_node(trgname)
            for ix in range(srcdata['spans']+1):
                pos = mc.xform('{}.cv[{}]'.format(src.shape, str(ix)), q = True, t = True, ws = world)
                mc.xform('{}.cv[{}]'.format(trg.shape, str(ix)), t = (-pos[0], pos[1], pos[2]), ws = world)

def scale_gimbal_all(size = 0.9):
    gmblall = mc.ls('*Gmbl*_Ctrl')
    for gmbl in gmblall:
        ctrl = gmbl.replace('Gmbl','')
        if mc.objExists(ctrl):
            copy_curve_shape(ctrl, gmbl, world = False)
            register_node(gmbl).scale_shape(size)

def translate_rotate_blend(controller_attr, a, b, c):
    '''
    '''
    blend = node.PairBlend()
    blend.attr('rotInterpolation').value = 0

    controller_attr >> blend.attr('weight')
    a.attr('t') >> blend.attr('inTranslate1')
    a.attr('r') >> blend.attr('inRotate1')
    b.attr('t') >> blend.attr('inTranslate2')
    b.attr('r') >> blend.attr('inRotate2')

    blend.attr('outTranslate') >> c.attr('t')
    blend.attr('outRotate') >> c.attr('r')
    
    return blend

def scale_blend(controller_attr, a, b, c):
    '''
    '''
    blend = node.BlendColors()
    controller_attr >> blend.attr('blender')
    a.attr('s') >> blend.attr('color1')
    b.attr('s') >> blend.attr('color2')
    blend.attr('output') >> c.attr('s')

    return blend

def local_world(controller, world_position, local_position, cons_position, type):
    '''
    '''
    ctrl = register_node(controller)
    prefix = ctrl.prefix
    side = ctrl.side
    _attr = 'localWorld'
    ctrl.add_attr(_attr, min = 0, max = 1)

    rev = node.Reverse('{}LocWor{}Rev'.format(prefix, side))
    space_grp = node.Transform('{}Space{}Grp'.format(prefix, side))
    world_grp = node.Transform('{}WorldSpace{}Grp'.format(prefix, side))
    local_grp = node.Transform('{}LocalSpace{}Grp'.format(prefix, side))

    for __grp in (space_grp, world_grp, local_grp):
        __grp.snap_matrix(local_position)
    
    if type == 'orient':
        cons_node = orient_constraint(local_grp, world_grp, cons_position, mo = True)
        if world_position:
            world_cons = orient_constraint(world_position, world_grp, mo = True)

    elif type == 'parent':
        cons_node = parent_constraint(local_grp, world_grp, cons_position, mo = True)
        if world_position:
            world_cons = parent_constraint(world_position, world_grp, mo = True)

    ctrl.attr(_attr) >> rev.attr('ix')
    ctrl.attr(_attr) >> cons_node.attr('{}W1'.format(world_grp))
    rev.attr('ox') >> cons_node.attr('{}W0'.format(local_grp))

    mc.parent(world_grp, local_grp, space_grp)
    mc.parent(space_grp, local_position)
    mc.select(cl = True)

    return ctrl, space_grp, world_grp, local_grp, cons_position, cons_node, world_cons, rev

def convert_local_world_to_specific_spaces(object_list, spaces_list):
    '''
    '''
    ctrl, space_grp, world_grp, local_grp, cons_position, cons_node, world_cons, rev = [register_node(obj) for obj in object_list]

    prefix = ctrl.prefix
    side = ctrl.side

    mc.delete(cons_node, rev)

    attr_list = list()
    attr_list.append(('world', world_grp))

    for space_name, space_position in spaces_list:
        grp = node.Transform('{}{}Space{}Grp'.format(prefix, space_name, side))
        parent_constraint(space_position, grp, mo = False)
        mc.parent(space_grp, grp)

        attr_list.append((space_name, grp))
    
    space_attr = 'space'
    ctrl.add_attr(space_attr, at = 'enum', en = '...', k = True)

    enum_attr = str()
    for ix, attr in enumerate(attr_list):
        enum_attr += '{}:'.format(attr[0])
        ctrl.add_attr(space_attr, e = True, en = enum_attr)

        parscons = parent_constraint(attr[1], cons_position, mo = True)
        space_cond = node.Condition('{}{}Space{}Cond'.format(prefix, attr[0], side))

        ctrl.attr(space_attr) >> space_cond.attr('st')
        space_cond.attr('ocr') >> parscons.attr('{}W{}'.format(attr[1], ix))

        space_cond.attr('ft').value = ix
        space_cond.attr('ctr').value = 1
        space_cond.attr('cfr').value = 0

    if ctrl.attr('localWorld').exists:
        mc.deleteAttr(ctrl, at = 'localWorld')
    
    mc.select(cl = True)

def add_non_roll_joint(target, twist_axis):
    '''
    '''
    trg = register_node(target)
    name = trg.prefix
    side = trg.side
    pars = trg.get_parent()

    jnt = joint('{}Nr{}Jnt'.format(name, side))
    jnt.rotate_order = trg.rotate_order
    jnt.snap_matrix(trg)
    jnt.add_attr('twist')
    mc.parent(jnt, pars)

    pntcons = point_constraint(trg, jnt, mo = True)
    
    etq = node.EulerToQuat('{}Nr{}Etq'.format(name, side))
    qtetw = node.QuatToEuler('{}Twist{}Qte'.format(name, side))
    qtenr = node.QuatToEuler('{}Nr{}Qte'.format(name, side))
    quatinv = node.QuatInvert('{}Nr{}Qinv'.format(name, side))
    quatprod = node.QuatProd('{}Nr{}Qprd'.format(name, side))

    trg.attr('r') >> etq.attr('inputRotate')
    trg.attr('ro') >> etq.attr('inputRotateOrder')

    inquat = 'inputQuat{}'.format(twist_axis.upper())
    outquat = 'outputQuat{}'.format(twist_axis.upper())

    etq.attr(outquat) >> qtetw.attr(inquat)
    etq.attr('outputQuatW') >> qtetw.attr('inputQuatW')

    etq.attr(outquat) >> quatinv.attr(inquat)
    etq.attr('outputQuatW') >> quatinv.attr('inputQuatW')
    quatinv.attr('outputQuat') >> quatprod.attr('input1Quat')
    etq.attr('outputQuat') >> quatprod.attr('input2Quat')
    quatprod.attr('outputQuat') >> qtenr.attr('inputQuat')

    qtenr.attr('outputRotate') >> jnt.attr('r')
    jnt.attr('ro') >> qtenr.attr('inputRotateOrder')

    outrot = 'outputRotate{}'.format(twist_axis.upper())
    qtetw.attr(outrot) >> jnt.attr('twist')
    jnt.attr('ro') >> qtetw.attr('inputRotateOrder')

    jnt.lock_hide('twist')

    return jnt, pntcons, etq, qtetw, qtenr, quatinv, quatprod

def swing_twist_nodes(name = '', side = '', axis = ''):
    '''
    '''
    etq = node.EulerToQuat('{}Swing{}Etq'.format(name, side))
    qtetw = node.QuatToEuler('{}Twist{}Qte'.format(name, side))
    qtesw = node.QuatToEuler('{}Swing{}Qte'.format(name, side))
    quatinv = node.QuatInvert('{}Swing{}Qinv'.format(name, side))
    quatprod = node.QuatProd('{}Swing{}Qprd'.format(name, side))

    inquat = 'inputQuat{}'.format(axis.upper())
    outquat = 'outputQuat{}'.format(axis.upper())

    etq.attr(outquat) >> qtetw.attr(inquat)
    etq.attr('outputQuatW') >> qtetw.attr('inputQuatW')

    etq.attr(outquat) >> quatinv.attr(inquat)
    etq.attr('outputQuatW') >> quatinv.attr('inputQuatW')
    quatinv.attr('outputQuat') >> quatprod.attr('input1Quat')
    etq.attr('outputQuat') >> quatprod.attr('input2Quat')
    quatprod.attr('outputQuat') >> qtesw.attr('inputQuat')

    return etq, qtetw, qtesw, quatinv, quatprod

def extract_swing_twist(target, twist_axis):
    '''
    '''
    trg = register_node(target)
    trg.add_attr('twist')
    trg.add_vector_attr('swing')

    etq, qtetw, qtesw, quatinv, quatprod = swing_twist_nodes(twist_axis)

    trg.attr('r') >> etq.attr('inputRotate')
    trg.attr('ro') >> etq.attr('inputRotateOrder')
    trg.attr('ro') >> qtetw.attr('inputRotateOrder')
    trg.attr('ro') >> qtesw.attr('inputRotateOrder')

    outrot = 'outputRotate{}'.format(twist_axis.upper())
    qtetw.attr(outrot) >> trg.attr('twist')

    qtesw.attr('outputRotate') >> trg.attr('swing')

    return etq, qtetw, qtesw, quatinv, quatprod

def add_offset_controller(controller, target, attr, ax, val):
    '''
    '''
    ctrl = register_node(controller)
    trg = register_node(target)

    mdl = node.MultDoubleLinear('{}{}{}Mdl'.format(ctrl.prefix, attr.capitalize(), ctrl.side))
    adl = node.AddDoubleLinear('{}{}{}Adl'.format(ctrl.prefix, attr.capitalize(), ctrl.side))

    ctrl.add_attr(attr)
    amp = '{}Amp'.format(attr)
    ctrl.shape.add_attr(amp)
    adl.add_attr('default')
    
    ctrl.shape.attr(amp).value = val
    ctrl.shape.attr(amp) >> mdl.attr('i1')
    ctrl.attr(attr) >> mdl.attr('i2')

    dv = trg.attr('t{}'.format(ax)).value
    adl.attr('default').value = dv
    adl.attr('default') >> adl.attr('i1')
    mdl.attr('o') >> adl.attr('i2')
    adl.attr('o') >> trg.attr('t{}'.format(ax))

    return mdl, adl

def add_squash_controller(controller, joint, ax): 
    '''
    '''
    ctrl = register_node(controller)
    jnt = register_node(joint)

    ctrl.add_attr('squash')

    allmdl = list()
    alladl = list()

    for x in ax:
        mdl = node.MultDoubleLinear('{}S{}{}Mdl'.format(ctrl.prefix, x, ctrl.side))
        adl = node.AddDoubleLinear('{}S{}{}Adl'.format(ctrl.prefix, x, ctrl.side))
        
        allmdl.append(mdl)
        alladl.append(adl)

        adl.add_attr('default', dv = 1)
        mdl.attr('i1').value = 0.5

        adl.attr('default') >> adl.attr('i1')
        ctrl.attr('squash') >> mdl.attr('i2')
        mdl.attr('o') >> adl.attr('i2')
        adl.attr('o') >> jnt.attr('s{}'.format(x))
    
    return allmdl, alladl

def add_stretchy_ik_chain(controller, joint, part, controller_pin = ''):
    '''
    '''
    ctrl = register_node(controller)
    gmbl = ctrl.get_child()
    jnts = [register_node(j) for j in joint]
    side = ctrl.side

    val = 1
    if 'R' in side:
        val = -1

    prefixlist = list()
    distlist = list()
    distsum = 0
    jntcount = list(range(len(jnts)))

    for i in jntcount:
        if not i == jntcount[0]:
            distance = distance_between(get_position(jnts[i-1]), 
                                        get_position(jnts[i]))
            distlist.append(distance)
            distsum += distance
        
        if not i == jntcount[-1]:
            prefixlist.append(jnts[i].name.split('Ik')[0])
        
    if controller_pin:
        ctrlpin = register_node(controller_pin)
        _namepin = ctrlpin.name.split('Ik')[0]
        ctrl.add_attr('{}Slide'.format(_namepin))

    ctrl.add_attr('softness', min = 0, max = 1, dv = 0)
    ctrl.add_divide_attr('stretch')
    ctrl.add_attr('autoStretch', min = 0, max = 1, dv = 1)

    for prefix in prefixlist:
        ctrl.add_attr('{}Stretch'.format(prefix))

    ctrl.shape.add_attr('defaultLen')
    for ix, pref in enumerate(prefixlist):
        _default_attr = 'defaultLen{}'.format(pref)
        ctrl.shape.add_attr(_default_attr)
        ctrl.shape.attr(_default_attr).value = distlist[ix]*val
        ctrl.shape.attr(_default_attr).lock = True
        ctrl.shape.attr(_default_attr).hide = True

    ctrl.shape.add_attr('stretchLen')
    for pref in prefixlist:
        _stretch_attr = 'stretchLen{}'.format(pref)
        ctrl.shape.add_attr(_stretch_attr)
        ctrl.shape.attr(_stretch_attr).hide = True

    ik_dist_grp = node.Transform('{}IkDist{}Grp'.format(part, side))
    ik_dist_start_grp = node.Transform('{}IkDistSt{}Grp'.format(part, side))
    ik_dist_end_grp = node.Transform('{}IkDistEn{}Grp'.format(part, side))
    mc.parent(ik_dist_start_grp, ik_dist_end_grp, ik_dist_grp)

    point_constraint(jnts[0], ik_dist_start_grp, mo = False)
    point_constraint(gmbl, ik_dist_end_grp, mo = False)

    def_sum_len_pma = node.PlusMinusAverage('{}IkDefSumLen{}Pma'.format(part,side))
    strt_sum_len_pma = node.PlusMinusAverage('{}IkStrtSumLen{}Pma'.format(part,side))
    strt_mul_mdv = node.MultiplyDivide('{}IkStrtMul{}Mdv'.format(part,side))
    strt_pow_mdv = node.MultiplyDivide('{}IkStrtPow{}Mdv'.format(part,side))
    strt_sqrt_mdv = node.MultiplyDivide('{}IkStrtSqrt{}Mdv'.format(part,side))
    strt_sum_pma = node.PlusMinusAverage('{}IkStrtSum{}Pma'.format(part,side))

    for pref, vec in zip(prefixlist, 'xyz'):
        _main_attr = '{}Stretch'.format(pref)
        _default_attr = 'defaultLen{}'.format(pref)
        _stretch_attr = 'stretchLen{}'.format(pref)

        ctrl.attr(_main_attr) >> strt_mul_mdv.attr('i1{}'.format(vec))
        ctrl.shape.attr(_default_attr) >> def_sum_len_pma.attr('i1').last()
        strt_mul_mdv.attr('o{}'.format(vec)) >> strt_sum_pma.attr('i3[0].i3{}'.format(vec))
        ctrl.shape.attr(_default_attr) >> strt_sum_pma.attr('i3[1].i3{}'.format(vec))
        strt_sqrt_mdv.attr('o{}'.format(vec)) >> ctrl.shape.attr(_stretch_attr)
        ctrl.shape.attr(_stretch_attr) >> strt_sum_len_pma.attr('i1').last()
    
    strt_sum_pma.attr('o3') >> strt_pow_mdv.attr('i1')
    strt_pow_mdv.attr('o') >> strt_sqrt_mdv.attr('i1')
    def_sum_len_pma.attr('o1') >> ctrl.shape.attr('defaultLen')
    strt_sum_len_pma.attr('o1') >> ctrl.shape.attr('stretchLen')

    strt_pow_mdv.attr('op').value = 3
    strt_sqrt_mdv.attr('op').value = 3
    
    strt_pow_mdv.attr('i2').value = (2, 2, 2)
    strt_sqrt_mdv.attr('i2').value = (0.5, 0.5, 0.5)
    strt_mul_mdv.attr('i2').value = (val, val, val)

    dist = node.DistanceBetween('{}IkAutoStrt{}Dist'.format(part, side))
    auto_strt_cond = node.Condition('{}IkAutoStrt{}Cnd'.format(part, side))
    zero_cond = node.Condition('{}IkZero{}Cnd'.format(part, side))
    neg_cond = node.Condition('{}IkNeg{}Cnd'.format(part, side))
    div_mdv = node.MultiplyDivide('{}IkDiv{}Mdv'.format(part, side))
    powe_mdv = node.MultiplyDivide('{}IkPowE{}Mdv'.format(part, side))
    auto_mul_len_mdv = node.MultiplyDivide('{}IkAutoStrtMulLen{}Mdv'.format(part, side))
    auto_strt_div_orig_mdv = node.MultiplyDivide('{}IkAutoStrtDivOrig{}Mdv'.format(part, side))
    sub_dist_pma = node.PlusMinusAverage('{}IkSubDist{}Pma'.format(part, side))
    sub_len_pma = node.PlusMinusAverage('{}IkSubLen{}Pma'.format(part, side))
    sum_len_pma = node.PlusMinusAverage('{}IkSumLen{}Pma'.format(part, side))
    inv_mdl = node.MultDoubleLinear('{}IkInv{}Mdl'.format(part, side))
    mult_mdl = node.MultDoubleLinear('{}IkMult{}Mdl'.format(part, side))
    limit_cmp = node.Clamp('{}IkLimit{}Cmp'.format(part, side))
    auto_bta = node.BlendTwoAttr('{}IkAutoStrt{}Bta'.format(part, side))
    soft_len_bta = node.BlendTwoAttr('{}IkSoftLen{}Bta'.format(part, side))
    soft_rev = node.Reverse('{}IkSoft{}Rev'.format(part, side))
    soft_adl = node.AddDoubleLinear('{}IkSoft{}Adl'.format(part, side))

    ik_dist_start_grp.attr('t') >> dist.attr('point1')
    ik_dist_end_grp.attr('t') >> dist.attr('point2')

    dist.attr('d') >> zero_cond.attr('cfr')
    dist.attr('d') >> auto_strt_cond.attr('ft')
    dist.attr('d') >> auto_strt_div_orig_mdv.attr('i1x')
    dist.attr('d') >> sub_dist_pma.attr('i1[1]')

    ctrl.shape.attr('stretchLen') >> zero_cond.attr('ctr')
    ctrl.shape.attr('stretchLen') >> sub_len_pma.attr('i1[0]')
    
    ctrl.attr('softness') >> zero_cond.attr('ctg')
    ctrl.attr('softness') >> zero_cond.attr('ft')
    ctrl.attr('softness') >> inv_mdl.attr('i1')
    ctrl.attr('softness') >> mult_mdl.attr('i2')
    ctrl.attr('softness') >> soft_rev.attr('ix')
    ctrl.attr('softness') >> sum_len_pma.attr('i2[0].i2y')
    ctrl.attr('softness') >> soft_len_bta.attr('attributesBlender')

    zero_cond.attr('ocr') >> sum_len_pma.attr('i2[1].i2x')
    zero_cond.attr('ocg') >> div_mdv.attr('i2x')

    soft_rev.attr('ox') >> soft_adl.attr('i1')
    soft_len_bta.attr('o') >> soft_adl.attr('i2')
    soft_adl.attr('o') >> sum_len_pma.attr('i2[1].i2y')

    inv_mdl.attr('o') >> sum_len_pma.attr('i2[0].i2x')

    sum_len_pma.attr('o2x') >> sub_dist_pma.attr('i1').last()
    sum_len_pma.attr('o2y') >> limit_cmp.attr('mxr')

    sub_dist_pma.attr('o1') >> div_mdv.attr('i1x')
    
    div_mdv.attr('ox') >> powe_mdv.attr('i2x')
    div_mdv.attr('ox') >> neg_cond.attr('ft')

    powe_mdv.attr('ox') >> mult_mdl.attr('i1')
    mult_mdl.attr('o') >> neg_cond.attr('ctr')
    neg_cond.attr('ocr') >> sub_len_pma.attr('i1[1]')

    sub_len_pma.attr('o1') >> auto_strt_div_orig_mdv.attr('i2x')
    sub_len_pma.attr('o1') >> auto_strt_cond.attr('st')

    auto_strt_div_orig_mdv.attr('ox') >> auto_strt_cond.attr('ctr')

    auto_strt_cond.attr('ocr') >> limit_cmp.attr('ipr')
    auto_strt_cond.attr('ocr') >> auto_bta.attr('input[1]')

    limit_cmp.attr('opr') >> auto_bta.attr('input[0]')

    ctrl.attr('autoStretch') >> auto_bta.attr('ab')

    auto_bta.attr('output') >> auto_mul_len_mdv.attr('i1x')
    auto_bta.attr('output') >> auto_mul_len_mdv.attr('i1y')
    auto_bta.attr('output') >> auto_mul_len_mdv.attr('i1z')

    strt_sum_pma.attr('o3') >> auto_mul_len_mdv.attr('i2')

    zero_cond.attr('op').value = 2
    neg_cond.attr('op').value = 4
    neg_cond.attr('cfr').value = 0
    auto_strt_cond.attr('op').value = 2
    sub_len_pma.attr('op').value = 2
    sub_dist_pma.attr('op').value = 2
    div_mdv.attr('op').value = 2
    powe_mdv.attr('op').value = 3
    powe_mdv.attr('i1x').value = 15
    auto_strt_div_orig_mdv.attr('op').value = 2
    inv_mdl.attr('i2').value = -1
    soft_adl.attr('i2').value = 0.15

    soft_len_bta.add_attr('defualt')
    soft_len_bta.add_attr('softLen', dv = 0.2)
    
    soft_len_bta.attr('defualt') >> soft_len_bta.attr('i[0]')
    soft_len_bta.attr('softLen') >> soft_len_bta.attr('i[1]')

    if controller_pin:
        attrpin = '{}Pin'.format(_namepin)
        ctrlpin.add_attr(attrpin, min = 0, max = 1)

        dist_lock_grp = node.Transform('{}IkDistLock{}Grp'.format(part, side))
        mc.parent(dist_lock_grp, ik_dist_grp)

        dist1 = node.DistanceBetween('{}IkLock1{}Dist'.format(part, side))
        dist2 = node.DistanceBetween('{}IkLock2{}Dist'.format(part, side))
        lock_div_len_mdv = node.MultiplyDivide('{}IkLockDivLen{}Mdv'.format(part, side))
        lock_mult_len_mdv = node.MultiplyDivide('{}IkLockMultLen{}Mdv'.format(part, side))
        lock_inv_len_mdv = node.MultiplyDivide('{}IkLockInvLen{}Mdv'.format(part, side))
        lock_bcl = node.BlendColors('{}IkLock{}Bcl'.format(part, side))

        lock_div_len_mdv.attr('op').value = 2
        lock_inv_len_mdv.attr('i2x').value = val
        lock_inv_len_mdv.attr('i2y').value = val

        point_constraint(controller_pin, dist_lock_grp, mo = False)

        ik_dist_start_grp.attr('t') >> dist1.attr('point1')
        ik_dist_end_grp.attr('t') >> dist2.attr('point1')
        dist_lock_grp.attr('t') >> dist1.attr('point2')
        dist_lock_grp.attr('t') >> dist2.attr('point2')
        dist1.attr('d') >> lock_div_len_mdv.attr('i1x')
        dist1.attr('d') >> lock_div_len_mdv.attr('i1y')
        controller_pin.attr(attrpin) >> lock_bcl.attr('b')
        lock_div_len_mdv.attr('ox') >> lock_mult_len_mdv.attr('i1x')
        lock_div_len_mdv.attr('oy') >> lock_mult_len_mdv.attr('i1y')
        lock_mult_len_mdv.attr('ox') >> lock_inv_len_mdv.attr('i1x')
        lock_mult_len_mdv.attr('oy') >> lock_inv_len_mdv.attr('i1y')
        lock_inv_len_mdv.attr('ox') >> lock_bcl.attr('c1r')
        lock_inv_len_mdv.attr('oy') >> lock_bcl.attr('c1g')
        auto_mul_len_mdv.attr('ox') >> lock_bcl.attr('c2r')
        auto_mul_len_mdv.attr('oy') >> lock_bcl.attr('c2g')

        lock_bcl.attr('opr') >> jnts[1].attr('ty')
        lock_bcl.attr('opg') >> jnts[2].attr('ty')

        slide_value = 0.1
        for pref, vec in zip(prefixlist, 'xyz'):
            _main_attr = '{}Stretch'.format(pref)
            _default_attr = 'defaultLen{}'.format(pref)

            ctrl.shape.attr(_default_attr) >> lock_div_len_mdv.attr('i2{}'.format(vec))
            ctrl.shape.attr(_default_attr) >> lock_mult_len_mdv.attr('i2{}'.format(vec))

            slide_mdl = node.MultDoubleLinear('{}IkSlide{}Mdl'.format(pref, side))
            slide_adl = node.AddDoubleLinear('{}IkSlide{}Adl'.format(pref, side))

            ctrl.attr('{}Slide'.format(_namepin)) >> slide_mdl.attr('i1')
            ctrl.attr('{}Stretch'.format(pref)) >> slide_adl.attr('i1')

            slide_mdl.attr('o') >> slide_adl.attr('i2')
            slide_adl.attr('o') >> strt_mul_mdv.attr('i1{}'.format(vec))

            slide_mdl.attr('i2').value = slide_value
            slide_value*=-1
        
        dist_lock_grp.lhtrs()
    
    else:
        for jnt, vec in zip(jnts[1:], 'xyz'):
            auto_mul_len_mdv.attr('o{}'.format(vec)) >> jnt.attr('ty')
    
    ik_dist_grp.add_str_tag('autoStretch', auto_mul_len_mdv)
    ik_dist_start_grp.lhtrs()
    ik_dist_end_grp.lhtrs()
    ctrl.shape.lock_hide('defaultLen', 'stretchLen')

    return register_node([ik_dist_grp , ik_dist_start_grp , ik_dist_end_grp , dist])