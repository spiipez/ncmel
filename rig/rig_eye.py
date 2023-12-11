# System modules.
from imp import reload

# Maya modules.
import maya.cmds as mc

# ncscript modules.
from ncTools.rig import node
from ncTools.rig import util
reload(node)
reload(util)

class EyeMain(object):
    
    def __init__( self , parent = 'Head_Jnt',
                         ctrl_grp = 'Ctrl_Grp',
                         part = ''
                 ):
        
        '''
        '''

        ##-- Prepare
        self.part = part.capitalize()

        #-- Create main group
        _maingrp_ = 'Eye{}Ctrl_Grp'.format(self.part)

        if mc.objExists(_maingrp_):
            self.eyeCtrl_grp = util.register_node(_maingrp_)
        else:
            self.eyeCtrl_grp = node.Transform(_maingrp_)
            util.trs_constraint(parent, self.eyeCtrl_grp, mo = False)
            mc.parent(self.eyeCtrl_grp, ctrl_grp)

            self.eyeCtrl_grp.lhtrs()
            self.eyeCtrl_grp.lhv()

class Eye(EyeMain):

    def __init__( self , target_tmpJnt = 'EyeTrgt_TmpJnt',
                         eyeLft_tmpJnt = 'Eye_L_TmpJnt',
                         targetLft_tmpJnt = 'EyeTrgt_L_TmpJnt',
                         irisLft_tmpJnt = 'EyeIris_L_TmpJnt',
                         pupilLft_tmpJnt = 'EyePupil_L_TmpJnt',
                         dotLft_tmpJnt = 'EyeDot_L_TmpJnt',
                         eyeRgt_tmpJnt = 'Eye_R_TmpJnt',
                         targetRgt_tmpJnt = 'EyeTrgt_R_TmpJnt',
                         irisRgt_tmpJnt = 'EyeIris_R_TmpJnt',
                         pupilRgt_tmpJnt = 'EyePupil_R_TmpJnt',
                         dotRgt_tmpJnt = 'EyeDot_R_TmpJnt',
                         parent = 'Head_Jnt',
                         ctrl_grp = 'Ctrl_Grp',
                         eye_scale = (1, 1, 1),
                         part = ''
                 ):
        
        '''
        '''

        super(Eye, self).__init__(parent, ctrl_grp, part)

        #-- Create controls
        self.target_ctrl = util.controller('Eye{}Target_Ctrl'.format(self.part), 'square', 'yellow')
        self.target_zro = util.group(self.target_ctrl, 'Zro')
        self.target_zro.snap(target_tmpJnt)

        #-- Adjust shape controls
        self.target_ctrl.scale_shape(0.55)
        self.target_ctrl.rotate_shape((90, 0, 0))

        #-- Rig process
        self.target_locWor = util.local_world(self.target_ctrl, ctrl_grp, self.eyeCtrl_grp, self.target_zro, 'parent')

        #-- Manage hierarchy
        mc.parent(self.target_zro, self.eyeCtrl_grp)

        #-- Cleanup
        self.target_ctrl.lock_hide('sx', 'sy', 'sz', 'v')

        #-- Eye left
        self.eye_left = Single( eye_tmpJnt = eyeLft_tmpJnt,
                                target_tmpJnt = targetLft_tmpJnt,
                                iris_tmpJnt = irisLft_tmpJnt,
                                pupil_tmpJnt = pupilLft_tmpJnt,
                                dot_tmpJnt = dotLft_tmpJnt,
                                parent = parent,
                                ctrl_grp = ctrl_grp,
                                eye_scale = eye_scale,
                                part = part )

        #-- Eye right
        self.eye_right = Single( eye_tmpJnt = eyeRgt_tmpJnt,
                                 target_tmpJnt = targetRgt_tmpJnt,
                                 iris_tmpJnt = irisRgt_tmpJnt,
                                 pupil_tmpJnt = pupilRgt_tmpJnt,
                                 dot_tmpJnt = dotRgt_tmpJnt,
                                 parent = parent,
                                 ctrl_grp = ctrl_grp,
                                 eye_scale = eye_scale,
                                 part = part )

        for __each in (self.eye_left.eye_locWor, self.eye_right.eye_locWor):
            ctrl, space_grp, world_grp, local_grp, cons_position, cons_node, world_cons, rev = __each
            mc.delete(space_grp, cons_node, rev)

        self.eye_left.target_ctrl.attr('localWorld').remove()
        self.eye_right.target_ctrl.attr('localWorld').remove()

        mc.parent(self.eye_left.target_zro, self.eye_right.target_zro, self.target_ctrl)
        mc.select(cl = True)

