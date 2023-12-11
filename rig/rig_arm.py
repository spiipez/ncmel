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

class Arm(object):

    def __init__( self , uparm_tmpJnt = 'UpArm_L_tmpJnt',
                         forearm_tmpJnt = 'Forearm_L_tmpJnt',
                         wrist_tmpJnt = 'Wrist_L_tmpJnt',
                         hand_tmpJnt = 'Hand_L_tmpJnt',
                         elbow_tmpJnt = 'Elbow_L_tmpJnt',
                         parent = 'ClavEnd_L_Jnt',
                         ctrl_grp = 'Ctrl_Grp',
                         still_grp = 'Still_Grp',
                         part = '',
                         side = 'L',
                         ribbon = True
                ):
        
        '''
        '''
        
        ##-- Prepare
        part = part.capitalize()
        side = util.set_side(side)
        rotate_order = 'yxz'

        side_value = 1
        axis = 'y+'
        elbow_aimvec = (0, -1, 0)
        elbow_upvec = (1, 0, 0)

        if 'R' in side:
            side_value = -1
            axis = 'y-'
            elbow_aimvec = (0, 1, 0)
            elbow_upvec = (-1, 0, 0)

        aim_axis = axis[0]
        sqsh_axis = 'xyz'.replace(aim_axis,'')

        #-- Create main group
        self.armCtrl_grp = node.Transform('Arm{}Ctrl{}Grp'.format(part, side))
        self.armScl_grp = node.Transform('Arm{}Scl{}Grp'.format(part, side))
        self.armJnt_grp = node.Transform('Arm{}Jnt{}Grp'.format(part, side))
        self.armRigJnt_grp = node.Transform('Arm{}RigJnt{}Grp'.format(part, side))

        self.armCtrl_grp.snap(parent)
        self.armScl_grp.snap(uparm_tmpJnt)
        self.armJnt_grp.snap(uparm_tmpJnt)
        self.armRigJnt_grp.snap(uparm_tmpJnt)

        mc.parent(self.armRigJnt_grp, self.armJnt_grp)
        mc.parent(self.armJnt_grp, self.armScl_grp)
        mc.parent(self.armScl_grp, self.armCtrl_grp)
        mc.parent(self.armCtrl_grp, ctrl_grp)

        #-- Create joint
        self.uparm_jnt = node.Joint('UpArm{}{}Jnt'.format(part, side), position = uparm_tmpJnt)
        self.forearm_jnt = node.Joint('Forearm{}{}Jnt'.format(part, side), position = forearm_tmpJnt)
        self.wrist_jnt = node.Joint('Wrist{}{}Jnt'.format(part, side), position = wrist_tmpJnt)
        self.hand_jnt = node.Joint('Hand{}{}Jnt'.format(part, side), position = hand_tmpJnt)

        mc.parent(self.hand_jnt, self.wrist_jnt)
        mc.parent(self.wrist_jnt, self.forearm_jnt)
        mc.parent(self.forearm_jnt, self.uparm_jnt)
        mc.parent(self.uparm_jnt, parent)

        #-- Create rig joint
        self.uparm_rigJnt = node.Joint('UpArm{}{}RigJnt'.format(part, side), position = uparm_tmpJnt)
        self.forearm_rigJnt = node.Joint('Forearm{}{}RigJnt'.format(part, side), position = forearm_tmpJnt)
        self.wrist_rigJnt = node.Joint('Wrist{}{}RigJnt'.format(part, side), position = wrist_tmpJnt)
        self.hand_rigJnt = node.Joint('Hand{}{}RigJnt'.format(part, side), position = hand_tmpJnt)

        mc.parent(self.hand_rigJnt, self.wrist_rigJnt)
        mc.parent(self.wrist_rigJnt, self.forearm_rigJnt)
        mc.parent(self.forearm_rigJnt, self.uparm_rigJnt)
        mc.parent(self.uparm_rigJnt, self.armRigJnt_grp)

        #-- Create main controls
        self.arm_ctrl = util.controller('Arm{}{}Ctrl'.format(part, side), 'stickSphere', 'green')
        self.arm_zro = util.group(self.arm_ctrl, 'Zro')
        
        mc.parent(self.arm_zro, self.armScl_grp)
        
        #-- Adjust shape controls
        if 'L' in side:
            self.arm_ctrl.rotate_shape((0, 90, 90))
        else:
            self.arm_ctrl.rotate_shape((0, 90, -90))
        
        #-- Set rotate order
        for __jnt in (self.uparm_jnt, self.forearm_jnt, self.wrist_jnt, self.hand_jnt,
                     self.uparm_rigJnt, self.forearm_rigJnt, self.wrist_rigJnt, self.hand_rigJnt):
            __jnt.rotate_order = rotate_order

        #-- Rig process
        util.parent_constraint(self.uparm_rigJnt, self.uparm_jnt, mo = False)
        util.parent_constraint(self.forearm_rigJnt, self.forearm_jnt, mo = False)
        util.parent_constraint(self.wrist_rigJnt, self.wrist_jnt, mo = False)
        util.parent_constraint(self.hand_rigJnt, self.hand_jnt, mo = False)
        util.parent_constraint(self.wrist_jnt, self.arm_zro, mo = False)

        self.uparm_nonroll_jnt = util.add_non_roll_joint(self.uparm_jnt, aim_axis)
        self.forearm_nonroll_jnt = util.add_non_roll_joint(self.forearm_jnt, aim_axis)

        #-- Cleanup
        self.arm_ctrl.lhtrs()
        self.arm_ctrl.lhv()
        self.armJnt_grp.hide()

        #-- Fk
        #-- Fk Create main group
        self.armCtrl_fk_grp = node.Transform('Arm{}FkCtrl{}Grp'.format(part, side))
        self.armJnt_fk_grp = node.Transform('Arm{}FkJnt{}Grp'.format(part, side))

        self.armCtrl_fk_grp.snap(uparm_tmpJnt)
        self.armJnt_fk_grp.snap(uparm_tmpJnt)

        mc.parent(self.armCtrl_fk_grp, self.armScl_grp)
        mc.parent(self.armJnt_fk_grp, self.armJnt_grp)

        util.parent_constraint(parent, self.armCtrl_fk_grp)

        #-- Fk Create rig joint
        self.uparm_fk_rigJnt = node.Joint('UpArm{}Fk{}RigJnt'.format(part, side), position = uparm_tmpJnt)
        self.forearm_fk_rigJnt = node.Joint('Forearm{}Fk{}RigJnt'.format(part, side), position = forearm_tmpJnt)
        self.wrist_fk_rigJnt = node.Joint('Wrist{}Fk{}RigJnt'.format(part, side), position = wrist_tmpJnt)
        self.hand_fk_rigJnt = node.Joint('Hand{}Fk{}RigJnt'.format(part, side), position = hand_tmpJnt)

        mc.parent(self.hand_fk_rigJnt, self.wrist_fk_rigJnt)
        mc.parent(self.wrist_fk_rigJnt, self.forearm_fk_rigJnt)
        mc.parent(self.forearm_fk_rigJnt, self.uparm_fk_rigJnt)
        mc.parent(self.uparm_fk_rigJnt, self.armJnt_fk_grp)

        #-- Fk Create controls
        self.uparm_fk_ctrl = util.controller('UpArm{}Fk{}Ctrl'.format(part, side), 'circle', 'red')
        self.uparm_fk_gmbl = util.gimbal(self.uparm_fk_ctrl)
        self.uparm_fk_zro = util.group(self.uparm_fk_ctrl, 'Zro')
        self.uparm_fk_zro.snap(uparm_tmpJnt)

        self.forearm_fk_ctrl = util.controller('Forearm{}Fk{}Ctrl'.format(part, side), 'circle', 'red')
        self.forearm_fk_gmbl = util.gimbal(self.forearm_fk_ctrl)
        self.forearm_fk_zro = util.group(self.forearm_fk_ctrl, 'Zro')
        self.forearm_fk_zro.snap(forearm_tmpJnt)

        self.wrist_fk_ctrl = util.controller('Wrist{}Fk{}Ctrl'.format(part, side), 'circle', 'red')
        self.wrist_fk_gmbl = util.gimbal(self.wrist_fk_ctrl)
        self.wrist_fk_zro = util.group(self.wrist_fk_ctrl, 'Zro')
        self.wrist_fk_zro.snap(wrist_tmpJnt)

        mc.parent(self.wrist_fk_zro, self.forearm_fk_gmbl)
        mc.parent(self.forearm_fk_zro, self.uparm_fk_gmbl)
        mc.parent(self.uparm_fk_zro, self.armCtrl_fk_grp)

        #-- Fk Set rotate order
        for __each in (self.uparm_fk_rigJnt, self.forearm_fk_rigJnt, self.wrist_fk_rigJnt, self.hand_fk_rigJnt,
                      self.uparm_fk_ctrl, self.forearm_fk_ctrl, self.wrist_fk_ctrl):
            __each.rotate_order = rotate_order

        #-- Fk Rig process
        util.parent_constraint( self.uparm_fk_gmbl, 
                                self.uparm_fk_rigJnt, 
                                mo = False )
        
        util.parent_constraint( self.forearm_fk_gmbl, 
                                self.forearm_fk_rigJnt, 
                                mo = False )
        
        util.parent_constraint( self.wrist_fk_gmbl, 
                                self.wrist_fk_rigJnt, 
                                mo = False )

        self.uparm_fk_stretch = util.add_offset_controller(self.uparm_fk_ctrl, self.forearm_fk_zro, 'stretch', aim_axis, side_value)
        self.forearm_fk_stretch = util.add_offset_controller(self.forearm_fk_ctrl, self.wrist_fk_zro, 'stretch', aim_axis, side_value)

        self.uparm_fk_locWor = util.local_world(self.uparm_fk_ctrl, ctrl_grp, self.armCtrl_fk_grp, self.uparm_fk_zro, 'orient')
        self.uparm_fk_ctrl.attr('localWorld').value = 1

        #-- Fk Cleanup
        for __ctrl in (self.uparm_fk_ctrl, self.forearm_fk_ctrl, self.wrist_fk_ctrl):
            __ctrl.lock_hide('sx', 'sy', 'sz', 'v')

        #-- Ik
        #-- Ik Create main group
        self.armCtrl_ik_grp = node.Transform('Arm{}IkCtrl{}Grp'.format(part, side))
        self.armJnt_ik_grp = node.Transform('Arm{}IkJnt{}Grp'.format(part, side))

        self.armCtrl_ik_grp.snap(uparm_tmpJnt)
        self.armJnt_ik_grp.snap(uparm_tmpJnt)

        mc.parent(self.armCtrl_ik_grp, self.armScl_grp)
        mc.parent(self.armJnt_ik_grp, self.armJnt_grp)

        #-- Ik Create rig joint
        self.uparm_ik_rigJnt = node.Joint('UpArm{}Ik{}RigJnt'.format(part, side), position = uparm_tmpJnt)
        self.forearm_ik_rigJnt = node.Joint('Forearm{}Ik{}RigJnt'.format(part, side), position = forearm_tmpJnt)
        self.wrist_ik_rigJnt = node.Joint('Wrist{}Ik{}RigJnt'.format(part, side), position = wrist_tmpJnt)
        self.hand_ik_rigJnt = node.Joint('Hand{}Ik{}RigJnt'.format(part, side), position = hand_tmpJnt)

        mc.parent(self.hand_ik_rigJnt, self.wrist_ik_rigJnt)
        mc.parent(self.wrist_ik_rigJnt, self.forearm_ik_rigJnt)
        mc.parent(self.forearm_ik_rigJnt, self.uparm_ik_rigJnt)
        mc.parent(self.uparm_ik_rigJnt, self.armJnt_ik_grp)

        #-- Ik create controls
        self.uparm_ik_ctrl = util.controller('UpArm{}Ik{}Ctrl'.format(part, side), 'cube', 'blue', jnt = True)
        self.uparm_ik_gmbl = util.gimbal(self.uparm_ik_ctrl)
        self.uparm_ik_zro = util.group(self.uparm_ik_ctrl, 'Zro')
        self.uparm_ik_zro.snap_point(uparm_tmpJnt)
        self.uparm_ik_ctrl.snap_joint_orient(uparm_tmpJnt)

        self.wrist_ik_ctrl = util.controller('Wrist{}Ik{}Ctrl'.format(part, side), 'square', 'blue', jnt = True)
        self.wrist_ik_gmbl = util.gimbal(self.wrist_ik_ctrl)
        self.wrist_ik_zro = util.group(self.wrist_ik_ctrl, 'Zro')
        self.wrist_ik_zro.snap_point(wrist_tmpJnt)
        self.wrist_ik_ctrl.snap_joint_orient(wrist_tmpJnt)

        self.elbow_ik_ctrl = util.controller('Elbow{}Ik{}Ctrl'.format(part, side), 'sphere', 'blue', jnt = True)
        self.elbow_ik_zro = util.group(self.elbow_ik_ctrl, 'Zro')
        self.elbow_ik_zro.snap_point(elbow_tmpJnt)

        mc.parent(self.uparm_ik_zro, self.wrist_ik_zro, self.armCtrl_ik_grp)

        #-- Ik prepare non flip elbow
        self.pole_ik_grp = node.Transform('Elbow{}IkPole{}Grp'.format(part, side))
        self.poleUpvec_ik_grp = node.Transform('Elbow{}IkPoleUpvec{}Grp'.format(part, side))
        self.poleAim_ik_grp = node.Transform('Elbow{}IkPoleAim{}Grp'.format(part, side))
        self.poleRotate_ik_grp = node.Transform('Elbow{}IkPoleRotate{}Grp'.format(part, side))
        
        self.pole_ik_grp.snap(wrist_tmpJnt)
        self.poleUpvec_ik_grp.snap(uparm_tmpJnt)
        self.poleAim_ik_grp.snap(wrist_tmpJnt)
        self.poleRotate_ik_grp.snap(wrist_tmpJnt)

        mc.parent(self.elbow_ik_zro, self.pole_ik_grp)
        mc.parent(self.poleRotate_ik_grp, self.poleAim_ik_grp)
        mc.parent(self.pole_ik_grp, self.poleUpvec_ik_grp, self.poleAim_ik_grp, self.armCtrl_ik_grp)

        #-- Ik Adjust shape controls
        self.elbow_ik_ctrl.scale_shape(0.5)

        #-- Ik Set rotate order
        for __each in (self.uparm_ik_rigJnt, self.forearm_ik_rigJnt, self.wrist_ik_rigJnt, self.hand_ik_rigJnt,
                      self.uparm_ik_ctrl, self.wrist_ik_ctrl):
            __each.rotate_order = rotate_order

        #-- Ik Rig process
        self.elbow_ik_locWor = util.local_world(self.elbow_ik_ctrl, ctrl_grp, self.wrist_ik_ctrl, self.pole_ik_grp, 'parent')
        self.wrist_ik_locWor = util.local_world(self.wrist_ik_ctrl, ctrl_grp, self.armCtrl_ik_grp, self.wrist_ik_zro, 'parent')
        
        self.wrist_ik_ctrl.attr('localWorld').value = 1

        elbow_local = self.elbow_ik_locWor[3]

        util.parent_constraint( parent,
                                self.uparm_ik_zro,
                                mo = True )
        
        util.point_constraint( self.uparm_ik_gmbl,
                               self.uparm_ik_rigJnt,
                               mo = False )
        
        util.point_constraint( self.wrist_ik_gmbl,
                               self.poleAim_ik_grp,
                               mo = True )
        
        util.parent_constraint( self.poleRotate_ik_grp,
                                elbow_local,
                                mo = True )
        
        util.orient_constraint( ctrl_grp,
                                self.poleUpvec_ik_grp,
                                mo = True )
        
        util.aim_constraint( self.uparm_ik_rigJnt,
                             self.poleAim_ik_grp,
                             aim = elbow_aimvec,
                             u = elbow_upvec,
                             wut ='objectrotation',
                             wuo = self.poleUpvec_ik_grp,
                             wu= (1,0,0),
                             mo = True )
        
        #-- Ik Add curve guide
        curve_guide, curve_grp = util.curve_guide(self.elbow_ik_ctrl, self.forearm_ik_rigJnt)
        mc.parent(curve_grp, self.armCtrl_ik_grp)

        #-- Ik Add ikhandle
        self.wrist_ikh, wrist_eff = util.add_ikhandle('Wrist{}'.format(part),
                                                      'ikRPsolver',
                                                       self.uparm_ik_rigJnt,
                                                       self.wrist_ik_rigJnt)
        
        self.hand_ikh, hand_eff = util.add_ikhandle('Hand{}'.format(part),
                                                    'ikSCsolver',
                                                     self.wrist_ik_rigJnt,
                                                     self.hand_ik_rigJnt)
        
        mc.parent(self.wrist_ikh, self.hand_ikh, self.wrist_ik_gmbl)
        mc.poleVectorConstraint(self.elbow_ik_ctrl, self.wrist_ikh)

        #-- Ik Setup twist
        self.wrist_ik_ctrl.add_attr('twist')
        self.wrist_ik_ctrl.attr('twist') >> self.wrist_ikh.attr('twist')

        #-- Ik Setup stretchy
        self.ik_dist_grp,\
        self.ik_dist_start_grp,\
        self.ik_dist_end_grp,\
        self.dist = util.add_stretchy_ik_chain( controller = self.wrist_ik_ctrl,
                                                joint = [self.uparm_ik_rigJnt, 
                                                         self.forearm_ik_rigJnt, 
                                                         self.wrist_ik_rigJnt],
                                                part = 'Arm{}'.format(part),
                                                controller_pin = self.elbow_ik_ctrl )

        mc.parent(self.ik_dist_grp, self.armCtrl_ik_grp)
        
        #-- Ik Cleanup
        for __ctrl in (self.uparm_ik_ctrl, self.elbow_ik_ctrl):
            __ctrl.lock_hide('rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v')

        self.wrist_ik_ctrl.lock_hide('sx', 'sy', 'sz', 'v')

        #-- Blending Fk Ik
        self.arm_ctrl.add_attr('fkIk', min = 0, max = 1)

        self.uparm_blend = util.translate_rotate_blend( self.arm_ctrl.attr('fkIk'),
                                                        self.uparm_fk_rigJnt,
                                                        self.uparm_ik_rigJnt,
                                                        self.uparm_rigJnt )

        self.forearm_blend = util.translate_rotate_blend( self.arm_ctrl.attr('fkIk'),
                                                          self.forearm_fk_rigJnt,
                                                          self.forearm_ik_rigJnt,
                                                          self.forearm_rigJnt )
        
        self.wrist_blend = util.translate_rotate_blend( self.arm_ctrl.attr('fkIk'),
                                                        self.wrist_fk_rigJnt,
                                                        self.wrist_ik_rigJnt,
                                                        self.wrist_rigJnt )
        
        self.uparm_blend.name = 'UpArm{}FkIk{}Blend'.format(part, side)
        self.forearm_blend.name = 'Forerm{}FkIk{}Blend'.format(part, side)
        self.wrist_blend.name = 'Wrist{}FkIk{}Blend'.format(part, side)

        self.fkIk_rev = node.Reverse('Arm{}FkIk{}Rev'.format(part, side))
        self.arm_ctrl.attr('fkIk') >> self.armCtrl_ik_grp.attr('v')
        self.arm_ctrl.attr('fkIk') >> self.fkIk_rev.attr('ix')
        self.fkIk_rev.attr('ox') >> self.armCtrl_fk_grp.attr('v')

        #-- Setup arm scale
        self.arm_ctrl.add_attr('armScale', dv = 1)
        self.forearm_jnt.attr('ssc').value = 0
        
        for __attr in 'xyz':
            self.arm_ctrl.attr('armScale') >> self.armScl_grp.attr('s{}'.format(__attr))
            self.arm_ctrl.attr('armScale') >> self.uparm_jnt.attr('s{}'.format(__attr))

        #-- Setup hand scale
        self.arm_ctrl.add_attr('handScale', dv = 1)
        self.hand_jnt.attr('ssc').value = 0

        for __attr in 'xyz':
            self.arm_ctrl.attr('handScale') >> self.wrist_rigJnt.attr('s{}'.format(__attr))
            self.arm_ctrl.attr('handScale') >> self.wrist_fk_rigJnt.attr('s{}'.format(__attr))
            self.arm_ctrl.attr('handScale') >> self.wrist_jnt.attr('s{}'.format(__attr))
        
        #-- Additional ribbon
        if ribbon:
            #-- Create ribbon group
            self.armRbn_ctrl_grp = node.Transform('Arm{}RbnCtrl{}Grp'.format(part, side))
            self.armRbn_still_grp = node.Transform('Arm{}RbnStill{}Grp'.format(part, side))

            mc.parent(self.armRbn_ctrl_grp, self.armScl_grp)
            mc.parent(self.armRbn_still_grp, still_grp)

            #-- Create ribbon controls 
            self.arm_rbn_ctrl = util.controller('Arm{}Rbn{}Ctrl'.format(part, side), 'plus', 'yellow')
            self.arm_rbn_zro = util.group(self.arm_rbn_ctrl, 'Zro')
            self.arm_rbn_zro.snap(forearm_tmpJnt)
            mc.parent(self.arm_rbn_zro, self.armScl_grp)

            self.arm_rbn_ctrl.lock_hide('rx', 'ry', 'rz', 's{}'.format(aim_axis[0]), 'v')

            #-- Adjust shape controls
            self.arm_rbn_ctrl.scale_shape(0.7)

            #-- Rig process
            util.parent_constraint( self.forearm_jnt,
                                    self.arm_rbn_zro,
                                    mo = True )
            
            uparm_dist = util.distance_between(util.get_position(self.uparm_jnt),
                                               util.get_position(self.forearm_jnt))
            
            forearm_dist = util.distance_between(util.get_position(self.forearm_jnt),
                                                 util.get_position(self.wrist_jnt))
            
            #-- UpArm ribbon
            self.uparm_rbn = rbn.Ribbon( name = 'UpArm{}'.format(part),
                                         axis = axis,
                                         side = side,
                                         dist = uparm_dist,
                                         subdiv = 1 )
            
            self.uparm_rbn.rbnCtrl_grp.snap(self.uparm_jnt)
            
            util.parent_constraint( self.uparm_jnt,
                                    self.uparm_rbn.rbnCtrl_grp,
                                    mo = True )
            
            util.parent_constraint( self.uparm_jnt,
                                    self.uparm_rbn.rbn_root_ctrl,
                                    mo = True )
            
            util.parent_constraint( self.arm_rbn_ctrl,
                                    self.uparm_rbn.rbn_end_ctrl,
                                    mo = True )

            #-- Forearm ribbon
            self.forearm_rbn = rbn.Ribbon( name = 'Forearm{}'.format(part),
                                           axis = axis,
                                           side = side,
                                           dist = forearm_dist,
                                           subdiv = 1 )
            
            self.forearm_rbn.rbnCtrl_grp.snap(self.forearm_jnt)
            
            util.parent_constraint( self.forearm_jnt,
                                    self.forearm_rbn.rbnCtrl_grp,
                                    mo = True )
            
            util.parent_constraint( self.arm_rbn_ctrl,
                                    self.forearm_rbn.rbn_root_ctrl,
                                    mo = True )
            
            util.parent_constraint( self.wrist_jnt,
                                    self.forearm_rbn.rbn_end_ctrl,
                                    mo = True )
            
            #-- Setup scale
            for __ax in sqsh_axis:
                ax_attr = 's{}'.format(__ax)
                self.arm_rbn_ctrl.attr(ax_attr) >> self.uparm_rbn.rbn_end_ctrl.attr(ax_attr)
                self.arm_rbn_ctrl.attr(ax_attr) >> self.forearm_rbn.rbn_root_ctrl.attr(ax_attr)
            
            #-- Cleanup
            for __ctrl in (self.uparm_rbn.rbn_root_ctrl, self.uparm_rbn.rbn_end_ctrl,
                          self.forearm_rbn.rbn_root_ctrl, self.forearm_rbn.rbn_end_ctrl):
                __ctrl.lock_hide('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 's{}'.format(sqsh_axis[0]), 's{}'.format(sqsh_axis[1]))
                __ctrl.get_parent().hide()

            #-- Adjust ribbon
            self.uparm_rbn.rbn_ctrl.shape.attr('rootTwistAmp').value = -1
            self.forearm_rbn.rbn_ctrl.shape.attr('rootTwistAmp').value = -1

            self.uparm_rbn.rbn_ctrl.attr('autoTwist').value = 1
            self.forearm_rbn.rbn_ctrl.attr('autoTwist').value = 1

            #-- Setup twist
            self.uparm_nonroll_jnt[0].attr('twist') >> self.uparm_rbn.rbn_ctrl.shape.attr('rootAbsTwist')
            self.wrist_jnt.attr('ry') >> self.forearm_rbn.rbn_ctrl.shape.attr('endAbsTwist')
            
            #-- Manage hierarchy
            mc.parent(self.uparm_rbn.rbnSkin_grp, self.uparm_jnt)
            mc.parent(self.forearm_rbn.rbnSkin_grp, self.forearm_jnt)
            
            mc.parent(self.uparm_rbn.rbnCtrl_grp, self.forearm_rbn.rbnCtrl_grp, self.armRbn_ctrl_grp)
            mc.parent(self.uparm_rbn.rbnStill_grp, self.forearm_rbn.rbnStill_grp, self.armRbn_still_grp)
    
    mc.select(cl = True)