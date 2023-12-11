# System modules.
from imp import reload

# Maya modules.
import maya.cmds as mc

# ncscript modules.
from ncTools.rig import node
from ncTools.rig import util
reload(node)
reload(util)

class Clavicle(object):

    def __init__( self, clav_tmpJnt = 'Clav_L_TmpJnt',
                        uparm_tmpJnt = 'UpArm_L_TmpJnt',
                        wrist_tmpJnt = 'Wrist_L_TmpJnt',
                        parent = 'Breast_Jnt',
                        ctrl_grp = 'Ctrl_Grp',
                        part = '',
                        side = 'L',
                        auto_clav = False,
                ):

        '''
        '''

        ##-- Prepare
        part = part.capitalize()
        side = util.set_side(side)
        rotate_order = 'yxz'
        aim_value = (0, 1, 0)

        if 'R' in side:
            aim_value = (0, -1, 0)

        #-- Create main group
        self.clavCtrl_grp = node.Transform('Clav{}Ctrl{}Grp'.format(part, side))
        util.trs_constraint(parent, self.clavCtrl_grp, mo = True)
        mc.parent(self.clavCtrl_grp, ctrl_grp)

        #-- Create joint
        self.clav_jnt = util.joint('Clav{}{}Jnt'.format(part, side), position = clav_tmpJnt)
        self.clavEnd_jnt = util.joint('Clav{}End{}Jnt'.format(part, side), position = uparm_tmpJnt)
        self.clavPos_jnt = util.joint('Clav{}Pos{}Jnt'.format(part, side), position = clav_tmpJnt)

        mc.parent(self.clav_jnt, self.clavEnd_jnt, self.clavPos_jnt)
        mc.parent(self.clavPos_jnt, parent)

        #-- Create controls
        self.clav_ctrl = util.controller('Clav{}{}Ctrl'.format(part, side), 'stick', 'yellow')
        self.clav_gmbl = util.gimbal(self.clav_ctrl)
        self.clav_zro = util.group(self.clav_ctrl, 'Zro')
        self.clav_ofst = util.group(self.clav_ctrl, 'Ofst')
        self.clav_zro.snap(clav_tmpJnt)

        self.shoulder_ctrl = util.controller('Shoulder{}{}Ctrl'.format(part, side), 'daimond', 'pink', jnt = True)
        self.shoulder_zro = util.group(self.shoulder_ctrl, 'Zro')
        self.shoulder_zro.snap_point(uparm_tmpJnt)
        self.shoulder_ctrl.snap_joint_orient(uparm_tmpJnt)

        self.shoulder_ctrl.lock_hide('rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v')

        #-- Adjust shape controls
        for __ctrl in (self.clav_ctrl, self.clav_gmbl, self.shoulder_ctrl):
            
            if 'L' in side:
                __ctrl.rotate_shape((90, 0, 0))
            elif 'R' in side:
                __ctrl.rotate_shape((-90, 0, 0))

        #-- Set rotate order
        for __obj in (self.clav_ctrl, self.shoulder_ctrl, self.clav_ofst,
                     self.clav_jnt, self.clavEnd_jnt, self.clavPos_jnt):
            __obj.rotate_order = rotate_order

        #-- Rig process
        self.clavAim_grp = node.Transform('Clav{}Aim{}Grp'.format(part, side))
        self.clavOri_grp = node.Transform('Clav{}Ori{}Grp'.format(part, side))
        self.clavAim_grp.snap(clav_tmpJnt)
        self.clavOri_grp.snap(clav_tmpJnt)

        util.aim_constraint( self.shoulder_ctrl,
                             self.clavAim_grp,
                             aim = aim_value,
                             u = (0, 0, 1),
                             wut = 'objectrotation',
                             wuo = self.clav_gmbl,
                             wu  = (0, 0, 1),
                             mo  = False )

        util.point_constraint( self.shoulder_ctrl, 
                               self.clavEnd_jnt, 
                               mo = False )
         
        util.parent_constraint( self.clavOri_grp, 
                                self.clavPos_jnt, 
                                mo = False )
        
        self.clav_ctrl.attr('s') >> self.clav_jnt.attr('s')

        #-- Manage hierarchy
        mc.parent(self.clav_zro, self.clavCtrl_grp)
        mc.parent(self.clavOri_grp, self.clavAim_grp)
        mc.parent(self.shoulder_zro, self.clavAim_grp, self.clav_gmbl)

        #-- Prepare auto clavicle
        if auto_clav:
            self.clavAuto_grp = node.Transform('Clav{}Auto{}Grp'.format(part, side))
            self.clavAutoIkh_grp = node.Transform('Clav{}Ikh{}Grp'.format(part, side))
            self.clavAutoJnt_grp = node.Transform('Clav{}Jnt{}Grp'.format(part, side))

            mc.parent(self.clavAutoIkh_grp, self.clavAutoJnt_grp, self.clavAuto_grp)
            mc.parent(self.clavAuto_grp, self.clavCtrl_grp)

            self.clavAuto_grp.snap(clav_tmpJnt)
            self.clavAuto_grp.snap_aim(wrist_tmpJnt, 
                                       aim = aim_value, 
                                       u = (0, 0, 1), 
                                       wuo = self.clav_jnt, 
                                       wu = (0,0,1))

            #-- Main
            self.clavAuto_jnt = util.joint('Clav{}Auto{}Jnt'.format(part, side), position = self.clavAuto_grp)
            self.clavAuto_jnt.rotate_order = rotate_order
            mc.parent(self.clavAuto_jnt, self.clavAutoJnt_grp)

            #-- Fk , Ik
            self.auto_fk_dict = dict()
            self.auto_ik_dict = dict()

            for __type, __dict in zip(['Fk', 'Ik'], [self.auto_fk_dict, self.auto_ik_dict]):
                #-- Create joint
                __dict['jnt'] = util.joint('Clav{}Auto{}{}Jnt'.format(part, __type, side))
                __dict['endjnt'] = util.joint('Clav{}Auto{}End{}Jnt'.format(part, __type, side))
                mc.parent(__dict['endjnt'], __dict['jnt'])

                __dict['on_jnt'] = util.joint('Clav{}Auto{}On{}Jnt'.format(part, __type, side))
                __dict['on_endjnt'] = util.joint('Clav{}Auto{}OnEnd{}Jnt'.format(part, __type, side))
                mc.parent(__dict['on_endjnt'], __dict['on_jnt'])

                __dict['off_jnt'] = util.joint('Clav{}Auto{}Off{}Jnt'.format(part, __type, side))
                __dict['off_endjnt'] = util.joint('Clav{}Auto{}OffEnd{}Jnt'.format(part, __type, side))
                mc.parent(__dict['off_endjnt'], __dict['off_jnt'])

                #-- Create group
                __dict['grp'] = node.Transform('Clav{}Auto{}{}Grp'.format(part, __type, side))

                mc.parent(__dict['jnt'], __dict['on_jnt'], __dict['off_jnt'], __dict['grp'])
                mc.parent(__dict['grp'], self.clavAutoJnt_grp)
                
                #-- Adjust positions
                __dict['grp'].snap(self.clavAuto_grp)

                for __end in (__dict['endjnt'], __dict['on_endjnt'], __dict['off_endjnt']):
                    __end.snap_point(wrist_tmpJnt)
                    
                #-- Set rotate order
                for __each in (__dict['jnt'], __dict['endjnt'], __dict['on_jnt'], __dict['on_endjnt'], 
                              __dict['off_jnt'], __dict['off_endjnt']):
                    __each.rotate_order = rotate_order

            #-- Rig process
            self.fk_ikh, fk_eff = util.add_ikhandle('Clav{}AutoFk'.format(part), 
                                                    'ikSCsolver', 
                                                    self.auto_fk_dict['jnt'], 
                                                    self.auto_fk_dict['endjnt'])
            
            self.ik_ikh, ik_eff = util.add_ikhandle('Clav{}AutoIk'.format(part), 
                                                    'ikSCsolver', 
                                                    self.auto_ik_dict['jnt'], 
                                                    self.auto_ik_dict['endjnt'])
            
            
            self.ikOn_ikh, ikOn_eff = util.add_ikhandle('Clav{}AutoIkOn'.format(part), 
                                                        'ikSCsolver', 
                                                        self.auto_ik_dict['on_jnt'], 
                                                        self.auto_ik_dict['on_endjnt'])
            
            self.fk_ikh.attr('poleVector').value = (0,0,0)
            self.ik_ikh.attr('poleVector').value = (0,0,0)
            self.ikOn_ikh.attr('poleVector').value = (0,0,0)

            mc.parent(self.fk_ikh, self.ik_ikh, self.ikOn_ikh, self.clavAutoIkh_grp)

            self.clav_oricons = util.orient_constraint(self.clavAuto_jnt, self.clav_ofst, mo = True)
            self.auto_oricons = util.orient_constraint(self.auto_fk_dict['jnt'], self.auto_ik_dict['jnt'], self.clavAuto_jnt, mo = True)
            self.fkIkh_pntcons = util.point_constraint(self.auto_fk_dict['on_endjnt'], self.auto_fk_dict['off_endjnt'], self.fk_ikh, mo = True)
            self.ikIkh_pntcons = util.point_constraint(self.auto_ik_dict['on_endjnt'], self.auto_ik_dict['off_endjnt'], self.ik_ikh, mo = True)

            self.clavAutoFk_pma = node.PlusMinusAverage('Clav{}AutoFkOn{}Pma'.format(part, side))
            self.clavAuto_rev = node.Reverse('Clav{}Auto{}Rev'.format(part, side))

            self.clav_ctrl.add_attr('autoClav', min = 0, max = 1)
            self.clav_ctrl.attr('autoClav') >> self.clavAuto_rev.attr('ix')
            self.clav_ctrl.attr('autoClav') >> self.fkIkh_pntcons.attr('{}W0'.format(self.auto_fk_dict['on_endjnt']))
            self.clavAuto_rev.attr('ox') >> self.fkIkh_pntcons.attr('{}W1'.format(self.auto_fk_dict['off_endjnt']))
            self.clav_ctrl.attr('autoClav') >> self.ikIkh_pntcons.attr('{}W0'.format(self.auto_ik_dict['on_endjnt']))
            self.clavAuto_rev.attr('ox') >> self.ikIkh_pntcons.attr('{}W1'.format(self.auto_ik_dict['off_endjnt']))
            self.clavAutoFk_pma.attr('o3') >> self.auto_fk_dict['on_jnt'].attr('r')

            self.clav_ctrl.shape.add_attr('fkIk', min = 0, max = 1)
            self.clav_ctrl.shape.attr('fkIk') >> self.clavAuto_rev.attr('iy')
            self.clav_ctrl.shape.attr('fkIk') >> self.auto_oricons.attr('{}W1'.format(self.auto_ik_dict['jnt']))
            self.clavAuto_rev.attr('oy') >> self.auto_oricons.attr('{}W0'.format(self.auto_fk_dict['jnt']))

            self.clav_ctrl.shape.add_bool_tag('clavAuto', True)
            self.clav_ctrl.shape.add_str_tag('clavAutoFk', self.clavAutoFk_pma)
            self.clav_ctrl.shape.add_str_tag('clavAutoIk', self.ikOn_ikh)

            util.parent_constraint(parent, self.clavAuto_grp, mo = True)
            
            #-- Cleanup
            self.clav_ctrl.shape.attr('fkIk').hide = True
            self.clavAuto_grp.hide()

            for __grp in (self.clavAuto_grp, self.clavAutoIkh_grp, self.clavAutoJnt_grp, 
                         self.auto_fk_dict['grp'], self.auto_ik_dict['grp']):
                __grp.lhtrs()
            
            self.clav_ctrl.lhv()
            self.clav_ctrl.lock_hide('autoClav')
        
        mc.select(cl = True)

