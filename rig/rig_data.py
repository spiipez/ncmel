# System modules.
from imp import reload
import os, re, pickle, json

# Maya modules.
import maya.mel as mm
import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma

# ncscript modules.
from ncTools.rig import core
from ncTools.rig import node
reload(core)
reload(node)


def importer(file_path = ''):
    '''
    '''
    return mc.file(file_path, i = True, preserveReferences = True) 

def get_data_folder(create_folder = True):
    '''
    '''
    scn_path = os.path.normpath(mc.file(q = True, sn = True))

    if not scn_path == '.':
        tmpAry = scn_path.split('\\')
        tmpAry[-2] = 'data'
        
        data_folder = '\\'.join(tmpAry[0:-1])
        
        if create_folder:
            if not os.path.isdir(data_folder):
                os.mkdir(data_folder)

        return data_folder
    else:
        mc.warning("Can't find folder data. Scence not save!")

def write_weight(geo = '', flPath = ''):
    '''
    '''
    shapes = mc.listRelatives('{}'.format(geo), shapes = True)
    
    if shapes:
        skn = mm.eval('findRelatedSkinCluster "{}"'.format(geo))

        if skn:
            sknMtd = mc.getAttr('{}.skinningMethod'.format(skn))
            infs = mc.skinCluster(skn, q = True, inf = True)
            sknSet = mc.listConnections('{}.message'.format(skn), d = True, s = False)[0]
            mc.skinPercent(skn, geo, pruneWeights = 0.005)

            wDct = {}
            wDct['influences'] = infs
            wDct['name'] = skn
            wDct['set'] = sknSet
            wDct['skinningMethod'] = sknMtd

            num_verts = mc.polyEvaluate(geo, v = True)
            sel_list = om.MSelectionList()
            sel_list.add(geo)
            sel_list.add(skn)

            shape_dag = sel_list.getDagPath(0)
            skin_dep = sel_list.getDependNode(1)
            skin_fn = oma.MFnSkinCluster(skin_dep)

            comp_ids = [c for c in range(num_verts)]
            single_fn = om.MFnSingleIndexedComponent()
            shape_comp = single_fn.create(om.MFn.kMeshVertComponent)
            single_fn.addElements(comp_ids)
            
            flat_weights, inf_count = skin_fn.getWeights(shape_dag, shape_comp)

            weight_plug = skin_fn.findPlug('weights', False)
            list_plug = skin_fn.findPlug('weightList', False).attribute()

            inf_dags = skin_fn.influenceObjects()
            inf_count = len(inf_dags)
            sparse_map = {skin_fn.indexForInfluenceObject(inf_dag): i for i, inf_dag in enumerate(inf_dags)}
            
            skin_weights = {}
            for c, comp_id in enumerate(comp_ids):
                weight_plug.selectAncestorLogicalIndex(comp_id, list_plug)
                valid_ids = weight_plug.getExistingArrayAttributeIndices()

                comp_weights = {}
                flat_index = c * inf_count
                for valid_id in valid_ids:
                    inf_index = sparse_map[valid_id]
                    comp_weights[inf_index] = flat_weights[flat_index + inf_index]
                
                skin_weights[comp_id] = comp_weights

            wDct['indexWeight'] = skin_weights

            flObj = open(flPath, 'w')
            json.dump(wDct, flObj, indent = 8, sort_keys = True)
            flObj.close()
        else:
            print ('{} has no related skinCluster node.'.format(geo))

