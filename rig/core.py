# System modules.
from imp import reload
import re

# Maya modules.
import maya.cmds as mc
import maya.OpenMaya as om

class Attribute(object):
    '''
    '''
    def __init__(self, attr_name):
        self.name = str(attr_name)
        self.nodename = str(attr_name)
        self.attrname = None
        self.children = None

        if '.' in str(attr_name):
            array = str(attr_name).split('.')
            self.nodename = array[0]
            self.attrname = '.'.join(array[1:])
            self.queryname = re.findall(r'([_a-zA-Z0-9]+)', array[-1])[0]

            if self.exists:
                self.children = mc.attributeQuery(self.queryname, node = self.nodename, listChildren = True)

    def __str__(self):
        return str(self.name)
    
    def __repr__(self) :
        return str(self.name)

    def __rshift__(self, target):
        if mc.objExists(target):
            mc.connectAttr(self.name, target, f = True)
        else:
            raise Exception('{} does not exists!'.format(target))

    def __floordiv__(self, target):
        if mc.objExists(target):
            mc.disconnectAttr(self.name, target)
        else:
            raise Exception('{} does not exists!'.format(target))

    def _setter(self, *args, **kwargs):
        if not self.children:
            mc.setAttr(self.name, *args, **kwargs)
            return True
        else:
            if len(args[0]) == len(self.children):
                for val, chld in zip(args[0], self.children):
                    lock_status = None
                    
                    try : lock_status = mc.getAttr(self.name, l = True)
                    except : pass

                    if lock_status:
                        mc.setAttr(self.name, lock = False)

                    mc.setAttr('{}.{}'.format(self.name, chld), val, **kwargs)
                    
                    if lock_status:
                        mc.setAttr(self.name, lock = True)
                return True
            else:
                raise ValueError('Invalid or out of argument value! ({} given)'.format(len(self.children))) 

    @property
    def value(self):
        val = mc.getAttr(self.name)
        if isinstance(val, list) or isinstance(val, tuple):
            if isinstance(val[0], list) or isinstance(val[0], tuple):
                val = val[0]
        return val
    
    @value.setter
    def value(self, val):
        self._setter(val)
    
    v = value

    @property
    def lock(self):
        return mc.getAttr(self.name, lock = True)
    
    @lock.setter
    def lock(self, val):
        if not self.children:
            mc.setAttr(self.name, lock = val)
            return True
        else:
            for chld in self.children:
                mc.setAttr('{}.{}'.format(self.nodename, chld), lock = val)
            return True

    @property
    def hide(self):
        return not mc.getAttr(self.name, k = True)

    @hide.setter
    def hide(self, val):
        if not self.children:
            mc.setAttr(self.name, k = not val)
            mc.setAttr(self.name, cb = not val)
            return True
        else:
            for chld in self.children:
                mc.setAttr('{}.{}'.format(self.nodename, chld), k = not val)
                mc.setAttr('{}.{}'.format(self.nodename, chld), cb = not val)
            return True

    @property
    def connections(self, **kwargs):
        cons = mc.listConnections(self.name, **kwargs)
        if not cons:
            return None

    @property
    def exists(self):
        return mc.objExists(self.name)
    
    def remove(self):
        mc.deleteAttr(self.name)

    def get_input(self):
        cons = mc.listConnections(self.name, s = True, d = False, p = True)
        if cons:
            return Attribute(cons[0])
        else:
            return None

    def get_output(self):
        cons = mc.listConnections(self.name, s = False, d = True, p = True)
        if cons:
            return Attribute(cons[0])
        else:
            return None

    def last(self):
        '''
        '''
        if not mc.attributeQuery(self.attrname, node = self.nodename, multi = True):
            return self.name

        ix = 0
        while True:
            curr_attr = '{}[{}]'.format(self.attrname, ix)
            if mc.listConnections('{}.{}'.format(self.nodename, curr_attr), s = True, d = False, p = True):
                ix += 1
                continue
            else:
                return self.nodename + '.' + curr_attr
  
