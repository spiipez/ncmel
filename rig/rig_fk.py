# System modules.
from imp import reload

# Maya modules.
import maya.cmds as mc

# ncscript modules.
from ncTools.rig import node
from ncTools.rig import util
reload(node)
reload(util)

class Fk(object):

    def __init__( self , name = '',
                         tmp_jnt = [],
                         parent = '',
                         ctrl_grp = 'Ctrl_Grp',
                         axis = 'y',
                         chain = True,
                         connection = False,
                         ctrl_tip = False,
                         shape = 'square',
                         side = '',
                ):
        
        '''
        '''

        ##-- Prepare
        counts = len(tmp_jnt)
        side = util.set_side(side)
        sqsh_axis = 'xyz'.replace(axis,'')

        if counts == 1:
            chain = False
            
        self.fkCtrl_list = list()
        self.fkGmbl_list = list()
        self.fkCtrlZro_list = list()
        self.fkOfst_list = list()
        self.fkJnt_list = list()
        self.fkPosi_list = list()
        self.fkJntZro_list = list()
        self.fkPars_list = list()
    
        #-- Create main group
        if chain:
            self.fkCtrl_grp = node.Transform('{}Ctrl{}Grp'.format(name, side))

            if mc.objExists(parent):
                util.trs_constraint(parent, self.fkCtrl_grp, mo = False)

        #-- Rig process
        lenght = counts
        if ctrl_tip or not chain:
            lenght = counts+1

        ctrl_nums = list(range(1, counts+1))
                         
        for ix, num in enumerate(ctrl_nums):
            
            if chain:
                #-- Create joint position
                pos_jnt = node.Joint('{}{}Pos{}Jnt'.format(name, num, side), position = tmp_jnt[ix])
                posJnt_zro = util.group(pos_jnt, 'Zro')
                self.fkPosi_list.append(pos_jnt)
                self.fkJntZro_list.append(posJnt_zro)
                pos_jnt.attr('radius').value = 0.5

            if not ix == lenght-1:
                #-- Create joint
                fk_jnt = node.Joint('{}{}{}Jnt'.format(name, num, side), position = tmp_jnt[ix])
                self.fkJnt_list.append(fk_jnt)

                if not chain:
                    jnt_zro = util.group(fk_jnt, 'Zro')
                    self.fkJntZro_list.append(jnt_zro)
                else:
                    mc.parent(fk_jnt, pos_jnt)

                #-- Create controls
                ctrl = util.controller('{}{}{}Ctrl'.format(name, num, side), shape)
                gmbl = util.gimbal(ctrl)
                ctrl_zro = util.group(ctrl, 'Zro')
                ctrl_ofst = util.group(ctrl, 'Ofst')
                ctrl_par = util.group(ctrl, 'Par')
                ctrl_zro.snap(tmp_jnt[ix])
                
                self.fkCtrl_list.append(ctrl)
                self.fkGmbl_list.append(gmbl)
                self.fkCtrlZro_list.append(ctrl_zro)
                self.fkOfst_list.append(ctrl_ofst)
                self.fkPars_list.append(ctrl_par)
            
            #-- Manage hierarchy
            if chain:
                if ix == 0:
                    if not ix == lenght-1:
                        if mc.objExists(ctrl_grp):
                            mc.parent(self.fkCtrl_grp, ctrl_grp)
                    
                    if mc.objExists(parent): 
                        mc.parent(posJnt_zro, parent)

                    mc.parent(ctrl_zro, self.fkCtrl_grp)

                else:
                    if not ix == lenght-1:
                        print(ix , self.fkGmbl_list)
                        mc.parent(ctrl_zro, self.fkGmbl_list[ix-1])

                    mc.parent(posJnt_zro, self.fkPosi_list[ix-1])

            #-- Additional functions
            if not ix == lenght-1:
                if connection:
                    trn_pma = node.PlusMinusAverage('{}{}Trn{}Pma'.format(name, num, side))
                    rot_pma = node.PlusMinusAverage('{}{}Rot{}Pma'.format(name, num, side))

                    ctrl.attr('t') >> trn_pma.attr('i3').last()
                    gmbl.attr('t') >> trn_pma.attr('i3').last()

                    ctrl.attr('r') >> rot_pma.attr('i3').last()
                    gmbl.attr('r') >> rot_pma.attr('i3').last()
                    
                    if not chain:
                        trn_pma.attr('o3') >> fk_jnt.attr('t')
                        rot_pma.attr('o3') >> fk_jnt.attr('r')
                        ctrl.attr('s') >> fk_jnt.attr('s')
                    else:
                        trn_pma.attr('o3') >> pos_jnt.attr('t')
                        rot_pma.attr('o3') >> pos_jnt.attr('r')
                else:
                    if not chain:
                        util.parent_constraint(gmbl, fk_jnt, mo = False)
                        util.scale_constraint(gmbl, fk_jnt, mo = False)
                    else:
                        util.parent_constraint(gmbl, pos_jnt, mo = False)

                if chain:
                    util.add_squash_controller(ctrl, fk_jnt, ax = (sqsh_axis[0], sqsh_axis[1]))
            
            if chain:
                if not ix == 0:
                    if not ix == lenght-1:
                        util.add_offset_controller(self.fkCtrl_list[ix-1], ctrl_ofst, 'stretch', axis, 1)
                    else:
                        util.add_offset_controller(self.fkCtrl_list[ix-1], pos_jnt, 'stretch', axis, 1)
        
        if chain:
            if mc.objExists(ctrl_grp):
                util.local_world(self.fkCtrl_list[0], ctrl_grp, self.fkCtrl_grp, self.fkCtrlZro_list[0], 'orient')
        
            self.fkPosi_list[0].attr('ssc').value = 0
        
        #-- Cleanup
        if chain:
            for __ctrl in self.fkCtrl_list:
                __ctrl.lock_hide('sx', 'sy', 'sz', 'v')
        
        mc.select(cl = True)