# System modules.
from imp import reload

# Maya modules.
import maya.cmds as mc

# ncscript modules.
from ncTools.rig import node
from ncTools.rig import util
reload(node)
reload(util)

class Pelvis(object):

    def __init__( self , pelvis_tmpJnt = 'Pelvis_TmpJnt', 
                         parent = 'Root_jnt',
                         ctrl_grp = 'Ctrl_Grp', 
                         part = '',
                 ):
        
        '''
        '''

        ##-- Prepare
        part = part.capitalize()

        #-- Create main group
        self.pelvisCtrl_grp = node.Transform('Pelvis{}Ctrl_Grp'.format(part))
        util.parent_constraint(parent, self.pelvisCtrl_grp, mo = True)
        mc.parent(self.pelvisCtrl_grp, ctrl_grp)

        #-- Create joint
        self.pelvis_jnt = node.Joint('Pelvis{}_Jnt'.format(part), position = pelvis_tmpJnt)
        mc.parent(self.pelvis_jnt, parent)
        
        #-- Create controls
        self.pelvis_ctrl = util.controller('Pelvis{}_Ctrl'.format(part), 'cube', 'yellow')
        self.pelvis_gmbl = util.gimbal(self.pelvis_ctrl)
        self.pelvis_zro = util.group(self.pelvis_ctrl, 'Zro')
        self.pelvis_zro.snap(pelvis_tmpJnt)
        
        mc.parent(self.pelvis_zro, self.pelvisCtrl_grp)
        
        #-- Set rotate order
        for __obj in (self.pelvis_ctrl, self.pelvis_jnt):
            __obj.rotate_order = 'xzy'

        #-- Rig process
        util.parent_constraint(self.pelvis_gmbl, self.pelvis_jnt, mo = False)
        self.pelvis_locWor = util.local_world(self.pelvis_ctrl, ctrl_grp, self.pelvisCtrl_grp, self.pelvis_zro, 'orient')
        
        #-- Cleanup
        self.pelvis_ctrl.lock_hide('sx', 'sy', 'sz', 'v')
        
        mc.select(cl = True)