def read_weight(geo = '', flPath = '', searchFor = '', replaceWith = ''):
    '''
    '''
    flObj = open(flPath, 'r')
    wDct = json.load(flObj)
    flObj.close()
    
    infs = []

    for oInf in wDct['influences']:
        if searchFor:
            oInf = oInf.replace(searchFor, replaceWith)
            
        if mc.objExists(oInf):
            infs.append(oInf)

    oSkn = mm.eval('findRelatedSkinCluster "{}"'.format(geo))
    if oSkn:
        mc.skinCluster(oSkn, e = True, ub = True)

    skn = mc.skinCluster(infs, geo, n = wDct['name'], tsb = True, nw = 1, sm = wDct['skinningMethod'])[0]
    sknSet = mc.rename(mc.listConnections('{}.message'.format(skn), d = True, s = False)[0], wDct['set'])
    
    for inf in infs:
        mc.setAttr('{}.liw'.format(inf), False)

    inf_count = len(infs)
    num_verts = mc.polyEvaluate(geo, v = True)

    weights = om.MDoubleArray(num_verts * inf_count, 0)
    for id in range(num_verts):
        start_id = id * inf_count
        
        for inf_id, weight in wDct['indexWeight']['{}'.format(id)].viewitems():
            weights[start_id + int(inf_id)] = weight

    sel_list = om.MSelectionList()
    sel_list.add(geo)
    sel_list.add(skn)

    shape_dag = sel_list.getDagPath(0)
    skin_dep = sel_list.getDependNode(1)
    skin_fn = oma.MFnSkinCluster(skin_dep)

    comp_ids = [c for c in range(num_verts)]
    single_fn = om.MFnSingleIndexedComponent()
    shape_comp = single_fn.create(om.MFn.kMeshVertComponent)
    single_fn.addElements(comp_ids)
       
    inf_index = om.MIntArray()
    for i in range(0, inf_count):
      inf_index.append(i)

    skin_fn.setWeights(shape_dag, shape_comp, inf_index, weights)

def write_selected_weight():
    '''
    '''
    fld = get_data_folder()
    dataFld = os.path.join(fld, 'skinWeight')

    if not os.path.isdir(dataFld):
        os.mkdir(dataFld)
        
    suffix = '_SkinWeight'
    for sel in mc.ls(sl = True):
        shapes = mc.listRelatives('{}'.format(sel), shapes = True)

        if shapes:
            try:
                flNmExt = '{}{}.json'.format(sel.split(':')[-1], suffix)
                flPath = os.path.join(dataFld, flNmExt)
                write_weight(sel, flPath)
            except:
                print('{} writing weight is failed.'.format(sel))

    print('{}'.format(dataFld))
    mc.confirmDialog(title = 'Progress', message = 'Exporting weight is done.')

def read_selected_weight(searchFor ='', replaceWith =''):
    '''
    '''
    dataFld = get_data_folder()
    sels = mc.ls(sl = True)

    for sel in sels:
        shapes = mc.listRelatives('{}'.format(sel) , shapes = True)

        if shapes:
            flNm = '{}_SkinWeight.json'.format(sel).replace(replaceWith, searchFor)

            try:
                read_weight(sel, os.path.join(dataFld, 'skinWeight', flNm), searchFor, replaceWith)
                print("Importing {} is done.".format(sel))
            except:
                print("Can't find weight file for {}".format(sel))
    
    mc.select(sels)
    mc.confirmDialog(title = 'Progress', message = 'Importing weight is done.')

def write_ctrl_shape(file_name = 'ctrlShape.dat'):
    '''
    '''
    file_path = os.path.join(get_data_folder(), file_name)
    file_obj = open(file_path, 'w')
    
    ctrlDict = {}
    
    for ctrl in mc.ls('*Ctrl'):
        
        shapes = mc.listRelatives(ctrl, s=True)

        if not shapes: continue # Continue if current controller has no shape.
        
        if mc.nodeType(shapes[0]) == 'nurbsCurve':
            
            cv = mc.getAttr('{}.spans'.format(shapes[0])) + mc.getAttr('{}.degree'.format(shapes[0]))
        
            for ix in range(0, cv):
                cvName = '{}.cv[{}]'.format(shapes[0], str(ix))
                ctrlDict[cvName] = mc.xform(cvName, q = True, os = True, t = True)

            # Write color property
            if mc.getAttr('{}.overrideEnabled'.format(shapes[0])):
                colVal = mc.getAttr('{}.overrideColor'.format(shapes[0]))
                ctrlDict[shapes[0]] = colVal
        
    pickle.dump(ctrlDict, file_obj)
    file_obj.close()

    if os.path.exists( file_path ):
        mc.confirmDialog( title = 'Progress' , message = 'Exporting controls shape is done.' )

def read_ctrl_shape(file_name = 'ctrlShape.dat', searchFor =' ', replaceWith = '', prefix = '', suffix =''):
    '''
    '''
    file_path = os.path.join(get_data_folder(), file_name)

    if os.path.exists(file_path):
        file_obj = open(file_path, 'r')
        ctrlDict = pickle.load(file_obj)
        file_obj.close()

        for key in ctrlDict.keys():

            curr = '{}{}{}'.format(prefix, key.replace(searchFor, replaceWith), suffix)

            if '.' in curr:
                # If current is cv, read the position.
                if mc.objExists(curr):
                    mc.xform(curr, os = True, t = ctrlDict[curr])
            else:
                # If current is object, read the color.
                if mc.objExists(curr):
                    mc.setAttr('{}.overrideEnabled'.format(curr), 1)
                    mc.setAttr('{}.overrideColor'.format(curr), ctrlDict[curr])

