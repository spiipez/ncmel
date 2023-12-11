# System modules.
from imp import reload

# Maya modules.
import maya.cmds as mc

# ncscript modules.
from ncTools.rig import node
from ncTools.rig import util
from ncTools.rig import rig_ribbon as rbn
reload(node)
reload(util)
reload(rbn)

class Neck(object):

    def __init__( self , neck_tmpJnt = 'Neck_TmpJnt',
                         head_tmpJnt = 'Head_TmpJnt',
                         parent = 'Breast_Jnt',
                         ctrl_grp = 'Ctrl_Grp',
                         still_grp = 'Still_Grp',
                         part = '',
                         ribbon = True,
                         subdiv = 0,
                         axis = 'y' ,
                 ):
        
        '''
        '''

        ##-- Prepare
        part = part.capitalize()

        #-- Create main group
        self.neckCtrl_grp = node.Transform('Neck{}Ctrl_Grp'.format(part))
        util.parent_constraint(parent, self.neckCtrl_grp, mo = True)
        mc.parent(self.neckCtrl_grp, ctrl_grp)

        #-- Create joint
        self.neck_jnt = node.Joint('Neck{}_Jnt'.format(part), position = neck_tmpJnt)
        self.neckEnd_jnt = node.Joint('Neck{}End_Jnt'.format(part), position = head_tmpJnt)
        self.neckEnd_grp = node.Transform('Neck{}End_Grp'.format(part))
        self.neckEnd_grp.snap(head_tmpJnt)

        mc.parent(self.neckEnd_grp, self.neckEnd_jnt)
        mc.parent(self.neckEnd_jnt, self.neck_jnt)
        mc.parent(self.neck_jnt, parent)

        #-- Create controls
        self.neck_ctrl = util.controller('Neck{}_Ctrl'.format(part), 'octagon', 'red')
        self.neck_gmbl = util.gimbal(self.neck_ctrl)
        self.neck_zro = util.group(self.neck_ctrl, 'Zro')
        self.neck_zro.snap(neck_tmpJnt)
        
        mc.parent(self.neck_zro, self.neckCtrl_grp)

        #-- Set rotate order
        for __obj in (self.neck_ctrl, self.neck_jnt, self.neckEnd_jnt):
            __obj.rotate_order = 'xzy'

        #-- Rig process
        util.parent_constraint(self.neck_gmbl, self.neck_jnt, mo = False)
        
        self.neck_stretch = util.add_offset_controller( self.neck_ctrl, 
                                                        self.neckEnd_jnt, 
                                                        'stretch', 
                                                        axis, 
                                                        1 )
        
        self.neck_locWor = util.local_world( self.neck_ctrl, 
                                             ctrl_grp, 
                                             self.neckCtrl_grp, 
                                             self.neck_zro, 
                                             'orient' )
        
        self.neck_nonroll_jnt = util.add_non_roll_joint(self.neck_jnt, axis)
        
        #-- Cleanup
        self.neck_ctrl.lock_hide('sx', 'sy', 'sz', 'v')
        
        #-- Additional ribbon
        if ribbon:
            self.neck_rbn_grp,\
            self.neck_rbn_skin,\
            self.neck_rbn_still,\
            self.neck_rbn_ctrl,\
            self.neck_rbn_root_ctrl,\
            self.neck_rbn_end_ctrl = rbn.run( name = 'Neck{}'.format(part),
                                              posiA = self.neck_jnt,
                                              posiB = self.neckEnd_grp,
                                              axis = '{}+'.format(axis),
                                              side = '',
                                              subdiv = subdiv,
                                              constraint = True )
            
            #-- Setup twist
            self.neckEnd_grp.attr('r{}'.format(axis)) >> self.neck_rbn_ctrl.shape.attr('endAbsTwist')
            self.neck_rbn_ctrl.attr('autoTwist').value = 1

            #-- Add tag
            self.neckEnd_jnt.add_str_tag('ribbon', self.neckEnd_grp)

            #-- Manage hierarchy
            mc.parent(self.neck_rbn_grp, self.neckCtrl_grp)
            mc.parent(self.neck_rbn_skin, self.neck_jnt)
            mc.parent(self.neck_rbn_still, still_grp)
        
        mc.select(cl = True)