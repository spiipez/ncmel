# System modules.
from imp import reload

# Maya modules.
import maya.cmds as mc

# ncscript modules.
from ncTools.rig import node
from ncTools.rig import util
reload(node)
reload(util)

class Spine(object):

    def __init__( self , spine1_tmpJnt = 'Spine1_TmpJnt',
                         spine2_tmpJnt = 'Spine2_TmpJnt',
                         spine3_tmpJnt = 'Spine3_TmpJnt',
                         spine4_tmpJnt = 'Spine4_TmpJnt',
                         parent = 'Root_jnt',
                         ctrl_grp = 'Ctrl_Grp',
                         part = '',
                ):
        
        '''
        '''
        
        ##-- Prepare
        part = part.capitalize()

        #-- Create main group
        self.spineCtrl_grp = node.Transform('Spine{}Ctrl{}Grp'.format(part))
        util.parent_constraint(parent, self.spineCtrl_grp, mo = True)

        #-- Create joint
        self.spine1Pos_jnt = node.Joint('Spine{}1Pos_Jnt'.format(part), position = spine1_tmpJnt)
        self.spine2Pos_jnt = node.Joint('Spine{}2Pos_Jnt'.format(part), position = spine2_tmpJnt)
        self.spine3Pos_jnt = node.Joint('Spine{}3Pos_Jnt'.format(part), position = spine3_tmpJnt)
        self.spine4Pos_jnt = node.Joint('Spine{}4Pos_Jnt'.format(part), position = spine4_tmpJnt)

        self.spine1_jnt = node.Joint('Spine{}1_Jnt'.format(part), position = spine1_tmpJnt)
        self.spine2_jnt = node.Joint('Spine{}2_Jnt'.format(part), position = spine2_tmpJnt)
        self.spine3_jnt = node.Joint('Spine{}3_Jnt'.format(part), position = spine3_tmpJnt)
        self.spine4_jnt = node.Joint('Spine{}4_Jnt'.format(part), position = spine4_tmpJnt)

        mc.parent(self.spine4Pos_jnt, self.spine3Pos_jnt)
        mc.parent(self.spine3Pos_jnt, self.spine2Pos_jnt)
        mc.parent(self.spine2Pos_jnt, self.spine1Pos_jnt)
        mc.parent(self.spine1Pos_jnt, parent)

        mc.parent(self.spine4_jnt, self.spine4Pos_jnt)
        mc.parent(self.spine3_jnt, self.spine3Pos_jnt)
        mc.parent(self.spine2_jnt, self.spine2Pos_jnt)
        mc.parent(self.spine1_jnt, self.spine1Pos_jnt)

        #-- Create controls
        self.spine1_ctrl = util.controller('Spine{}1_Ctrl'.format(part), 'circle', 'red')
        self.spine1_gmbl = util.gimbal(self.spine1_ctrl)
        self.spine1_zro = util.group(self.spine1_ctrl, 'Zro')
        self.spine1_ofst = util.group(self.spine1_ctrl, 'Ofst')
        self.spine1_zro.snap(spine1_tmpJnt)

        self.spine2_ctrl = util.controller('Spine{}2_Ctrl'.format(part), 'circle', 'red')
        self.spine2_gmbl = util.gimbal(self.spine2_ctrl)
        self.spine2_zro = util.group(self.spine2_ctrl, 'Zro')
        self.spine2_ofst = util.group(self.spine2_ctrl, 'Ofst')
        self.spine2_zro.snap(spine2_tmpJnt)

        self.spine3_ctrl = util.controller('Spine{}3_Ctrl'.format(part), 'circle', 'red')
        self.spine3_gmbl = util.gimbal(self.spine3_ctrl)
        self.spine3_zro = util.group(self.spine3_ctrl, 'Zro')
        self.spine3_ofst = util.group(self.spine3_ctrl, 'Ofst')
        self.spine3_zro.snap(spine3_tmpJnt)

        self.spine4_ctrl = util.controller('Spine{}4_Ctrl'.format(part), 'circle', 'red')
        self.spine4_gmbl = util.gimbal(self.spine4_ctrl)
        self.spine4_zro = util.group(self.spine4_ctrl, 'Zro')
        self.spine4_ofst = util.group(self.spine4_ctrl, 'Ofst')
        self.spine4_zro.snap(spine4_tmpJnt)
        
        mc.parent(self.spine4_zro, self.spine3_gmbl)
        mc.parent(self.spine3_zro, self.spine2_gmbl)
        mc.parent(self.spine2_zro, self.spine1_gmbl)
        mc.parent(self.spine1_zro, self.spineCtrl_grp)

        #-- Adjust shape controls
        for __ctrl in (self.spine1_ctrl, self.spine1_gmbl, self.spine2_ctrl, self.spine2_gmbl, 
                       self.spine3_ctrl, self.spine3_gmbl, self.spine4_ctrl, self.spine4_gmbl):
            __ctrl.scale_shape(1.8)

        #-- Set rotate order
        for __obj in (self.spine1_ctrl, self.spine2_ctrl, self.spine3_ctrl, self.spine4_ctrl,
                      self.spine1Pos_jnt, self.spine2Pos_jnt, self.spine3Pos_jnt, self.spine4Pos_jnt,
                      self.spine1_jnt, self.spine2_jnt, self.spine3_jnt, self.spine4_jnt):
            __obj.rotate_order = 'xzy'

        #-- Rig process
        util.parent_constraint( self.spine1_gmbl, 
                                self.spine1Pos_jnt, 
                                mo = False )
        
        util.parent_constraint( self.spine2_gmbl, 
                                self.spine2Pos_jnt, 
                                mo = False )
        
        util.parent_constraint( self.spine3_gmbl, 
                                self.spine3Pos_jnt, 
                                mo = False )
        
        util.parent_constraint( self.spine4_gmbl, 
                                self.spine4Pos_jnt, 
                                mo = False )
        
        self.spine1_stretch = util.add_offset_controller(self.spine1_ctrl, self.spine2_ofst, 'stretch', 'y', 1)
        self.spine1_stretch = util.add_offset_controller(self.spine2_ctrl, self.spine3_ofst, 'stretch', 'y', 1)
        self.spine1_stretch = util.add_offset_controller(self.spine3_ctrl, self.spine4_ofst, 'stretch', 'y', 1)
        
        util.add_squash_controller(self.spine1_ctrl, self.spine1_jnt, 'xz')
        util.add_squash_controller(self.spine2_ctrl, self.spine2_jnt, 'xz')
        util.add_squash_controller(self.spine3_ctrl, self.spine3_jnt, 'xz')
        util.add_squash_controller(self.spine4_ctrl, self.spine4_jnt, 'xz')
     
        self.spine_locWor = util.local_world(self.spine1_ctrl, ctrl_grp, self.spineCtrl_grp, self.spine1_zro, 'orient')
        
        #-- Cleanup
        for __obj in (self.spine1_ctrl, self.spine2_ctrl, self.spine3_ctrl, self.spine4_ctrl):
            __obj.lock_hide('sx', 'sy', 'sz', 'v')
            
        mc.select(cl = True)