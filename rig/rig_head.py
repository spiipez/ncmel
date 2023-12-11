# System modules.
from imp import reload

# Maya modules.
import maya.cmds as mc

# ncscript modules.
from ncTools.rig import node
from ncTools.rig import util
reload(node)
reload(util)

class Head(object):

    def __init__( self , head_tmpJnt = 'Head_TmpJnt',
                         headEnd_tmpJnt = 'HeadEnd_TmpJnt',
                         parent = 'NeckEnd_Jnt',
                         ctrl_grp = 'Ctrl_Grp',
                         part = ''
                 ):
        
        '''
        '''

        ##-- Prepare
        part = part.capitalize()

        #-- Create main group
        self.headCtrl_grp = node.Transform('Head{}Ctrl_Grp'.format(part))
        util.parent_constraint(parent, self.headCtrl_grp, mo = True)
        mc.parent(self.headCtrl_grp, ctrl_grp)

        #-- Create joint
        self.head_jnt = node.Joint('Head{}_Jnt'.format(part), position = head_tmpJnt)
        self.headEnd_jnt = node.Joint('Head{}End_Jnt'.format(part), position = headEnd_tmpJnt)

        mc.parent(self.headEnd_jnt, self.head_jnt)
        mc.parent(self.head_jnt, parent)

        #-- Create controls
        self.head_ctrl = util.controller('Head{}_Ctrl'.format(part), 'cube', 'blue')
        self.head_gmbl = util.gimbal(self.head_ctrl)
        self.head_zro = util.group(self.head_ctrl, 'Zro')
        self.head_zro.snap(head_tmpJnt)
        
        #-- Set rotate order
        for __obj in (self.head_ctrl, self.head_jnt, self.headEnd_jnt):
            __obj.rotate_order = 'xzy'

        #-- Rig process
        util.trs_constraint(self.head_gmbl, self.head_jnt, mo = False)
        self.head_locWor = util.local_world(self.head_ctrl, ctrl_grp, self.headCtrl_grp, self.head_zro, 'orient')
        
        if mc.objExists('{}.ribbon'.format(parent)):
            ribbon_pars = mc.getAttr('{}.ribbon'.format(parent))
            util.parent_constraint(self.head_jnt, ribbon_pars, mo = False)

        #-- Manage hierarchy
        mc.parent(self.head_zro, self.headCtrl_grp)

        #-- Cleanup
        self.head_ctrl.lhv()
        self.head_ctrl.attr('localWorld').value = 1
        self.head_jnt.attr('ssc').value = 0
        self.headEnd_jnt.attr('ssc').value = 0

        mc.select(cl = True)