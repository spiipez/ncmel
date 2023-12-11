# System modules.
from imp import reload

# Maya modules.
import maya.cmds as mc

# ncscript modules.
from ncTools.rig import node
from ncTools.rig import util
reload(node)
reload(util)

class Scapular(object):

    def __init__( self, scap_tmpJnt = 'Scap_L_TmpJnt',
                        rump_tmpJnt = 'Rump_L_TmpJnt',
                        scapEnd_tmpJnt = 'UpLeg_L_TmpJnt',
                        scapAim_tmpJnt = 'Ankle_L_TmpJnt',
                        parent = 'Spine5Pos_jnt',
                        ctrl_grp = 'Ctrl_Grp',
                        part = '' ,
                        side = 'L',
                        axis = 'y',
                        auto_scap = False,
                        limb_lock = False,
                ):

        '''
        '''

        ##-- Prepare
        part = part.capitalize()
        side = util.set_side(side)
        rotate_order = 'xyz'
        aim_value = (0, 1, 0)
        side_value = 1

        if 'R' in side:
            aim_value = (0, -1, 0)
            side_value = -1

        #-- Create main group
        self.scapCtrl_grp = node.Transform('Scap{}Ctrl{}Grp'.format(part, side))
        util.parent_constraint(parent, self.scapCtrl_grp, mo = True)
        mc.parent(self.scapCtrl_grp, ctrl_grp)

        #-- Create joint
        self.scap_jnt = util.joint('Scap{}{}Jnt'.format(part, side), position = scap_tmpJnt)
        self.scapEnd_jnt = util.joint('Scap{}End{}Jnt'.format(part, side), position = scapEnd_tmpJnt)
        self.scapPos_jnt = util.joint('Scap{}Pos{}Jnt'.format(part, side), position = scap_tmpJnt)

        mc.parent(self.scap_jnt, self.scapEnd_jnt, self.scapPos_jnt)
        mc.parent(self.scapPos_jnt, parent)

        self.scap_jnt.attr('ssc').value = 0
        
        #-- Create controls
        self.rump_ctrl = util.controller('Rump{}{}Ctrl'.format(part, side), 'arrowBall', 'yellow')
        self.rump_gmbl = util.gimbal(self.rump_ctrl)
        self.rump_zro = util.group(self.rump_ctrl, 'Zro')
        self.rump_lock = util.group(self.rump_ctrl, 'LimbLock')
        self.rump_zro.snap(rump_tmpJnt)

        self.scap_ctrl = util.controller('Scap{}{}Ctrl'.format(part, side), 'arrowBall', 'yellow')
        self.scap_gmbl = util.gimbal(self.scap_ctrl)
        self.scap_zro = util.group(self.scap_ctrl, 'Zro')
        self.scap_auto = util.group(self.scap_ctrl, 'Auto')
        self.scap_zro.snap(scap_tmpJnt)

        self.scapMus_ctrl = util.controller('Scap{}Mus{}Ctrl'.format(part, side), 'sphere', 'pink')
        self.scapMus_gmbl = util.gimbal(self.scapMus_ctrl)
        self.scapMus_zro = util.group(self.scapMus_ctrl, 'Zro')
        self.scapMus_zro.snap(scap_tmpJnt)

        mc.parent(self.rump_zro, self.scapCtrl_grp)
        mc.parent(self.scap_zro, self.rump_gmbl)
        mc.parent(self.scapMus_zro, self.scap_gmbl)

        #-- Adjust shape controls
        for __ctrl in (self.scap_ctrl, self.scap_gmbl):
            __ctrl.scale_shape(0.35)

            if 'L' in side:
                __ctrl.rotate_shape((0, 0, 180))

        for __ctrl in (self.rump_ctrl, self.rump_gmbl):
            __ctrl.scale_shape(0.55)

            if 'L' in side:
                __ctrl.rotate_shape((0, 0, 90))
            elif 'R' in side:
                __ctrl.rotate_shape((0, 0, -90))

        for __ctrl in (self.scapMus_ctrl, self.scapMus_gmbl):
            __ctrl.scale_shape(0.55)

        #-- Set rotate order
        for __obj in (self.scap_jnt, self.scapPos_jnt, self.rump_ctrl, self.scap_ctrl):
            __obj.rotate_order = rotate_order

        #-- Rig process
        util.trs_constraint( self.scapMus_gmbl,
                             self.scap_jnt,
                             mo = False )
        
        util.parent_constraint( self.scap_gmbl,
                                self.scapPos_jnt,
                                mo = False )
        
        self.rump_stretch = util.add_offset_controller( self.rump_ctrl, 
                                                        self.scapEnd_jnt, 
                                                        'stretch', 
                                                        axis, side_value )
        
        self.scap_nonroll_jnt = util.add_non_roll_joint(self.scap_jnt, axis)

        #-- Cleanup
        for __obj in (self.scapCtrl_grp, self.scap_zro, self.scap_auto):
            __obj.lhtrs()
            __obj.lhv()

        for __obj in (self.scap_ctrl, self.scap_gmbl):
            __obj.lock_hide('sx', 'sy', 'sz', 'v')

        #-- Setup auto scapula
        if auto_scap:
            #-- Create group
            self.scapAuto_grp = node.Transform('Scap{}Auto{}Grp'.format(part, side))
            self.scapAuto_fkik_grp = node.Transform('Scap{}AutoFkIk{}Grp'.format(part, side))
            self.scapAuto_fk_grp = node.Transform('Scap{}AutoFk{}Grp'.format(part, side))
            self.scapAuto_ik_grp = node.Transform('Scap{}AutoIk{}Grp'.format(part, side))
            self.scapAim_on_grp = node.Transform('Scap{}AimOn{}Grp'.format(part, side))
            self.scapAim_off_grp = node.Transform('Scap{}AimOff{}Grp'.format(part, side))
            self.scapTrgt_grp = node.Transform('Scap{}Trgt{}Grp'.format(part, side))
            self.scapAim_rev = node.Reverse('Scap{}Aim{}Rev'.format(part, side))
            self.scap_fk_pma = node.PlusMinusAverage('Scap{}AutoFk{}Pma'.format(part, side))

            self.scapAuto_grp.snap(scap_tmpJnt)
            self.scapAuto_fkik_grp.snap(scapEnd_tmpJnt)
            self.scapAuto_fk_grp.snap(scapEnd_tmpJnt)
            self.scapAuto_ik_grp.snap(scapAim_tmpJnt)
            self.scapAim_on_grp.snap(scap_tmpJnt)
            self.scapAim_off_grp.snap(scap_tmpJnt)
            self.scapTrgt_grp.snap(scapAim_tmpJnt)

            mc.parent(self.scapAuto_grp, self.scap_zro)
            mc.parent(self.scapAuto_fk_grp, self.scapAuto_ik_grp, self.scapAuto_fkik_grp)
            mc.parent(self.scapAuto_fkik_grp, self.scapTrgt_grp, self.scapAim_on_grp, self.scapAim_off_grp, self.scapAuto_grp)

            #-- Rig process
            util.aim_constraint( self.scapTrgt_grp,
                                 self.scapAim_on_grp,
                                 aim = aim_value,
                                 u = (1, 0, 0),
                                 wut = 'objectrotation',
                                 wuo = self.scapTrgt_grp,
                                 wu = (1, 0, 0),
                                 mo = False )
            
            self.scapAim_off_grp.snap(self.scapAim_on_grp) # Adjust position after aim constraint

            self.scapAuto_oricons = util.orient_constraint( self.scapAim_on_grp,
                                                            self.scapAim_off_grp,
                                                            self.scap_auto,
                                                            mo = True )
            
            self.scap_ctrl.add_attr('autoScapula', min = 0, max = 1)
            self.scap_ctrl.attr('autoScapula') >> self.scapAim_rev.attr('ix')
            self.scap_ctrl.attr('autoScapula') >> self.scapAuto_oricons.attr('{}W0'.format(self.scapAim_on_grp))
            self.scapAim_rev.attr('ox') >> self.scapAuto_oricons.attr('{}W1'.format(self.scapAim_off_grp))
            self.scap_fk_pma.attr('o3') >> self.scapAuto_fk_grp.attr('r')

            #-- Setup Fk Ik switch
            self.fkIk_parcons = util.parent_constraint( self.scapAuto_fk_grp,
                                                        self.scapAuto_ik_grp,
                                                        self.scapTrgt_grp,
                                                        mo = True )
            
            self.scap_ctrl.shape.add_attr('fkIk', min = 0, max = 1)
            fkIk_rev = node.Reverse('Scap{}FkIk{}Rev'.format(part, side))
            self.scap_ctrl.shape.attr('fkIk') >> fkIk_rev.attr('ix')
            self.scap_ctrl.shape.attr('fkIk') >> self.fkIk_parcons.attr('{}W1'.format(self.scapAuto_ik_grp))
            fkIk_rev.ox >> self.fkIk_parcons.attr('{}W0'.format(self.scapAuto_fk_grp))
            
            self.scap_ctrl.shape.add_bool_tag('scapAuto', True)
            self.scap_ctrl.shape.add_str_tag('scapAutoFk', self.scap_fk_pma)
            self.scap_ctrl.shape.add_str_tag('scapAutoIk', self.scapAuto_ik_grp)

            #-- Cleanup
            for __obj in (self.scapAuto_grp, self.scapAim_on_grp, self.scapAim_off_grp):
                __obj.lhtrs()
                __obj.lhv()
            
            self.scap_ctrl.shape.attr('fkIk').hide = True

        #-- Setup limb lock
        if limb_lock:
            #-- Create group
            self.limbLock_grp = node.Transform('Limb{}Lock{}Grp'.format(part, side))
            self.limbLock_on_grp = node.Transform('Limb{}LockOn{}Grp'.format(part, side))
            self.limbLock_off_grp = node.Transform('Limb{}LockOff{}Grp'.format(part, side))
            self.limbLock_rev = node.Reverse('Limb{}Lock{}Rev'.format(part, side))
            
            mc.parent(self.limbLock_on_grp, self.limbLock_off_grp, self.limbLock_grp)
            mc.parent(self.limbLock_grp, self.rump_zro)

            self.limbLock_grp.snap(scap_tmpJnt)

            #-- Rig process
            util.parent_constraint( parent,
                                    self.limbLock_on_grp,
                                    st = 'y',
                                    mo = True )
        
            util.parent_constraint( parent,
                                    self.limbLock_off_grp,
                                    mo = True )
            
            self.lock_parcons = util.parent_constraint( self.limbLock_on_grp,
                                                        self.limbLock_off_grp,
                                                        self.rump_lock,
                                                        mo = True )
            
            self.scap_ctrl.add_attr('limbLock', min = 0, max = 1)

            self.scap_ctrl.attr('limbLock') >> self.limbLock_rev.attr('ix')
            self.scap_ctrl.attr('limbLock') >> self.lock_parcons.attr('{}W0'.format(self.limbLock_on_grp))
            self.limbLock_rev.attr('ox') >> self.lock_parcons.attr('{}W1'.format(self.limbLock_off_grp))

            if mc.objExists('Root_Jnt'):
                self.limbLock_parcons = util.parent_constraint( 'Root_Jnt',
                                                                self.limbLock_grp,
                                                                mo = True)
        mc.select(cl = True)

