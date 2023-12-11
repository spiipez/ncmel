# System modules.
from imp import reload

# Maya modules.
import maya.cmds as mc

# ncscript modules.
from ncTools.rig import node
from ncTools.rig import util
reload(node)
reload(util)

class Root(object):

    def __init__(self, root_tmpJnt = '',
                       ctrl_grp = '',
                       skin_grp = '',
                       part = ''
                ):

        '''
        '''

        ##-- Prepare
        part = part.capitalize()

        #-- Create main group
        self.rootCtrl_grp = node.Transform('Root{}Ctrl_Grp'.format(part))
        self.rootCtrl_grp.snap(root_tmpJnt)
        mc.parent(self.rootCtrl_grp, ctrl_grp)
        
        #-- Create joint
        self.root_jnt = node.Joint('Root{}_Jnt'.format(part))

        #-- Create controls
        self.root_ctrl = util.controller('Root{}_Ctrl'.format(part), 'octagon', 'green', True)
        self.root_gmbl = util.gimbal(self.root_ctrl)
        self.root_zro = util.group(self.root_ctrl, 'Zro')

        self.root_zro.snap_point(root_tmpJnt)
        self.root_ctrl.snap_joint_orient(root_tmpJnt)

        self.rootPiv_ctrl = util.controller('Root{}Piv_Ctrl'.format(part), 'locator', 'white')
        self.rootPiv_zro = util.group(self.rootPiv_ctrl, 'Zro')
        self.rootPiv_zro.snap(root_tmpJnt)

        #-- Adjust shape controls
        for __ctrl in (self.root_ctrl, self.root_gmbl):
            __ctrl.scale_shape(3)

        #-- Set rotate order
        for __obj in (self.root_jnt, self.root_ctrl):
            __obj.rotate_order = 'xzy'

        #-- Rig process
        util.parent_constraint(self.root_gmbl, self.root_jnt, mo = False)

        self.root_ctrl.shape.add_attr('pivotControl', min = 0, max = 1)
        self.root_ctrl.shape.attr('pivotControl') >> self.rootPiv_zro.attr('v')

        self.rootPiv_ctrl.attr('t') >> self.root_ctrl.attr('rotatePivot')
        self.rootPiv_ctrl.attr('t') >> self.root_ctrl.attr('scalePivot')
        
        #-- Manage hierarchy
        mc.parent(self.root_zro, self.rootPiv_zro, self.rootCtrl_grp)
        mc.parent(self.root_jnt, skin_grp)

        #-- Cleanup
        for __obj in (self.root_ctrl, self.rootPiv_ctrl):
            __obj.lock_hide('sx', 'sy', 'sz', 'v')
        
        mc.select(cl = True)