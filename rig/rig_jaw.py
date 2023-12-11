# System modules.
from imp import reload

# Maya modules.
import maya.cmds as mc

# ncscript modules.
from ncTools.rig import node
from ncTools.rig import util
reload(node)
reload(util)

class Jaw(object):

    def __init__( self , jawUpr1_tmpJnt = 'JawUpr1_TmpJnt' ,
                         jawUprEnd_tmpJnt = 'JawUprEnd_TmpJnt' ,
                         jawLwr1_tmpJnt = 'JawLwr1_TmpJnt' ,
                         jawLwr2_tmpJnt = 'JawLwr2_TmpJnt' ,
                         jawLwrEnd_tmpJnt = 'JawLwrEnd_TmpJnt' ,
                         parent = 'Head_Jnt' ,
                         ctrl_grp = 'Ctrl_Grp' ,
                         part = '' ,
                 ):
        
        '''
        '''

        ##-- Prepare
        part = part.capitalize()

        #-- Create main group
        self.jawCtrl_grp = node.Transform('Jaw{}Ctrl_Grp'.format(part))
        util.trs_constraint(parent, self.jawCtrl_grp, mo = True)
        mc.parent(self.jawCtrl_grp, ctrl_grp)

        #-- Create joint
        self.jawUpr1_jnt = node.Joint('Jaw{}Upr1_Jnt'.format(part), position = jawUpr1_tmpJnt)
        self.jawUprEnd_jnt = node.Joint('Jaw{}UprEnd_Jnt'.format(part), position = jawUprEnd_tmpJnt)

        self.jawLwr1_jnt = node.Joint('Jaw{}Lwr1_Jnt'.format(part), position = jawLwr1_tmpJnt)
        self.jawLwr2_jnt = node.Joint('Jaw{}Lwr2_Jnt'.format(part), position = jawLwr2_tmpJnt)
        self.jawLwrEnd_jnt = node.Joint('Jaw{}LwrEnd_Jnt'.format(part), position = jawLwrEnd_tmpJnt)

        mc.parent(self.jawUprEnd_jnt, self.jawUpr1_jnt)
        mc.parent(self.jawLwrEnd_jnt, self.jawLwr2_jnt)
        mc.parent(self.jawLwr2_jnt, self.jawLwr1_jnt)
        mc.parent(self.jawUpr1_jnt, self.jawLwr1_jnt, parent)

        #-- Create controls
        self.jawLwr1_ctrl = util.controller('Jaw{}Lwr1_Ctrl'.format(part), 'arrowBall', 'red')
        self.jawLwr1_gmbl = util.gimbal(self.jawLwr1_ctrl)
        self.jawLwr1_zro = util.group(self.jawLwr1_ctrl, 'Zro')
        self.jawLwr1_zro.snap(jawLwr1_tmpJnt)

        self.jawLwr2_ctrl = util.controller('Jaw{}Lwr2_Ctrl'.format(part), 'square', 'yellow')
        self.jawLwr2_gmbl = util.gimbal(self.jawLwr2_ctrl)
        self.jawLwr2_zro = util.group(self.jawLwr2_ctrl, 'Zro')
        self.jawLwr2_zro.snap(jawLwr2_tmpJnt)

        self.jawUpr1_ctrl = util.controller('Jaw{}Upr1_Ctrl'.format(part), 'square', 'yellow')
        self.jawUpr1_gmbl = util.gimbal(self.jawUpr1_ctrl)
        self.jawUpr1_zro = util.group(self.jawUpr1_ctrl, 'Zro')
        self.jawUpr1_zro.snap(jawUpr1_tmpJnt)

        #-- Adjust shape controls
        for __ctrl in (self.jawLwr2_ctrl, self.jawLwr2_gmbl, self.jawUpr1_ctrl, self.jawUpr1_gmbl):
            __ctrl.scale_shape(0.3)
            __ctrl.rotate_shape((90, 0, 0))

        self.jawLwr1_ctrl.scale_shape(0.3)

        #-- Set rotate order
        for __obj in (self.jawLwr1_ctrl, self.jawLwr2_ctrl, self.jawUpr1_ctrl,
                     self.jawLwr1_jnt, self.jawLwr2_jnt, self.jawUpr1_jnt):
            __obj.rotate_order = 'zyx'

        #-- Rig process
        for __ctrl, __jnt in zip([self.jawLwr1_gmbl, self.jawLwr2_gmbl, self.jawUpr1_gmbl],
                               [self.jawLwr1_jnt, self.jawLwr2_jnt, self.jawUpr1_jnt]):
            util.parent_constraint(__ctrl, __jnt, mo = True)
            util.scale_constraint(__ctrl, __jnt, mo = True)

        #-- Manage hierarchy
        mc.parent(self.jawLwr2_zro, self.jawLwr1_gmbl)
        mc.parent(self.jawUpr1_zro, self.jawLwr1_zro, self.jawCtrl_grp)

        #-- Cleanup
        self.jawLwr1_ctrl.lhv()
        self.jawLwr2_ctrl.lhv()
        self.jawUpr1_ctrl.lhv()

        self.jawUpr1_jnt.attr('ssc').value = 0
        self.jawLwr1_jnt.attr('ssc').value = 0
        self.jawLwr2_jnt.attr('ssc').value = 0
        
        mc.select(cl = True)