class Node(object):
    '''
    '''
    def __init__(self, name):
        if not mc.objExists(name):
            raise Exception('{} does not exists!'.format(name))
        
        self.sellist = om.MSelectionList()
        self.sellist.add(name)

        self.mObj = om.MObject()
        self.sellist.getDependNode(0, self.mObj)

        self.fn_dependency_node = om.MFnDependencyNode(self.mObj)
    
    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
    
    @property
    def name(self):
        return self.fn_dependency_node.name()

    @name.setter
    def name(self, new_name):
        mc.rename(self.name, new_name)

    @property
    def side(self):
        curr_side = '_'
        for side in ['L','R']:
            if '_{}_'.format(side) in self.name:
                curr_side = '_{}_'.format(side)
        return curr_side
    
    @property
    def prefix(self):
        nmsp = ' '
        if ':' in self.name:
            nmsp = self.name.split(':')[0] + ':'

        if '_' in self.name:
            return self.name.split('_')[0].split(nmsp)[-1]
        else:
            return self.name
        
    @property
    def suffix(self):
        return self.name.replace(self.prefix, '')
    
    @property
    def type(self):
        return self.name.split('_')[-1].capitalize()
    
    def list_attr_from_channelbox(self, **kwargs):
        attrs = list()
        attrs.extend(mc.listAttr(self, sn = True, k = True))
        attrs.extend(mc.listAttr(self, sn = True, cb = True))

        if kwargs:
            if kwargs['skip']:
                for skip in kwargs['skip']:
                    attrs.pop(attrs.index(skip))

        return attrs

    def lock_hide(self, *args):
        for attr in args:
            self.attr(attr).lock = True
            self.attr(attr).hide = True
    
    def attr(self, attr_name):
        return Attribute('{}.{}'.format(self.name, attr_name))

    def add_attr(self, attr_name = '', at = 'float', k = True, **kwargs):
        ''' Add attribute
        '''
        if not mc.objExists('{}.{}'.format(self.name, attr_name)):
            mc.addAttr(self.name, ln = attr_name, at = at, k = k, **kwargs)

    def add_divide_attr(self, attr_name = ''):
        ''' Add divide attribute
        '''
        nice_name_attr = ' '.join(re.findall('.[^A-Z]*', attr_name[0].upper() + attr_name[1:]))
        if not mc.objExists('{}.{}'.format(self.name, attr_name)):
            mc.addAttr(self.name, ln = attr_name, nn = '__{}'.format(nice_name_attr), at = 'float', min = 0, max = 1)
            mc.setAttr('{}.{}'.format(self.name, attr_name), k = False, cb = True)
            
    def add_vector_attr(self, attr_name = '', k = True):
        if not mc.objExists('{}.{}'.format(self.name, attr_name)):
            mc.addAttr(self.name, ln = attr_name, at = 'double3')
            mc.addAttr(self.name, ln = '{}X'.format(attr_name), at = 'double', parent = attr_name, k = k)
            mc.addAttr(self.name, ln = '{}Y'.format(attr_name), at = 'double', parent = attr_name, k = k)
            mc.addAttr(self.name, ln = '{}Z'.format(attr_name), at = 'double', parent = attr_name, k = k)

    def add_str_tag(self, attr_name = '', str = ''):
        if not mc.objExists('{}.{}'.format(self.name, attr_name)):
            mc.addAttr(self.name, ln = attr_name, dt = 'string', k = False)
        mc.setAttr('{}.{}'.format(self.name, attr_name), str, type = "string")
        
    def add_bool_tag(self, attr_name = '', val = True):
        if not mc.objExists('{}.{}'.format(self.name, attr_name)):
            mc.addAttr(self.name, ln = attr_name, at = 'bool', k = False)
        mc.setAttr('{}.{}'.format(self.name, attr_name), val)

    def list_attr_from_channelbox(self, **kwargs):
        attrs = []
        attrs.extend(mc.listAttr(self.pynode, sn = True, k = True))
        attrs.extend(mc.listAttr(self.pynode, sn = True, cb = True))

        if kwargs:
            if kwargs['skip']:
                for skip in kwargs['skip']:
                    attrs.pop(attrs.index(skip))

        return attrs