class ClavicleAuto(object):

    def __init__( self, arm_ctrl = 'Arm_L_Ctrl',
                        clav_ctrl = 'Clav_L_Ctrl',
                        uparm_fk_ctrl = 'UpArmFk_L_Ctrl',
                        wrist_ik_ctrl = 'WristIk_L_Ctrl'
                ):
        
        '''
        '''

        if mc.objExists('{}.clavAuto'.format(clav_ctrl.shape)):
            uparm_fk_gmbl = util.get_gimbal(uparm_fk_ctrl)
            wrist_ik_gmbl = util.get_gimbal(wrist_ik_ctrl)

            #-- Connect switch fk ik
            arm_ctrl.attr('fkIk') >> clav_ctrl.shape.attr('fkIk')
            clav_ctrl.shape.attr('fkIk').lock = True

            #-- Connect fk ctrl
            fk_pma = util.register_node(mc.getAttr('{}.clavAutoFk'.format(clav_ctrl.shape)))
            uparm_fk_ctrl.attr('r') >> fk_pma.attr('i3').last()

            if uparm_fk_gmbl:
                uparm_fk_gmbl.attr('r') >> fk_pma.attr('i3').last()

            #-- Connect ik ctrl
            ik_ikh = mc.getAttr('{}.clavAutoIk'.format(clav_ctrl.shape))

            if wrist_ik_gmbl:
                util.parent_constraint(wrist_ik_gmbl, ik_ikh, mo = True)
            else:
                util.parent_constraint(wrist_ik_ctrl, ik_ikh, mo = True)
            
            #-- Set value
            mc.setAttr('{}.autoClav'.format(clav_ctrl), l = False, k = True)
            clav_ctrl.attr('autoClav').value = 0.2

            #-- Cleanup
            clav_ctrl.shape.attr('clavAuto').remove()
            clav_ctrl.shape.attr('clavAutoFk').remove()
            clav_ctrl.shape.attr('clavAutoIk').remove()
        
        mc.select(cl = True)