def write_attr(obj = '', flPath = ''):
    '''
    '''
    shapes = mc.listRelatives(obj, shapes = True)[0]

    exception = [ 'controlPoints.xValue' ,
                  'controlPoints.yValue' ,
                  'controlPoints.zValue' ,
                  'colorSet.clamped' ,
                  'colorSet.representation' ]

    aDct = {}

    for each in (obj, shapes):
        attrs = mc.listAttr( each, keyable = True, s = True, unlocked = True)

        if attrs :
            aDctAttr = {}

            ary = each.split(':')
            nm = ary[-1]
            nmsp = ':'.join(ary[0:-1])
            aDctAttr['namespace'] = nmsp

            for attr in attrs :
                if not attr in exception :
                    aDctAttr[attr] = mc.getAttr('{}.{}'.format(each, attr))

            aDct[nm] = aDctAttr

        flObj = open(flPath, 'w')
        json.dump(aDct, flObj, indent = 8, sort_keys = True)
        flObj.close()

def write_selected_attr():
    '''
    '''
    fld = get_data_folder()
    dataFld = os.path.join(fld, 'ctrlAttribute')
    
    if not os.path.isdir(dataFld) :
        os.mkdir(dataFld)
        
    suffix = '_Attribute'
    
    for sel in mc.ls(sl = True):
        flNmExt = '{}{}.json'.format(sel.split(':')[-1], suffix)
        flPath = os.path.join(dataFld, flNmExt)
        write_attr(sel, flPath)

    mc.confirmDialog(title = 'Progress', message = 'Exporting attribute is done.')
    print ('\n{}'.format(dataFld))

def write_all_ctrl_attr():
    '''
    '''
    all = mc.ls(ap = True)

    ctrlList = []
    ndTypeList = ['transform', 'joint']

    for ctrl in  all :
        if '_Ctrl' in ctrl :
            if mc.nodeType(ctrl) in ndTypeList :
                ctrlList.append(ctrl)
    
    if ctrlList :
        mc.select(ctrlList)
        write_selected_attr()

    mc.select(cl = True)

def read_attr(obj = '', flPath = ''):
    '''
    '''
    flObj = open(flPath, 'r')
    aDct = json.load(flObj)
    flObj.close()
    
    shapes = mc.listRelatives(obj, shapes = True)[0]
    
    objNmsp = ''
    objNm = obj
    shpNm = shapes
    
    if ':' in obj :
        objAry = obj.split(':')
        objNm = objAry[-1]
        objNmsp = ':'.join(objAry[0:-1]) + ':'
        
        shpAry = shapes.split(':')
        shpNm = shpAry[-1]
        
    for each in (objNm, shpNm):
        objs = aDct[each]
        keys = objs.keys()
        
        for key in keys :
            if not key == 'namespace' :
                ctrl = '{}{}.{}'.format(objNmsp,each,key)

                mc.setAttr(ctrl, objs[key])

def read_selected_attr():
    '''
    '''
    dataFld = get_data_folder()
    sels =  mc.ls(sl = True)
    
    for sel in sels:
        selNm = sel
        selNmsp = ''
        
        if ':' in sel :
            selAry = sel.split(':')
            selNm = selAry[-1]
            selNmsp = ':'.join(selAry[0:-1]) + ':'
            
        flNm = '{}_Attribute.json'.format(selNm)
        
        try:
            read_attr(sel, os.path.join(dataFld, 'ctrlAttribute', flNm))
            print ('Importing {} done.'.format(flNm))
        except:
            print ('Cannot find attribute file for {}'.format(selNm))

def read_all_ctrl_attr():
    '''
    '''
    all = mc.ls(ap = True)

    ctrlList = []
    ndTypeList = ['transform', 'joint']

    for ctrl in  all :
        if '_Ctrl' in ctrl :
            if mc.nodeType(ctrl) in ndTypeList :
                ctrlList.append(ctrl)
                
    if ctrlList :
        mc.select(ctrlList)
        read_selected_attr()

    mc.select(cl = True)