class Single(EyeMain):

    def __init__( self , eye_tmpJnt = 'Eye_L_TmpJnt',
                         target_tmpJnt = 'EyeTrgt_L_TmpJnt',
                         iris_tmpJnt = 'EyeIris_L_TmpJnt',
                         pupil_tmpJnt = 'EyePupil_L_TmpJnt',
                         dot_tmpJnt = 'EyeDot_L_TmpJnt',
                         parent = 'Head_Jnt',
                         ctrl_grp = 'Ctrl_Grp',
                         eye_scale = (1, 1, 1),
                         part = ''
                 ):
        
        '''
        '''

        super(Single, self).__init__(parent, ctrl_grp, part)

        ##-- Prepare
        side = util.register_node(eye_tmpJnt).side

        #-- Create joint
        self.eye_jnt = node.Joint('Eye{}{}Jnt'.format(self.part, side), position = eye_tmpJnt)
        self.eyeAdj_jnt = node.Joint('Eye{}Adj{}Jnt'.format(self.part, side), position = eye_tmpJnt)
        self.eyeLid_jnt = node.Joint('Eye{}Lid{}Jnt'.format(self.part, side), position = eye_tmpJnt)

        mc.parent(self.eye_jnt, self.eyeAdj_jnt)
        mc.parent(self.eyeLid_jnt, self.eye_jnt)
        mc.parent(self.eyeAdj_jnt, parent)

        self.eyeAdj_jnt.attr('s').value = eye_scale

        for __jnt in (self.eye_jnt, self.eyeLid_jnt):
            __jnt.attr('s').value = [1]*3

        #-- Create controls
        self.eye_ctrl = util.controller('Eye{}{}Ctrl'.format(self.part, side), 'sphere', 'red')
        self.eye_zro = util.group(self.eye_ctrl, 'Zro')
        self.eye_aim = util.group(self.eye_ctrl, 'Aim')
        self.eye_zro.snap(eye_tmpJnt)

        self.target_ctrl = util.controller('Eye{}Target{}Ctrl'.format(self.part, side), 'plus', 'red')
        self.target_zro = util.group(self.target_ctrl, 'Zro')
        self.target_zro.snap(target_tmpJnt)

        #-- Adjust shape controls
        self.eye_ctrl.scale_shape(0.5)
        self.target_ctrl.scale_shape(0.15)
        self.target_ctrl.rotate_shape((90, 0, 0))

        #-- Adjust scale eye
        self.eye_zro.attr('s').value = eye_scale

        #-- Rig process
        util.parent_constraint(self.eye_ctrl, self.eye_jnt, mo = False)
        self.eye_locWor = util.local_world(self.target_ctrl, ctrl_grp, self.eyeCtrl_grp, self.target_zro, 'parent')

        self.eye_ctrl.attr('s') >> self.eye_jnt.attr('s')

        self.eye_jnt.attr('ssc').value = 0
        self.eyeAdj_jnt.attr('ssc').value = 0
        self.eyeLid_jnt.attr('ssc').value = 0

        util.aim_constraint( self.target_ctrl,
                             self.eye_aim,
                             aim = (0,0,1),
                             u = (0,1,0),
                             wut = "objectrotation",
                             wu = (0,1,0),
                             wuo = self.eye_zro,
                             mo = True )
        
        self.eye_ctrl.add_attr('eyelidsFollow', min = 0, max = 1)
        self.lidCons = util.orient_constraint(parent, self.eyeLid_jnt, mo = True)
        self.followCons = util.orient_constraint(parent, self.eye_jnt, self.eyeLid_jnt, mo = True)

        rev = node.Reverse('Eye{}Lid{}Rev'.format(self.part, side))

        self.eye_ctrl.attr('eyelidsFollow') >> self.followCons.attr('{}W1'.format(self.eye_jnt))
        self.eye_ctrl.attr('eyelidsFollow') >> rev.attr('ix')
        rev.attr('ox') >> self.followCons.attr('{}W0'.format(parent))

        #-- Manage hierarchy
        mc.parent(self.eye_zro, self.target_zro, self.eyeCtrl_grp)

        #-- Cleanup
        self.target_ctrl.lock_hide('sx', 'sy', 'sz', 'v')
        self.eye_ctrl.lock_hide('v')

        if iris_tmpJnt:
            #-- Create joint
            self.iris_jnt = node.Joint('Iris{}{}Jnt'.format(self.part, side), position = iris_tmpJnt)
            self.iris_grp = util.group(self.iris_jnt)
            self.iris_grp.attr('s').value = eye_scale
            self.iris_jnt.attr('ssc').value = 0
            mc.parent(self.iris_grp, self.eye_jnt)

            #-- Create controls
            self.iris_ctrl = util.controller('Iris{}{}Ctrl'.format(self.part, side), 'circle', 'cyan')
            self.iris_zro = util.group(self.iris_ctrl)
            self.iris_zro.snap(iris_tmpJnt)

            self.iris_zro.attr('s').value = eye_scale
            mc.parent(self.iris_zro, self.eye_ctrl)

            #-- Adjust shape controls
            self.iris_ctrl.scale_shape(0.1)
            self.iris_ctrl.rotate_shape((90, 0, 0))
            
            #-- Rig process
            util.parent_constraint(self.iris_ctrl, self.iris_jnt, mo = True)
            self.iris_ctrl.attr('s') >> self.iris_jnt.attr('s')

            #-- Cleanup
            self.iris_ctrl.lhv()

        if pupil_tmpJnt:
            #-- Create joint
            self.pupil_jnt = node.Joint('Pupil{}{}Jnt'.format(self.part, side), position = pupil_tmpJnt)
            self.pupil_grp = util.group(self.pupil_jnt)
            self.pupil_grp.attr('s').value = eye_scale
            self.pupil_jnt.attr('ssc').value = 0
            mc.parent(self.pupil_grp, self.eye_jnt)

            #-- Create controls
            self.pupil_ctrl = util.controller('Pupil{}{}Ctrl'.format(self.part, side), 'circle', 'pink')
            self.pupil_zro = util.group(self.pupil_ctrl)
            self.pupil_zro.snap(pupil_tmpJnt)

            self.pupil_zro.attr('s').value = eye_scale
            mc.parent(self.pupil_zro, self.eye_ctrl)

            #-- Adjust shape controls
            self.pupil_ctrl.scale_shape(0.1)
            self.pupil_ctrl.rotate_shape((90, 0, 0))
            
            #-- Rig process
            if iris_tmpJnt:
                mc.parent(self.pupil_zro, self.iris_ctrl)
                mc.parent(self.pupil_grp, self.iris_jnt)

            util.parent_constraint(self.pupil_ctrl, self.pupil_jnt, mo = True)
            self.pupil_ctrl.attr('s') >> self.pupil_jnt.attr('s')

            #-- Cleanup
            self.pupil_ctrl.lhv()

        if dot_tmpJnt:
            #-- Create joint
            self.dot_jnt = node.Joint('Dot{}{}Jnt'.format(self.part, side), position = dot_tmpJnt)
            self.dot_grp = util.group(self.dot_jnt)
            self.dot_jnt.attr('ssc').value = 0
            mc.parent(self.dot_grp, self.eye_jnt)

            #-- Create controls
            self.dot_ctrl = util.controller('Dot{}{}Ctrl'.format(self.part, side), 'circle', 'pink')
            self.dot_zro = util.group(self.dot_ctrl)
            self.dot_zro.snap(dot_tmpJnt)

            self.dot_zro.attr('s').value = eye_scale
            mc.parent(self.dot_zro, self.eye_ctrl)

            #-- Adjust shape controls
            self.dot_ctrl.scale_shape(0.1)
            self.dot_ctrl.rotate_shape((90, 0, 0))
            
            #-- Rig process
            util.parent_constraint(self.dot_ctrl, self.dot_jnt, mo = True)
            self.dot_ctrl.attr('s') >> self.dot_jnt.attr('s')

            #-- Cleanup
            self.dot_ctrl.lhv()
        
        mc.select(cl = True)