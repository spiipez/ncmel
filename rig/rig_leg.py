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

class Leg(object):

    def __init__( self , upleg_tmpJnt = 'UpLeg_L_TmpJnt',
                         lowleg_tmpJnt = 'LowLeg_L_TmpJnt',
                         ankle_tmpJnt = 'Ankle_L_TmpJnt',
                         ball_tmpJnt = 'Ball_L_TmpJnt',
                         toe_tmpJnt = 'Toe_L_TmpJnt',
                         heel_tmpJnt = 'Heel_L_TmpJnt',
                         footIn_tmpJnt = 'FootIn_L_TmpJnt',
                         footOut_tmpJnt = 'FootOut_L_TmpJnt',
                         knee_tmpJnt = 'Knee_L_TmpJnt',
                         footSmart_tmpJnt = 'FootSmart_L_TmpJnt',
                         parent = 'Pelvis_Jnt', 
                         ctrl_grp = 'Ctrl_Grp',
                         still_grp = 'Still_Grp',
                         part = '',
                         side = 'L',
                         ribbon = True,
                         foot = True,
                         footSmart = False,
                         scapular = False
                ):
        
        '''
        '''
        
        ##-- Prepare
        part = part.capitalize()
        side = util.set_side(side)
        rotate_order = 'yzx'

        side_value = 1
        axis = 'y+'
        upvec = (0, 0, 1)
        knee_aimvec = (0, -1, 0)
        knee_upvec = (1, 0, 0)

        if 'R' in side:
            side_value = -1
            axis = 'y-'
            upvec = (0, 0, -1)
            knee_aimvec = (0, 1, 0)
            knee_upvec = (-1, 0, 0)

        aim_axis = axis[0]
        sqsh_axis = 'xyz'.replace(aim_axis,'')

        #-- Create main group
        self.legCtrl_grp = node.Transform('Leg{}Ctrl{}Grp'.format(part, side))
        self.legScl_grp = node.Transform('Leg{}Scl{}Grp'.format(part, side))
        self.legJnt_grp = node.Transform('Leg{}Jnt{}Grp'.format(part, side))
        self.legRigJnt_grp = node.Transform('Leg{}RigJnt{}Grp'.format(part, side))
        
        self.legCtrl_grp.snap(parent)
        self.legScl_grp.snap(upleg_tmpJnt)
        self.legJnt_grp.snap(upleg_tmpJnt)
        self.legRigJnt_grp.snap(upleg_tmpJnt)

        mc.parent(self.legRigJnt_grp, self.legJnt_grp)
        mc.parent(self.legJnt_grp, self.legScl_grp)
        mc.parent(self.legScl_grp, self.legCtrl_grp)
        mc.parent(self.legCtrl_grp, ctrl_grp)

        #-- Create joint
        self.upleg_jnt = node.Joint('UpLeg{}{}Jnt'.format(part, side), position = upleg_tmpJnt)
        self.lowleg_jnt = node.Joint('LowLeg{}{}Jnt'.format(part, side), position = lowleg_tmpJnt)
        self.ankle_jnt = node.Joint('Ankle{}{}Jnt'.format(part, side), position = ankle_tmpJnt)

        mc.parent(self.ankle_jnt, self.lowleg_jnt)
        mc.parent(self.lowleg_jnt, self.upleg_jnt)
        mc.parent(self.upleg_jnt, parent)

        #-- Create rig joint
        self.upleg_rigJnt = node.Joint('UpLeg{}{}RigJnt'.format(part, side), position = upleg_tmpJnt)
        self.lowleg_rigJnt = node.Joint('LowLeg{}{}RigJnt'.format(part, side), position = lowleg_tmpJnt)
        self.ankle_rigJnt = node.Joint('Ankle{}{}RigJnt'.format(part, side), position = ankle_tmpJnt)

        mc.parent(self.ankle_rigJnt, self.lowleg_rigJnt)
        mc.parent(self.lowleg_rigJnt, self.upleg_rigJnt)
        mc.parent(self.upleg_rigJnt, self.legRigJnt_grp)

        #-- Set rotate order
        for __jnt in (self.upleg_jnt, self.lowleg_jnt, self.ankle_jnt, 
                      self.upleg_rigJnt, self.lowleg_rigJnt, self.ankle_rigJnt):
            __jnt.rotate_order = rotate_order

        #-- Rig process
        util.parent_constraint(self.upleg_rigJnt, self.upleg_jnt, mo = False)
        util.parent_constraint(self.lowleg_rigJnt, self.lowleg_jnt, mo = False)
        util.parent_constraint(self.ankle_rigJnt, self.ankle_jnt, mo = False)

        self.ankle_rigJnt.attr('s') >> self.ankle_jnt.attr('s')

        if foot:
            #-- Create joint
            self.ball_jnt = node.Joint('Ball{}{}Jnt'.format(part, side), position = ball_tmpJnt)
            self.toe_jnt = node.Joint('Toe{}{}Jnt'.format(part, side), position = toe_tmpJnt)

            mc.parent(self.toe_jnt, self.ball_jnt)
            mc.parent(self.ball_jnt, self.ankle_jnt)

            #-- Create rig joint
            self.ball_rigJnt = node.Joint('Ball{}{}RigJnt'.format(part, side), position = ball_tmpJnt)
            self.toe_rigJnt = node.Joint('Toe{}{}RigJnt'.format(part, side), position = toe_tmpJnt)

            mc.parent(self.toe_rigJnt, self.ball_rigJnt)
            mc.parent(self.ball_rigJnt, self.ankle_rigJnt)
            
            #-- Set rotate order
            for _jnt in (self.ball_jnt, self.toe_jnt,
                         self.ball_rigJnt, self.toe_rigJnt):
                _jnt.rotate_order = rotate_order

            #-- Rig process
            util.parent_constraint(self.ball_rigJnt, self.ball_jnt, mo = False)
            util.parent_constraint(self.toe_rigJnt, self.toe_jnt, mo = False)
            
        #-- Create main controls
        self.leg_ctrl = util.controller('Leg{}{}Ctrl'.format(part, side), 'stickSphere', 'green')
        self.leg_zro = util.group(self.leg_ctrl, 'Zro')
        
        mc.parent(self.leg_zro, self.legScl_grp)

        util.parent_constraint(self.ankle_jnt, self.leg_zro, mo = False)

        #-- Adjust shape controls
        if 'L' in side:
            self.leg_ctrl.rotate_shape((-90, 0, 0))
        else:
            self.leg_ctrl.rotate_shape((90, 0, 0))

        #-- Rig process
        self.upleg_nonroll_jnt = util.add_non_roll_joint(self.upleg_jnt, aim_axis)
        self.lowleg_nonroll_jnt = util.add_non_roll_joint(self.lowleg_jnt, aim_axis)

        #-- Cleanup
        self.leg_ctrl.lhtrs()
        self.leg_ctrl.lhv()
        self.legJnt_grp.hide()

        #-- Fk
        #-- Fk Create main group
        self.legCtrl_fk_grp = node.Transform('Leg{}FkCtrl{}Grp'.format(part, side))
        self.legJnt_fk_grp = node.Transform('Leg{}FkJnt{}Grp'.format(part, side))

        self.legCtrl_fk_grp.snap(upleg_tmpJnt)
        self.legJnt_fk_grp.snap(upleg_tmpJnt)

        mc.parent(self.legCtrl_fk_grp, self.legScl_grp)
        mc.parent(self.legJnt_fk_grp, self.legJnt_grp)

        util.parent_constraint(parent, self.legCtrl_fk_grp)

        #-- Fk Create rig joint
        self.upleg_fk_rigJnt = node.Joint('UpLeg{}Fk{}RigJnt'.format(part, side), position = upleg_tmpJnt)
        self.lowleg_fk_rigJnt = node.Joint('LowLeg{}Fk{}RigJnt'.format(part, side), position = lowleg_tmpJnt)
        self.ankle_fk_rigJnt = node.Joint('Ankle{}Fk{}RigJnt'.format(part, side), position = ankle_tmpJnt)

        mc.parent(self.ankle_fk_rigJnt, self.lowleg_fk_rigJnt)
        mc.parent(self.lowleg_fk_rigJnt, self.upleg_fk_rigJnt)
        mc.parent(self.upleg_fk_rigJnt, self.legJnt_fk_grp)

        #-- Fk Create controls
        self.upleg_fk_ctrl = util.controller('UpLeg{}Fk{}Ctrl'.format(part, side), 'circle', 'red')
        self.upleg_fk_gmbl = util.gimbal(self.upleg_fk_ctrl)
        self.upleg_fk_zro = util.group(self.upleg_fk_ctrl, 'Zro')
        self.upleg_fk_zro.snap(upleg_tmpJnt)

        self.lowleg_fk_ctrl = util.controller('LowLeg{}Fk{}Ctrl'.format(part, side), 'circle', 'red')
        self.lowleg_fk_gmbl = util.gimbal(self.lowleg_fk_ctrl)
        self.lowleg_fk_zro = util.group(self.lowleg_fk_ctrl, 'Zro')
        self.lowleg_fk_zro.snap(lowleg_tmpJnt)

        self.ankle_fk_ctrl = util.controller('Ankle{}Fk{}Ctrl'.format(part, side), 'circle', 'red')
        self.ankle_fk_gmbl = util.gimbal(self.ankle_fk_ctrl)
        self.ankle_fk_zro = util.group(self.ankle_fk_ctrl, 'Zro')
        self.ankle_fk_zro.snap(ankle_tmpJnt)

        mc.parent(self.ankle_fk_zro, self.lowleg_fk_gmbl)
        mc.parent(self.lowleg_fk_zro, self.upleg_fk_gmbl)
        mc.parent(self.upleg_fk_zro, self.legCtrl_fk_grp)

        #-- Fk Set rotate order
        for __each in (self.upleg_fk_rigJnt, self.lowleg_fk_rigJnt, self.ankle_fk_rigJnt,
                      self.upleg_fk_ctrl, self.lowleg_fk_ctrl, self.ankle_fk_ctrl):
            __each.rotate_order = rotate_order

        #-- Fk Rig process
        util.parent_constraint( self.upleg_fk_gmbl, 
                                self.upleg_fk_rigJnt, 
                                mo = False )
        
        util.parent_constraint( self.lowleg_fk_gmbl, 
                                self.lowleg_fk_rigJnt, 
                                mo = False )
        
        util.parent_constraint( self.ankle_fk_gmbl, 
                                self.ankle_fk_rigJnt, 
                                mo = False )

        self.upleg_fk_stretch = util.add_offset_controller(self.upleg_fk_ctrl, self.lowleg_fk_zro, 'stretch', aim_axis, side_value)
        self.lowleg_fk_stretch = util.add_offset_controller(self.lowleg_fk_ctrl, self.ankle_fk_zro, 'stretch', aim_axis, side_value)
        
        self.upleg_fk_locWor = util.local_world(self.upleg_fk_ctrl, ctrl_grp, self.legCtrl_fk_grp, self.upleg_fk_zro, 'orient')
        self.upleg_fk_ctrl.attr('localWorld').value = 1

        #-- Fk Cleanup
        for __ctrl in (self.upleg_fk_ctrl, self.lowleg_fk_ctrl, self.ankle_fk_ctrl):
            __ctrl.lock_hide('sx', 'sy', 'sz', 'v')

        if foot:
            #-- Fk Foot Create rig joint
            self.ball_fk_rigJnt = node.Joint('Ball{}Fk{}RigJnt'.format(part, side), position = ball_tmpJnt)
            self.toe_fk_rigJnt = node.Joint('Toe{}Fk{}RigJnt'.format(part, side), position = toe_tmpJnt)

            mc.parent(self.toe_fk_rigJnt, self.ball_fk_rigJnt)
            mc.parent(self.ball_fk_rigJnt, self.ankle_fk_rigJnt)

            #-- Fk Foot Create controls
            self.ball_fk_ctrl = util.controller('Ball{}Fk{}Ctrl'.format(part, side), 'circle', 'red')
            self.ball_fk_gmbl = util.gimbal(self.ball_fk_ctrl)
            self.ball_fk_scl = util.group(self.ball_fk_ctrl, 'Scl')
            self.ball_fk_zro = util.group(self.ball_fk_ctrl, 'Zro')
            self.ball_fk_scl.snap(ankle_tmpJnt)
            self.ball_fk_zro.snap(ball_tmpJnt)

            mc.parent(self.ball_fk_scl, self.ankle_fk_gmbl)

            #-- Fk Foot Set rotate order
            for __each in (self.ball_fk_rigJnt, self.toe_fk_rigJnt, self.ball_fk_ctrl):
                __each.rotate_order = rotate_order

            #-- Fk Foot Rig process
            util.parent_constraint( self.ball_fk_gmbl, 
                                    self.ball_fk_rigJnt, 
                                    mo = False )
            
            self.ball_fk_stretch = util.add_offset_controller(self.ball_fk_ctrl, self.toe_fk_rigJnt, 'stretch', aim_axis, side_value)
        
            #-- Fk Foot Cleanup
            self.ball_fk_ctrl.lock_hide('sx', 'sy', 'sz', 'v')

        #-- Ik
        #-- Ik Create main group
        self.legCtrl_ik_grp = node.Transform('Leg{}IkCtrl{}Grp'.format(part, side))
        self.legJnt_ik_grp = node.Transform('Leg{}IkJnt{}Grp'.format(part, side))

        self.legCtrl_ik_grp.snap(upleg_tmpJnt)
        self.legJnt_ik_grp.snap(upleg_tmpJnt)

        mc.parent(self.legCtrl_ik_grp, self.legScl_grp)
        mc.parent(self.legJnt_ik_grp, self.legJnt_grp)

        #-- Ik Create rig joint
        self.upleg_ik_rigJnt = node.Joint('UpLeg{}Ik{}RigJnt'.format(part, side), position = upleg_tmpJnt)
        self.lowleg_ik_rigJnt = node.Joint('LowLeg{}Ik{}RigJnt'.format(part, side), position = lowleg_tmpJnt)
        self.ankle_ik_rigJnt = node.Joint('Ankle{}Ik{}RigJnt'.format(part, side), position = ankle_tmpJnt)

        mc.parent(self.ankle_ik_rigJnt, self.lowleg_ik_rigJnt)
        mc.parent(self.lowleg_ik_rigJnt, self.upleg_ik_rigJnt)
        mc.parent(self.upleg_ik_rigJnt, self.legJnt_ik_grp)

        #-- Ik Create controls
        self.upleg_ik_ctrl = util.controller('UpLeg{}Ik{}Ctrl'.format(part, side), 'cube', 'blue', jnt = True)
        self.upleg_ik_gmbl = util.gimbal(self.upleg_ik_ctrl)
        self.upleg_ik_zro = util.group(self.upleg_ik_ctrl, 'Zro')
        self.upleg_ik_zro.snap_point(upleg_tmpJnt)
        self.upleg_ik_ctrl.snap_joint_orient(upleg_tmpJnt)

        self.ankle_ik_ctrl = util.controller('Ankle{}Ik{}Ctrl'.format(part, side), 'cube', 'blue', jnt = True)
        self.ankle_ik_gmbl = util.gimbal(self.ankle_ik_ctrl)
        self.ankle_ik_zro = util.group(self.ankle_ik_ctrl, 'Zro')
        self.ankle_ik_zro.snap_point(ankle_tmpJnt)
        self.ankle_ik_ctrl.snap_joint_orient(ankle_tmpJnt)

        self.knee_ik_ctrl = util.controller('Knee{}Ik{}Ctrl'.format(part, side), 'sphere', 'blue', jnt = True)
        self.knee_ik_zro = util.group(self.knee_ik_ctrl, 'Zro')
        self.knee_ik_zro.snap_point(knee_tmpJnt)

        mc.parent(self.upleg_ik_zro, self.ankle_ik_zro, self.legCtrl_ik_grp)

        #-- Ik Prepare non flip knee
        self.pole_ik_grp = node.Transform('Knee{}IkPole{}Grp'.format(part, side))
        self.poleUpvec_ik_grp = node.Transform('Knee{}IkPoleUpvec{}Grp'.format(part, side))
        self.poleAim_ik_grp = node.Transform('Knee{}IkPoleAim{}Grp'.format(part, side))
        self.poleRotate_ik_grp = node.Transform('Knee{}IkPoleRotate{}Grp'.format(part, side))
        
        self.pole_ik_grp.snap(ankle_tmpJnt)
        self.poleUpvec_ik_grp.snap(upleg_tmpJnt)
        self.poleAim_ik_grp.snap(ankle_tmpJnt)
        self.poleRotate_ik_grp.snap(ankle_tmpJnt)

        mc.parent(self.knee_ik_zro, self.pole_ik_grp)
        mc.parent(self.poleRotate_ik_grp, self.poleAim_ik_grp)
        mc.parent(self.pole_ik_grp, self.poleUpvec_ik_grp, self.poleAim_ik_grp, self.legCtrl_ik_grp)

        #-- Ik Adjust shape controls
        self.knee_ik_ctrl.scale_shape(0.5)

        #-- Ik Set rotate order
        for __each in (self.upleg_ik_rigJnt, self.lowleg_ik_rigJnt, self.ankle_ik_rigJnt,
                       self.upleg_ik_ctrl, self.ankle_ik_ctrl):
            __each.rotate_order = rotate_order

        #-- Ik Rig process
        self.knee_ik_locWor = util.local_world(self.knee_ik_ctrl, ctrl_grp, self.ankle_ik_ctrl, self.pole_ik_grp, 'parent')
        knee_local = self.knee_ik_locWor[3]

        if scapular:
            #-- Prepare for scapular
            self.ankle_ik_locWor = False
            util.parent_constraint( ctrl_grp, 
                                    self.ankle_ik_zro, 
                                    mo = True )
        else:
            self.ankle_ik_locWor = util.local_world(self.ankle_ik_ctrl, ctrl_grp, self.upleg_ik_gmbl, self.ankle_ik_zro, 'parent')
            self.ankle_ik_ctrl.attr('localWorld').value = 1

        util.parent_constraint( parent,
                                self.upleg_ik_zro,
                                mo = True )
        
        util.point_constraint( self.upleg_ik_gmbl,
                               self.upleg_ik_rigJnt,
                               mo = False )
        
        util.point_constraint( self.ankle_ik_gmbl,
                               self.poleAim_ik_grp,
                               mo = True )
        
        util.parent_constraint( self.poleRotate_ik_grp,
                                knee_local,
                                mo = True )
        
        util.orient_constraint( ctrl_grp,
                                self.poleUpvec_ik_grp,
                                mo = True )
        
        util.aim_constraint( self.upleg_ik_rigJnt,
                             self.poleAim_ik_grp,
                             aim = knee_aimvec,
                             u = knee_upvec,
                             wut ='objectrotation',
                             wuo = self.poleUpvec_ik_grp,
                             wu = (1,0,0),
                             mo = True )

        #-- Ik Add curve guide
        curve_guide, curve_grp = util.curve_guide(self.knee_ik_ctrl, self.lowleg_ik_rigJnt)
        mc.parent(curve_grp, self.legCtrl_ik_grp)

        #-- Ik Add ikhandle
        self.ankle_ikh, ankle_eff = util.add_ikhandle('Ankle{}'.format(part),
                                                      'ikRPsolver',
                                                       self.upleg_ik_rigJnt,
                                                       self.ankle_ik_rigJnt)
        
        mc.parent(self.ankle_ikh, self.ankle_ik_gmbl)
        mc.poleVectorConstraint(self.knee_ik_ctrl, self.ankle_ikh)

        #-- Ik Setup twist
        self.ankle_ik_ctrl.add_attr('twist')
        self.ankle_ik_ctrl.attr('twist') >> self.ankle_ikh.attr('twist')

        #-- Ik Setup stretchy
        self.ik_dist_grp,\
        self.ik_dist_start_grp,\
        self.ik_dist_end_grp,\
        self.dist = util.add_stretchy_ik_chain( controller = self.ankle_ik_ctrl,
                                                joint = [self.upleg_ik_rigJnt, 
                                                         self.lowleg_ik_rigJnt, 
                                                         self.ankle_ik_rigJnt],
                                                part = 'Leg{}'.format(part),
                                                controller_pin = self.knee_ik_ctrl )

        mc.parent(self.ik_dist_grp, self.legCtrl_ik_grp)

        #-- Setup non flip knee
        self.kneePoleRy_ik_add = node.AddDoubleLinear('Knee{}IkPoleRy{}Add'.format(part, side))
        self.kneePoleRz_ik_add = node.AddDoubleLinear('Knee{}IkPoleRz{}Add'.format(part, side))

        self.ankle_ik_ctrl.attr('ry') >> self.kneePoleRy_ik_add.attr('i1')
        self.ankle_ik_gmbl.attr('ry') >> self.kneePoleRy_ik_add.attr('i2')

        self.ankle_ik_ctrl.attr('rz') >> self.kneePoleRz_ik_add.attr('i1')
        self.ankle_ik_gmbl.attr('rz') >> self.kneePoleRz_ik_add.attr('i2')
        
        self.kneePoleRy_ik_add.attr('o') >> self.poleRotate_ik_grp.attr('ry')
        self.kneePoleRz_ik_add.attr('o') >> self.poleRotate_ik_grp.attr('rz')

        #-- Ik Cleanup
        for __ctrl in (self.upleg_ik_ctrl, self.knee_ik_ctrl):
            __ctrl.lock_hide('rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v')

        self.ankle_ik_ctrl.lock_hide('sx', 'sy', 'sz', 'v')

        #-- Blending Fk Ik
        self.leg_ctrl.add_attr('fkIk', min = 0, max = 1)

        self.upleg_blend = util.translate_rotate_blend( self.leg_ctrl.attr('fkIk'),
                                                        self.upleg_fk_rigJnt,
                                                        self.upleg_ik_rigJnt,
                                                        self.upleg_rigJnt )

        self.lowleg_blend = util.translate_rotate_blend( self.leg_ctrl.attr('fkIk'),
                                                         self.lowleg_fk_rigJnt,
                                                         self.lowleg_ik_rigJnt,
                                                         self.lowleg_rigJnt )
        
        self.ankle_blend = util.translate_rotate_blend( self.leg_ctrl.attr('fkIk'),
                                                        self.ankle_fk_rigJnt,
                                                        self.ankle_ik_rigJnt,
                                                        self.ankle_rigJnt )
        
        self.upleg_blend.name = 'UpLeg{}FkIk{}Blend'.format(part, side)
        self.lowleg_blend.name = 'LowLeg{}FkIk{}Blend'.format(part, side)
        self.ankle_blend.name = 'Ankle{}FkIk{}Blend'.format(part, side)

        self.fkIk_rev = node.Reverse('Leg{}FkIk{}Rev'.format(part, side))
        self.leg_ctrl.attr('fkIk') >> self.legCtrl_ik_grp.attr('v')
        self.leg_ctrl.attr('fkIk') >> self.fkIk_rev.attr('ix')
        self.fkIk_rev.attr('ox') >> self.legCtrl_fk_grp.attr('v')
        self.leg_ctrl.attr('fkIk').value = 1

        #-- Setup leg scale
        self.leg_ctrl.add_attr('legScale', dv = 1)
        self.lowleg_jnt.attr('ssc').value = 0
        
        for __attr in 'xyz':
            self.leg_ctrl.attr('legScale') >> self.legScl_grp.attr('s{}'.format(__attr))
            self.leg_ctrl.attr('legScale') >> self.upleg_jnt.attr('s{}'.format(__attr))

        if foot:
            #-- Ik Create rig joint
            self.ball_ik_rigJnt = node.Joint('Ball{}Ik{}RigJnt'.format(part, side), position = ball_tmpJnt)
            self.toe_ik_rigJnt = node.Joint('Toe{}Ik{}RigJnt'.format(part, side), position = toe_tmpJnt)
            
            mc.parent(self.toe_ik_rigJnt, self.ball_ik_rigJnt)
            mc.parent(self.ball_ik_rigJnt, self.ankle_ik_rigJnt)

            #-- Ik Pivot create group
            self.footScl_grp = node.Transform('Foot{}Scale{}Grp'.format(part, side))
            self.footAllPiv_grp = node.Transform('Foot{}IkAllPiv{}Grp'.format(part, side))
            self.footZro_grp = node.Transform('Foot{}IkZro{}Grp'.format(part, side))
            self.footPiv_grp = node.Transform('Foot{}IkPiv{}Grp'.format(part, side))
            self.ballPiv_grp = node.Transform('Ball{}IkPiv{}Grp'.format(part, side))
            self.bendPiv_grp = node.Transform('Bend{}IkPiv{}Grp'.format(part, side))
            self.heelPiv_grp = node.Transform('Heel{}IkPiv{}Grp'.format(part, side))
            self.toePiv_grp = node.Transform('Toe{}IkPiv{}Grp'.format(part, side))
            self.inPiv_grp = node.Transform('In{}IkPiv{}Grp'.format(part, side))
            self.outPiv_grp = node.Transform('Out{}IkPiv{}Grp'.format(part, side))
            self.anklePiv_grp = node.Transform('Ankle{}IkPiv{}Grp'.format(part, side))

            #-- Ik Pivot create controls
            self.footPiv_ik_ctrl = util.controller('Foot{}IkPiv{}Ctrl'.format(part, side), 'locator', 'cyan')

            self.footSmartPiv_ik_ctrl = util.controller('Foot{}IkSmartPiv{}Ctrl'.format(part, side), 'locator', 'white')
            self.footFrame_ik_ctrl = util.controller('Foot{}IkFrame{}Ctrl'.format(part, side), 'square', 'red')
            self.footSmart_ik_ctrl = util.controller('Foot{}IkSmart{}Ctrl'.format(part, side), 'arrowCircle', 'pink')

            self.anklePiv_ik_ctrl = util.controller('Ankle{}IkPiv{}Ctrl'.format(part, side), 'square', 'red')
            self.bendPiv_ik_ctrl = util.controller('Bend{}IkPiv{}Ctrl'.format(part, side), 'square', 'red')
            self.toePiv_ik_ctrl = util.controller('Toe{}IkPiv{}Ctrl'.format(part, side), 'arrowBall', 'yellow')
            self.heelPiv_ik_ctrl = util.controller('Heel{}IkPiv{}Ctrl'.format(part, side), 'arrowBall', 'yellow')
            self.inPiv_ik_ctrl = util.controller('In{}IkPiv{}Ctrl'.format(part, side), 'cube', 'yellow')
            self.outPiv_ik_ctrl = util.controller('Out{}IkPiv{}Ctrl'.format(part, side), 'cube', 'yellow')
            
            #-- Ik Pivot manage hierarchy
            mc.parent(self.footScl_grp, self.ankle_ik_gmbl)
            mc.parent(self.footAllPiv_grp, self.footScl_grp)
            
            mc.parent(self.footSmart_ik_ctrl, self.footFrame_ik_ctrl)
            mc.parent(self.footFrame_ik_ctrl, self.footSmartPiv_ik_ctrl)
            mc.parent(self.footPiv_grp, self.footPiv_ik_ctrl, self.footSmartPiv_ik_ctrl, self.footAllPiv_grp)

            mc.parent(self.anklePiv_ik_ctrl, self.ballPiv_grp)
            mc.parent(self.bendPiv_ik_ctrl, self.bendPiv_grp)
            mc.parent(self.toePiv_ik_ctrl, self.toePiv_grp)
            mc.parent(self.heelPiv_ik_ctrl, self.heelPiv_grp)
            mc.parent(self.inPiv_ik_ctrl, self.inPiv_grp)
            mc.parent(self.outPiv_ik_ctrl, self.outPiv_grp)
            
            #-- Ik Pivot setup positions
            self.footScl_grp.snap(ankle_tmpJnt)
            self.footAllPiv_grp.snap_point(toe_tmpJnt)
            self.footZro_grp.snap_point(toe_tmpJnt)
            self.footPiv_grp.snap_point(toe_tmpJnt)
            self.ballPiv_grp.snap_point(ball_tmpJnt)
            self.bendPiv_grp.snap_point(ball_tmpJnt)
            self.toePiv_grp.snap_point(toe_tmpJnt)
            self.heelPiv_grp.snap_point(heel_tmpJnt)
            self.inPiv_grp.snap_point(footIn_tmpJnt)
            self.outPiv_grp.snap_point(footOut_tmpJnt)
            self.anklePiv_grp.snap_point(ankle_tmpJnt)

            for __grp in (self.footZro_grp, self.ballPiv_grp, self.bendPiv_grp, self.toePiv_grp,
                          self.heelPiv_grp, self.inPiv_grp, self.outPiv_grp):
                __grp.snap_orient(ball_tmpJnt)

            self.footAllPiv_grp.snap_aim(ball_tmpJnt, aim = (0, 0, -1), u = (0, 1, 0))

            smart_position = toe_tmpJnt
            if mc.objExists(footSmart_tmpJnt):
                smart_position = footSmart_tmpJnt

            self.footSmartPiv_ik_ctrl.snap_point(smart_position)

            #-- Ik Pivot manage hierarchy
            mc.parent(self.ballPiv_grp, self.bendPiv_grp, self.outPiv_ik_ctrl)
            mc.parent(self.outPiv_grp, self.inPiv_ik_ctrl)
            mc.parent(self.inPiv_grp, self.heelPiv_ik_ctrl)
            mc.parent(self.heelPiv_grp, self.toePiv_ik_ctrl)
            mc.parent(self.toePiv_grp, self.footZro_grp)
            mc.parent(self.footZro_grp, self.footPiv_grp)
            mc.parent(self.anklePiv_grp, self.anklePiv_ik_ctrl)
            
            #-- Ik Pivot rig process
            self.footSmart_ik_ctrl.shape.add_attr('pivotControls', min = 0, max = 1)
            self.footSmart_ik_ctrl.shape.add_attr('smartAmp', dv = 7.5)

            self.footSmart_ik_ctrl.shape.attr('pivotControls') >> self.inPiv_ik_ctrl.shape.attr('v')
            self.footSmart_ik_ctrl.shape.attr('pivotControls') >> self.outPiv_ik_ctrl.shape.attr('v')
            self.footSmart_ik_ctrl.shape.attr('pivotControls') >> self.footPiv_ik_ctrl.shape.attr('v')

            self.footPiv_ik_ctrl.attr('r') >> self.footPiv_grp.attr('r')
            self.footPiv_ik_ctrl.attr('t') >> self.footPiv_grp.attr('rotatePivot')
            self.footPiv_ik_ctrl.attr('t') >> self.footPiv_grp.attr('scalePivot')

            #-- Ik Pivot cleanup
            self.footFrame_ik_ctrl.lhtrs()
            self.footFrame_ik_ctrl.lhv()

            self.footFrame_ik_ctrl.shape.attr('overrideEnabled').value = 1
            self.footFrame_ik_ctrl.shape.attr('overrideDisplayType').value = 2
            
            self.footPiv_ik_ctrl.lock_hide('sx', 'sy', 'sz', 'v')

            for __ctrl in (self.anklePiv_ik_ctrl, self.bendPiv_ik_ctrl, self.toePiv_ik_ctrl,
                           self.heelPiv_ik_ctrl, self.inPiv_ik_ctrl, self.outPiv_ik_ctrl):
                __ctrl.lock_hide('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')

            mc.transformLimits(self.footSmart_ik_ctrl, etx = (True, True), tx = (-5, 5))
            mc.transformLimits(self.footSmart_ik_ctrl, etz = (True, True), tz = (-5, 5))

            #-- Ik Pivot adjust shape controls
            for __ctrl in (self.inPiv_ik_ctrl, self.outPiv_ik_ctrl):
                __ctrl.scale_shape(0.25)

            for __ctrl in (self.toePiv_ik_ctrl, self.heelPiv_ik_ctrl):
                __ctrl.scale_shape(0.50)

            for __ctrl in (self.anklePiv_ik_ctrl, self.bendPiv_ik_ctrl):
                __ctrl.rotate_shape((90, 0, 0))
            
            self.footSmart_ik_ctrl.scale_shape(0.8)
            self.footFrame_ik_ctrl.scale_shape(5)

            self.footSmartPiv_ik_ctrl.attr('s').value = [0.2]*3

            if 'L' in side:
                self.heelPiv_ik_ctrl.rotate_shape((180, 0, 0))
            elif 'R' in side:
                self.toePiv_ik_ctrl.rotate_shape((180, 0, 0))
                self.footSmartPiv_ik_ctrl.attr('sx').value = (self.footSmartPiv_ik_ctrl.attr('sx').value * -1)
            
            position_value = util.get_local_offset(self.anklePiv_ik_ctrl, heel_tmpJnt)
            self.anklePiv_ik_ctrl.move_shape(position_value)

            #-- Ik Set rotate order
            for __each in (self.ball_ik_rigJnt, self.toe_ik_rigJnt,
                           self.anklePiv_ik_ctrl, self.bendPiv_ik_ctrl):
                __each.rotate_order = rotate_order

            #-- Ik Foot additional toe stretch
            self.ankle_ik_ctrl.add_attr('toeStretch')
            self.toeStrt_ik_mult = node.MultDoubleLinear('Toe{}IkStrt{}Mult'.format(part, side))
            self.toeStrt_ik_add = node.AddDoubleLinear('Toe{}IkStrt{}Add'.format(part, side))
            
            self.toeStrt_ik_mult.attr('i2').value = side_value
            self.toeStrt_ik_add.add_attr('default', dv = self.toe_ik_rigJnt.attr('ty').value)

            self.ankle_ik_ctrl.attr('toeStretch') >> self.toeStrt_ik_mult.attr('i1')
            self.toeStrt_ik_add.attr('default') >> self.toeStrt_ik_add.attr('i1')
            self.toeStrt_ik_mult.attr('o') >> self.toeStrt_ik_add.attr('i2')
            self.toeStrt_ik_add.attr('o') >> self.toe_ik_rigJnt.attr('ty')

            #-- Ik Foot Add ikhandle
            self.ball_ikh, ball_eff = util.add_ikhandle('Ball{}'.format(part),
                                                        'ikSCsolver',
                                                        self.ankle_ik_rigJnt,
                                                        self.ball_ik_rigJnt)
            
            self.toe_ikh, toe_eff = util.add_ikhandle('Toe{}'.format(part),
                                                       'ikSCsolver',
                                                       self.ball_ik_rigJnt,
                                                       self.toe_ik_rigJnt)
            
            mc.parent(self.ankle_ikh, self.ball_ikh, self.anklePiv_ik_ctrl)
            mc.parent(self.toe_ikh, self.bendPiv_ik_ctrl)
            
            #-- Ik Foot update position end distance
            util.remove_connected_constraints(self.ik_dist_end_grp)

            self.ik_dist_end_grp.attr('t').lock = False
            self.ik_dist_end_grp.attr('r').lock = False

            util.parent_constraint( self.anklePiv_grp, 
                                    self.ik_dist_end_grp, 
                                    mo = True )
            
            #-- Ik Foot setup functions
            self.ankle_ik_ctrl.add_divide_attr('foot')
            self.ankle_ik_ctrl.add_attr('ballRoll')
            self.ankle_ik_ctrl.add_attr('toeHeelRoll')
            self.ankle_ik_ctrl.add_attr('heelTwist')
            self.ankle_ik_ctrl.add_attr('toeTwist')
            self.ankle_ik_ctrl.add_attr('toeBend')
            self.ankle_ik_ctrl.add_attr('toeSide')
            self.ankle_ik_ctrl.add_attr('toeSwirl')
            self.ankle_ik_ctrl.add_attr('footRock')

            if foot == True and footSmart == True:
                self.foot_ctrl = self.footSmart_ik_ctrl
            elif foot == True and footSmart == False:
                self.foot_ctrl = self.ankle_ik_ctrl

            self.foot_ctrl.shape.add_attr('toeBreak')
            self.foot_ctrl.shape.attr('toeBreak').value = -30

            self.smart_inv_amp = node.MultDoubleLinear('Leg{}IkSmartInv{}Amp'.format(part, side))
            self.footSmart_ik_ctrl.shape.attr('smartAmp') >> self.smart_inv_amp.attr('i1')
            self.smart_inv_amp.attr('i2').value = -1

            self.ball_break_cmp = node.Clamp('Ball{}IkBreak{}Cmp'.format(part, side))
            self.ball_break_sum = node.AddDoubleLinear('Ball{}IkBreak{}Sum'.format(part, side))
            self.ball_smart_amp = node.MultDoubleLinear('Ball{}IkSmart{}Amp'.format(part, side))
            self.smart_inv_amp.attr('o') >> self.ball_smart_amp.attr('i2')

            self.toe_break_cnd = node.Condition('Toe{}IkBreak{}Cnd'.format(part, side))
            self.toe_break_amp_mdv = node.MultiplyDivide('Toe{}IkBreakAmp{}Mdv'.format(part, side))
            self.toe_break_amp_pma = node.PlusMinusAverage('Toe{}IkBreakAmp{}Pma'.format(part, side))
            self.toe_break_pma = node.PlusMinusAverage('Toe{}IkBreak{}Pma'.format(part, side))
            self.toe_break_sum = node.AddDoubleLinear('Toe{}IkBreak{}Sum'.format(part, side))
            self.toe_smart_amp = node.MultDoubleLinear('Toe{}IkSmart{}Amp'.format(part, side))
            self.toe_break_cnd.attr('op').value = 2
            self.toe_break_amp_mdv.attr('i2x').value = -1
            self.toe_break_cnd.attr('cfr').value = 0
            self.smart_inv_amp.attr('o') >> self.toe_smart_amp.attr('i2')

            self.heel_break_cmp = node.Clamp('Heel{}IkBreak{}Cmp'.format(part, side))
            self.heel_break_pma = node.PlusMinusAverage('Heel{}IkBreak{}Pma'.format(part, side))
            self.heel_break_sum = node.AddDoubleLinear('Heel{}IkBreak{}Sum'.format(part, side))
            self.heel_smart_amp = node.MultDoubleLinear('Heel{}IkSmart{}Amp'.format(part, side))
            self.heel_break_cmp.attr('maxR').value = 100
            self.smart_inv_amp.attr('o') >> self.heel_smart_amp.attr('i2')
            
            self.footIn_sum = node.AddDoubleLinear('Foot{}IkIn{}Sum'.format(part, side))
            self.footOut_sum = node.AddDoubleLinear('Foot{}IkOut{}Sum'.format(part, side))
            self.footIn_smart_amp = node.MultDoubleLinear('Foot{}IkInSmart{}Amp'.format(part, side))
            self.footOut_smart_amp = node.MultDoubleLinear('Foot{}IkOutSmart{}Amp'.format(part, side))
            self.smart_inv_amp.attr('o') >> self.footIn_smart_amp.attr('i2')
            self.smart_inv_amp.attr('o') >> self.footOut_smart_amp.attr('i2')
            
            self.ankle_ik_ctrl.attr('ballRoll') >> self.ball_break_sum.attr('i1')
            self.footSmart_ik_ctrl.attr('tz') >> self.ball_smart_amp.attr('i1')
            self.ball_smart_amp.attr('o') >> self.ball_break_sum.attr('i2')
            self.ball_break_sum.attr('o') >> self.ball_break_cmp.attr('inputR')
            self.foot_ctrl.shape.attr('toeBreak') >> self.ball_break_cmp.attr('minR')
            self.ball_break_cmp.attr('outputR') >> self.ballPiv_grp.attr('rx')
            self.foot_ctrl.shape.attr('toeBreak') >> self.toe_break_amp_mdv.attr('i1x')
            self.toe_break_amp_mdv.attr('ox') >> self.toe_break_amp_pma.attr('i1').last()
            self.footSmart_ik_ctrl.attr('tz') >> self.toe_smart_amp.attr('i1')
            self.ankle_ik_ctrl.attr('ballRoll') >> self.toe_break_amp_pma.attr('i1').last()
            self.toe_smart_amp.attr('o') >> self.toe_break_amp_pma.attr('i1').last()
            self.toe_break_amp_pma.attr('o1') >> self.toe_break_cnd.attr('ctr')
            self.foot_ctrl.shape.attr('toeBreak') >> self.toe_break_cnd.attr('ft')
            self.ankle_ik_ctrl.attr('ballRoll') >> self.toe_break_sum.attr('i1')
            self.toe_smart_amp.attr('o') >> self.toe_break_sum.attr('i2')
            self.toe_break_sum.attr('o') >> self.toe_break_cnd.attr('st')
            self.toe_break_cnd.attr('ocr') >> self.toe_break_pma.attr('i1').last()
            self.toe_break_pma.attr('o1') >> self.toePiv_grp.attr('rx')

            self.footSmart_ik_ctrl.attr('tz') >> self.heel_smart_amp.attr('i1')
            self.ankle_ik_ctrl.attr('ballRoll') >> self.heel_break_sum.attr('i1')
            self.heel_smart_amp.attr('o') >> self.heel_break_sum.attr('i2')
            self.heel_break_sum.attr('o') >> self.heel_break_cmp.attr('inputR')
            self.heel_break_cmp.attr('outputR') >> self.heel_break_pma.attr('i1').last()
            self.heel_break_pma.attr('o1') >> self.heelPiv_grp.attr('rx')

            self.ankle_ik_ctrl.attr('toeHeelRoll') >> self.heel_break_pma.attr('i1').last()
            self.ankle_ik_ctrl.attr('toeHeelRoll') >> self.toe_break_pma.attr('i1').last()

            self.ankle_ik_ctrl.attr('heelTwist') >> self.heelPiv_grp.attr('rz')
            self.ankle_ik_ctrl.attr('toeTwist') >> self.toePiv_grp.attr('rz')
            self.ankle_ik_ctrl.attr('toeBend') >> self.bendPiv_grp.attr('rx')
            self.ankle_ik_ctrl.attr('toeSide') >> self.bendPiv_grp.attr('rz')
            self.ankle_ik_ctrl.attr('toeSwirl') >> self.bendPiv_grp.attr('ry')

            self.ankle_ik_ctrl.attr('footRock') >> self.footIn_sum.attr('i1')
            self.ankle_ik_ctrl.attr('footRock') >> self.footOut_sum.attr('i1')
            self.footSmart_ik_ctrl.attr('tx') >> self.footIn_smart_amp.attr('i1')
            self.footSmart_ik_ctrl.attr('tx') >> self.footOut_smart_amp.attr('i1')
            self.footIn_smart_amp.attr('o') >> self.footIn_sum.attr('i2')
            self.footOut_smart_amp.attr('o') >> self.footOut_sum.attr('i2')
            self.footIn_sum.attr('o') >> self.inPiv_grp.attr('ry')
            self.footOut_sum.attr('o') >> self.outPiv_grp.attr('ry')
            
            mc.transformLimits(self.inPiv_grp, ery = (True, False), ry = (0, 0))
            mc.transformLimits(self.outPiv_grp, ery = (False, True), ry = (0, 0))

            mc.transformLimits(self.toePiv_grp, erx = (False, True), rx = (0, 0))
            mc.transformLimits(self.heelPiv_grp, erx = (True, False), rx = (0, 0))
            
            #-- Foot Blending Fk Ik
            self.ball_blend = util.translate_rotate_blend( self.leg_ctrl.attr('fkIk'),
                                                           self.ball_fk_rigJnt,
                                                           self.ball_ik_rigJnt,
                                                           self.ball_rigJnt )

            self.toe_blend = util.translate_rotate_blend( self.leg_ctrl.attr('fkIk'),
                                                          self.toe_fk_rigJnt,
                                                          self.toe_ik_rigJnt,
                                                          self.toe_rigJnt )
        
            self.ball_blend.name = 'Ball{}FkIk{}Blend'.format(part, side)
            self.toe_blend.name = 'Toe{}FkIk{}Blend'.format(part, side)

            #-- Setup foot scale
            self.leg_ctrl.add_attr('footScale', dv = 1)

            for __jnt in (self.ankle_rigJnt, self.ankle_jnt, self.ball_rigJnt, self.ball_jnt, 
                          self.ball_fk_rigJnt, self.ball_ik_rigJnt, self.toe_rigJnt, 
                          self.toe_jnt, self.toe_fk_rigJnt, self.toe_ik_rigJnt):
                __jnt.attr('ssc').value = 0

            for __attr in 'xyz':
                for __scl in (self.footScl_grp, self.ball_fk_scl, self.ankle_rigJnt, 
                              self.ankle_fk_rigJnt, self.ankle_ik_rigJnt):
                    self.leg_ctrl.attr('footScale') >> __scl.attr('s{}'.format(__attr))
            
            #-- Ik Foot Cleanup
            if foot == True and footSmart == True:
                self.ankle_ik_ctrl.lock_hide( 'foot',
                                              'ballRoll',
                                              'toeHeelRoll',
                                              'heelTwist',
                                              'toeTwist',
                                              'toeBend',
                                              'toeSide',
                                              'toeSwirl',
                                              'footRock' )

            elif foot == True and footSmart == False:
                self.footAllPiv_grp.attr('v').value = 0

        #-- Additional ribbon
        if ribbon:
            #-- Create group ribbon
            self.legRbn_ctrl_grp = node.Transform('Leg{}RbnCtrl{}Grp'.format(part, side))
            self.legRbn_still_grp = node.Transform('Leg{}RbnStill{}Grp'.format(part, side))

            mc.parent(self.legRbn_ctrl_grp, self.legScl_grp)
            mc.parent(self.legRbn_still_grp, still_grp)

            #-- Create ribbon controls 
            self.leg_rbn_ctrl = util.controller('Leg{}Rbn{}Ctrl'.format(part, side), 'plus', 'yellow')
            self.leg_rbn_zro = util.group(self.leg_rbn_ctrl, 'Zro')
            self.leg_rbn_zro.snap(lowleg_tmpJnt)

            mc.parent(self.leg_rbn_zro, self.legScl_grp)

            self.leg_rbn_ctrl.lock_hide('rx', 'ry', 'rz', 's{}'.format(aim_axis[0]), 'v')

            #-- Adjust shape controls
            self.leg_rbn_ctrl.scale_shape(0.7)

            #-- Rig process
            util.parent_constraint( self.lowleg_jnt,
                                    self.leg_rbn_zro,
                                    mo = True )
            
            #-- Find distance
            upleg_dist = util.distance_between(util.get_position(self.upleg_jnt),
                                               util.get_position(self.lowleg_jnt))
            
            lowleg_dist = util.distance_between(util.get_position(self.lowleg_jnt),
                                                util.get_position(self.ankle_jnt))

            blend_offset = (lowleg_dist/10)*side_value

            #-- Setup ankle blend
            self.ankle_blend_grp = node.Transform('Ankle{}Blend{}Grp'.format(part, side))
            self.ankle_blend_ofst = node.Transform('Ankle{}BlendOfst{}Grp'.format(part, side))
            self.ankle_blend_on = node.Transform('Ankle{}BlendOn{}Grp'.format(part, side))
            self.ankle_blend_off = node.Transform('Ankle{}BlendOff{}Grp'.format(part, side))
            self.ankle_blend_auto = node.Transform('Ankle{}BlendAuto{}Grp'.format(part, side))

            mc.parent(self.ankle_blend_off, self.ankle_blend_on, self.ankle_blend_auto, self.ankle_blend_ofst)
            mc.parent(self.ankle_blend_ofst, self.ankle_blend_grp)
            mc.parent(self.ankle_blend_grp, self.legRbn_ctrl_grp)

            self.ankle_blend_grp.snap(ankle_tmpJnt)
            self.ankle_blend_ofst.attr('ty').value = blend_offset
            
            util.aim_constraint( self.lowleg_jnt,
                                 self.ankle_blend_on,
                                 aim = knee_aimvec,
                                 u = upvec,
                                 wut ='object',
                                 wuo = self.ankle_blend_ofst )
            
            util.parent_constraint( self.ankle_jnt,
                                    self.ankle_blend_grp,
                                    mo = True )

            self.ankle_blend_parcons = util.parent_constraint( self.ankle_blend_on,
                                                               self.ankle_blend_off,
                                                               self.ankle_blend_auto,
                                                               mo = True )
        
            self.ankle_blend_rev = node.Reverse('Ankle{}Blend{}Rev'.format(part, side))
            self.ankle_blend_rem = node.RemapValue('Ankle{}Blend{}Rem'.format(part, side))
            
            self.leg_ctrl.add_attr('ankleBlend', min = 0, max = 1)
            self.leg_ctrl.attr('ankleBlend') >> self.ankle_blend_rem.attr('i')
            self.ankle_blend_rem.attr('outValue') >> self.ankle_blend_rev.attr('ix')
            self.ankle_blend_rem.attr('outValue') >> self.ankle_blend_parcons.attr('{}W0'.format(self.ankle_blend_on))
            self.ankle_blend_rev.attr('ox') >> self.ankle_blend_parcons.attr('{}W1'.format(self.ankle_blend_off))
            self.ankle_blend_rem.attr('omx').value = 0.5
            
            #-- UpLeg ribbon
            self.upleg_rbn = rbn.Ribbon( name = 'UpLeg{}'.format(part),
                                         axis = axis,
                                         side = side,
                                         dist = upleg_dist,
                                         subdiv = 1 )
            
            self.upleg_rbn.rbnCtrl_grp.snap(self.upleg_jnt)
            
            util.parent_constraint( self.upleg_jnt,
                                    self.upleg_rbn.rbnCtrl_grp,
                                    mo = True )
            
            util.parent_constraint( self.upleg_jnt,
                                    self.upleg_rbn.rbn_root_ctrl,
                                    mo = True )
            
            util.parent_constraint( self.leg_rbn_ctrl,
                                    self.upleg_rbn.rbn_end_ctrl,
                                    mo = True )

            #-- LowLeg ribbon
            self.lowleg_rbn = rbn.Ribbon( name = 'LowLeg{}'.format(part),
                                          axis = axis,
                                          side = side,
                                          dist = lowleg_dist,
                                          subdiv = 1 )
            
            self.lowleg_rbn.rbnCtrl_grp.snap(self.lowleg_jnt)
            
            util.parent_constraint( self.lowleg_jnt,
                                    self.lowleg_rbn.rbnCtrl_grp,
                                    mo = True )
            
            util.parent_constraint( self.leg_rbn_ctrl,
                                    self.lowleg_rbn.rbn_root_ctrl,
                                    mo = True )
            
            util.parent_constraint( self.ankle_blend_auto,
                                    self.lowleg_rbn.rbn_end_ctrl,
                                    mo = True )
            
            #-- Setup scale
            for _ax in sqsh_axis:
                ax_attr = 's{}'.format(_ax)
                self.leg_rbn_ctrl.attr(ax_attr) >> self.upleg_rbn.rbn_end_ctrl.attr(ax_attr)
                self.leg_rbn_ctrl.attr(ax_attr) >> self.lowleg_rbn.rbn_root_ctrl.attr(ax_attr)
            
            #-- Cleanup
            for _ctrl in (self.upleg_rbn.rbn_root_ctrl, self.upleg_rbn.rbn_end_ctrl,
                          self.lowleg_rbn.rbn_root_ctrl, self.lowleg_rbn.rbn_end_ctrl):
                _ctrl.lock_hide('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 's{}'.format(sqsh_axis[0]), 's{}'.format(sqsh_axis[1]))
                _ctrl.get_parent().hide()

            #-- Adjust ribbon
            self.upleg_rbn.rbn_ctrl.shape.attr('rootTwistAmp').value = -1
            self.lowleg_rbn.rbn_ctrl.shape.attr('rootTwistAmp').value = -1

            self.upleg_rbn.rbn_ctrl.attr('autoTwist').value = 1
            self.lowleg_rbn.rbn_ctrl.attr('autoTwist').value = 1

            #-- Setup twist
            self.upleg_nonroll_jnt[0].attr('twist') >> self.upleg_rbn.rbn_ctrl.shape.attr('rootAbsTwist')
            self.ankle_jnt.attr('ry') >> self.lowleg_rbn.rbn_ctrl.shape.attr('endAbsTwist')
            
            #-- Manage hierarchy
            mc.parent(self.upleg_rbn.rbnSkin_grp, self.upleg_jnt)
            mc.parent(self.lowleg_rbn.rbnSkin_grp, self.lowleg_jnt)
            
            mc.parent(self.upleg_rbn.rbnCtrl_grp, self.lowleg_rbn.rbnCtrl_grp, self.legRbn_ctrl_grp)
            mc.parent(self.upleg_rbn.rbnStill_grp, self.lowleg_rbn.rbnStill_grp, self.legRbn_still_grp)
    
        mc.select(cl = True)