class ScapularAuto(object):

    def __init__( self , leg_ctrl = 'Leg_L_Ctrl',
                         scap_ctrl = 'Scap_L_Ctrl',
                         upleg_fk_ctrl = 'UpLegFk_L_Ctrl',
                         ankle_ik_ctrl = 'AnkleIk_L_Ctrl'
                ):
        
        '''
        '''

        if mc.objExists('{}.scapAuto'.format(scap_ctrl.shape)):
            upleg_fk_gmbl = util.get_gimbal(upleg_fk_ctrl)
            ankle_ik_gmbl = util.get_gimbal(ankle_ik_ctrl)

            #-- Connect switch fk ik
            leg_ctrl.attr('fkIk') >> scap_ctrl.shape.attr('fkIk')
            scap_ctrl.shape.attr('fkIk').lock = True

            #-- Connect fk ctrl
            fk_pma = util.register_node(mc.getAttr('{}.scapAutoFk'.format(scap_ctrl.shape)))
            upleg_fk_ctrl.attr('r') >> fk_pma.attr('i3').last()

            if upleg_fk_gmbl:
                upleg_fk_gmbl.attr('r') >> fk_pma.attr('i3').last()
                
            #-- Connect ik ctrl
            ik_grp = mc.getAttr('{}.scapAutoIk'.format(scap_ctrl.shape))

            if ankle_ik_gmbl:
                util.parent_constraint(ankle_ik_gmbl, ik_grp, mo = True)
            else:
                util.parent_constraint(ankle_ik_ctrl, ik_grp, mo = True)
            
            #-- Set value
            mc.setAttr('{}.autoScapula'.format(scap_ctrl), l = False, k = True)
            scap_ctrl.attr('autoScapula').value = 0.5

            #-- Cleanup
            scap_ctrl.shape.attr('scapAuto').remove()
            scap_ctrl.shape.attr('scapAutoFk').remove()
            scap_ctrl.shape.attr('scapAutoIk').remove()
        
        mc.select(cl = True)