class Dag(Node):
    '''
    '''
    def __init__(self, name):
        super(Dag, self).__init__(name)

        self.mDagPath = om.MDagPath()
        self.sellist.getDagPath(0, self.mDagPath)
        self.fnDagNode = om.MFnDagNode(self.mDagPath)
        
    @property
    def name(self):
        if len(mc.ls(self.mDagPath.partialPathName())) > 1:
            return self.mDagPath.fullPathName()
        else:
            return self.mDagPath.partialPathName()
        
    @name.setter
    def name(self, new_name):
        mc.rename(self.name, new_name)

    def get_parent(self):
        parent = self.fnDagNode.parent(0)
        if parent.apiType() == om.MFn.kWorld:
            return None
        parentname = om.MFnDagNode(parent).fullPathName()
        return Dag(parentname)

    def get_shape(self):
        shapes = mc.listRelatives(self.name, s = True, f = True)
        if not shapes:
            return None
        return Dag(shapes[0])
    
    @property
    def shape(self):
        return self.get_shape()

    def get_all_shapes(self):
        shapes = mc.listRelatives(self.name, s=True, f=True)
        if not shapes:
            return None
        return [Dag(shape) for shape in shapes]
    
    @property
    def shape_all(self):
        return self.get_all_shapes()

    def get_child(self):
        children = mc.listRelatives(self.name, type = 'transform')
        if children:
            return Dag(children[0])
        else:
            None
    
    def get_all_children(self):
        children = mc.listRelatives(self.name, type = 'transform')
        if children:
            return [Dag(chd) for chd in children]

    @property
    def color(self):
        if not self.shape:
            return None
        return self.shape.attr('overrideColor').value

    @color.setter
    def color(self, color):
        color_ids = {'none'      : 0,
                     'black'     : 1,
                     'gray'      : 2,
                     'softGray'  : 3,
                     'darkRed'   : 4,
                     'darkBlue'  : 5,
                     'blue'      : 6,
                     'darkGreen' : 7,
                     'brown'     : 11,
                     'red'       : 13,
                     'green'     : 14,
                     'white'     : 16,
                     'yellow'    : 17,
                     'cyan'      : 18,
                     'pink'      : 20}
        
        if type(color) == type(str()):
            if color in color_ids.keys():
                id = color_ids[color]
            else :
                id = 0
        else :
            id = color

        if self.shape:
            self.shape.attr('overrideEnabled').value = True
            self.shape.attr('overrideColor').value = id

    @property
    def rotate_order(self):
        return mc.getAttr('{}.rotateOrder'.format(self.name))

    @rotate_order.setter
    def rotate_order(self, value):
        rotate_order_ids = { 'xyz':0, 'yzx':1, 'zxy':2, 'xzy':3, 'yxz':4, 'zyx':5 }

        if value in rotate_order_ids.keys():
            value = rotate_order_ids[value]

        mc.setAttr('{}.rotateOrder'.format(self.name), value)

    @property
    def get_world_space_from_posi(self):
        pass
    
    @property
    def pivot(self):
        return mc.xform(self.name, q = True, t = True, ws = True )
    
    @pivot.setter
    def pivot(self, pos):
        mc.move(pos[0], pos[1], pos[2], '{}.scalePivot'.format(self.name), '{}.rotatePivot'.format(self.name) ,absolute = True)

    def duplicate(self, name):
        dup = mc.duplicate(self.name, rr = True)
        if name:
            dup = mc.rename(dup, name)
        return dup
    
    def set_parent(self, parent = ''):
        '''
        '''    
        mSel = om.MSelectionList()
        mSel.add(str(self.name))
        mObj = om.MObject()
        mSel.getDependNode(0, mObj)
        if mObj.hasFn(om.MFn.kShape):
            mc.parent(self, parent, s = True, r = True)
        else:
            if parent:
                try: mc.parent(self, parent)
                except RuntimeError: pass
            else:
                if self.get_parent():
                    mc.parent(self, w = True)

    def delete_history(self):
        mc.delete(self.name, ch = True)

    def freeze(self, **kwargs):
        mc.makeIdentity(self.name, a = True, **kwargs)
    
    def snap(self, *args, **kwargs):
        mc.delete(mc.parentConstraint(args, self.name, mo = False, **kwargs))

    def snap_point(self, *args, **kwargs):
        mc.delete(mc.pointConstraint(args, self.name, mo = False, **kwargs))

    def snap_orient(self, *args, **kwargs):
        mc.delete(mc.orientConstraint(args, self.name, mo = False, **kwargs))
    
    def snap_scale(self, target, **kwargs):
        mc.delete(mc.scaleConstraint(target, self.name, mo = False, **kwargs))

    def snap_aim(self, target, **kwargs):
        mc.delete(mc.aimConstraint(target, self.name, mo = False, **kwargs))

    # def snap_aim(self, target, aim = (0,1,0), upvec = (1,0,0), worldUpObj = '', worldUpVec = (0,1,0), **kwargs):
    #     if worldUpObj:
    #         mc.delete(mc.aimConstraint(target, self.name, mo = False, aim = aim, u = upvec, wut = 'objectrotation', wuo = worldUpObj, wu  = worldUpVec, **kwargs))
    #     else:
    #         mc.delete(mc.aimConstraint(target, self.name, mo = False, aim = aim, u = upvec, **kwargs))

    def snap_joint_orient(self, target):
        mc.delete(mc.orientConstraint((target, self.name), mo = False))
        ro = self.attr('r').value
        mc.setAttr('{}.jointOrient'.format(self), *ro)
        mc.setAttr('{}.r'.format(self), 0, 0, 0)

    def snap_world_orient(self):
        worGrp = mc.createNode('transform')
        mc.delete(mc.orientConstraint((worGrp, self.name), mo = False))
        mc.delete(worGrp)

    def snap_pivot(self, target):
        position = mc.xform(target, q = True, worldSpace = True, rotatePivot = True)
        mc.xform(self.name, piv = [position[0], position[1], position[2]], ws = True)

    def snap_matrix(self, target):
        val = mc.xform(target, q = True, worldSpace = True, matrix = True)
        mc.xform(self.name, worldSpace = True, matrix = val)
        
    def move_shape(self, value):
        degree = mc.getAttr('{}.degree'.format(self.shape))
        spans = mc.getAttr('{}.spans'.format(self.shape))
        component = '{}.cv[0:{}]'.format(self.name, (spans + degree)-1)
        mc.move(value[0], value[1], value[2], component, relative = True, objectSpace = True, worldSpaceDistance = True)

    def rotate_shape(self, value):
        degree = mc.getAttr('{}.degree'.format(self.shape))
        spans = mc.getAttr('{}.spans'.format(self.shape))
        component = '{}.cv[0:{}]'.format(self.name, (spans + degree)-1)
        mc.rotate(value[0], value[1], value[2], component, r = True, os = True, p = (self.pivot[0], self.pivot[1], self.pivot[2]))

    def scale_shape(self, value):
        degree = mc.getAttr('{}.degree'.format(self.shape))
        spans = mc.getAttr('{}.spans'.format(self.shape))
        component = '{}.cv[0:{}]'.format(self.name, (spans + degree)-1)
        mc.scale(value, value, value, component, r = True)

    def lhtrs(self):
        '''
        '''
        for at in ('t', 'r', 's'):
            self.attr(at).lock = True
            self.attr(at).hide = True

    def lhv(self):
        '''
        '''
        self.attr('v').lock = True
        self.attr('v').hide = True

    def disable(self):
        '''
        '''
        for attr in mc.listAttr(self.name, k = True):
            self.attr(attr).lock = True
            self.attr(attr).hide = True

        shape = self.shape
        if shape:
            shape.attr('v').value = False

    def hide(self):
        self.attr('v').value = 0

    def show(self):
        self.attr('v').value = 1

def to_rig_node(name):
    '''
    '''
    mSel = om.MSelectionList()
    mSel.add(str(name))
    mObj = om.MObject()
    mSel.getDependNode(0, mObj)

    if mObj.hasFn(om.MFn.kTransform):
        return Dag(name)
    else:
        return Node(name)

def to_rig_nodes(names):
    return tuple([to_rig_node(name) for name in names])