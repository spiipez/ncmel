# System modules.
from imp import reload

# Maya modules.
import maya.cmds as mc

# ncscript modules.
from ncTools.rig import node
from ncTools.rig import util
reload(node)
reload(util)

class FingerMain(object):

    def __init__( self , parent  = 'Hand_L_Jnt' ,
                         ctrl_grp = 'Ctrl_Grp' ,
                         part    = '' ,
                         side    = 'L' ,
                ):
        
        '''
        '''

        ##-- Prepare
        self.side = util.set_side(side)
        self.part = part.capitalize()

        #-- Create main group
        _maingrp_ = 'Finger{}Ctrl{}Grp'.format(self.part, self.side)

        if mc.objExists(_maingrp_):
            self.fngrCtrl_main_grp = util.register_node(_maingrp_)
        else:
            self.fngrCtrl_main_grp = node.Transform(_maingrp_)
            util.trs_constraint(parent, self.fngrCtrl_main_grp, mo = False)
            mc.parent(self.fngrCtrl_main_grp, ctrl_grp)

            self.fngrCtrl_main_grp.lhtrs()

class HandSmart(FingerMain):

    def __init__( self , handSmart_tmpJnt = 'HandSmart_L_TmpJnt',
                         parent = 'Hand_L_Jnt',
                         ctrl_grp = 'Ctrl_Grp',
                         part = '',
                         side = 'L',
                ):
        
        '''
        '''

        super(HandSmart, self).__init__(parent, ctrl_grp, part, side)

        #-- Create main group
        self.smartCtrl_grp = node.Transform('HandSmart{}Ctrl{}Grp'.format(self.part, self.side))
        self.smartCtrl_grp.snap(parent)

        mc.parent(self.smartCtrl_grp, self.fngrCtrl_main_grp)

        #-- Create controls
        self.smart_ctrl = util.controller('HandSmart{}{}Ctrl'.format(self.part, self.side), 'sphere', 'pink')
        self.smart_zro = util.group(self.smart_ctrl, 'Zro')
        self.smart_zro.snap(handSmart_tmpJnt)

        mc.parent(self.smart_zro, self.smartCtrl_grp)
        
        #-- Adjust shape controls
        self.smart_ctrl.scale_shape(0.25)

        #-- Cleanup
        self.smart_ctrl.lock_hide('tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v')
        
        mc.select(cl = True)


class Finger(FingerMain):

    def __init__( self , fngr = 'Index',
                         fngr_tmpJnt = ['Index1_L_TmpJnt',
                                        'Index2_L_TmpJnt',
                                        'Index3_L_TmpJnt',
                                        'Index4_L_TmpJnt',
                                        'Index5_L_TmpJnt'],
                         arm_ctrl = 'Arm_L_Ctrl',
                         smart_ctrl = 'HandSmart_L_Ctrl',
                         parent = 'Hand_L_Jnt', 
                         ctrl_grp = 'Ctrl_Grp',
                         setup_value = True,
                         part = '',
                         side = 'L',
                ):
        
        '''
        '''

        super(Finger, self).__init__(parent, ctrl_grp, part, side)

        ##-- Prepare
        name = '{}{}'.format(fngr, self.part)
        rotate_order = 'yzx'
        side_value = 1

        if 'R' in self.side:
            side_value = -1

        self.fngrJnt_list = list()
        self.fngrCtrl_list = list()
        self.fngrZro_list = list()
        self.fngrDrv_list = list()
        self.fngrDrvMdv_list = list()
        self.fngrRxPma_list = list()
        self.fngrRyPma_list = list()
        self.fngrRzPma_list = list()
        self.fngrTyPma_list = list()

        fngr_member = len(fngr_tmpJnt)

        #-- Create main group
        self.fngrCtrl_grp = node.Transform('{}Ctrl{}Grp'.format(name, self.side))
        self.fngrCup_grp = node.Transform('{}Cup{}Grp'.format(name, self.side))
        
        self.fngrCtrl_grp.snap(parent)
        self.fngrCup_grp.snap(parent)

        mc.parent(self.fngrCup_grp, self.fngrCtrl_grp)
        mc.parent(self.fngrCtrl_grp, self.fngrCtrl_main_grp)

        #-- Create controls
        self.fngrAttr_ctrl = util.controller('{}Attr{}Ctrl'.format(name, self.side), 'stickCircle', 'yellow')
        self.fngrAttr_zro = util.group(self.fngrAttr_ctrl, 'Zro')
        mc.parent(self.fngrAttr_zro, self.fngrCup_grp)

        self.fngrAttr_ctrl.lhtrs()
        self.fngrAttr_ctrl.lhv()

        #-- Adjust shape controls
        self.fngrAttr_ctrl.scale_shape(0.5)
        
        #-- Adjust shape controls
        if 'L' in side:
            self.fngrAttr_ctrl.rotate_shape((90, 0, 0))
        else:
            self.fngrAttr_ctrl.rotate_shape((-90, 0, 0))

        #-- Additional attribute
        self.fngrAttr_ctrl.add_attr('fold')
        self.fngrAttr_ctrl.add_attr('twist')
        self.fngrAttr_ctrl.add_attr('slide')
        self.fngrAttr_ctrl.add_attr('scruch')
        self.fngrAttr_ctrl.add_attr('stretch')
        self.fngrAttr_ctrl.add_attr('spread')

        self.fngrAttr_ctrl.shape.add_attr('detailControls', min = 0, max = 1, dv = 1)

        #-- Detail controls
        for ix, tmp in enumerate(fngr_tmpJnt):
            index = ix+1
            #-- Create joint
            self.fngr_jnt = node.Joint('{}{}{}Jnt'.format(name, index, self.side), position = tmp)
            self.fngr_jnt.attr('ssc').value = 0

            self.fngrJnt_list.append(self.fngr_jnt)

            if not tmp == fngr_tmpJnt[-1]:
                #-- Create controls
                self.fngr_ctrl = util.controller('{}{}{}Ctrl'.format(name, index, self.side), 'hexagon2', 'red')
                self.fngr_zro = util.group(self.fngr_ctrl, 'Zro')
                self.fngr_drv = util.group(self.fngr_ctrl, 'Drv')
                
                self.fngr_zro.snap(tmp)
                self.fngr_ctrl.lhv()

                mc.parent(self.fngr_zro, self.fngrCup_grp)

                #-- Adjust shape controls
                self.fngr_ctrl.scale_shape(0.35)
                
                #-- Set rotate order
                for __each in (self.fngr_jnt, self.fngr_ctrl, self.fngr_drv):
                    __each.rotate_order = rotate_order
                
                #-- Rig process
                util.parent_constraint(self.fngr_ctrl, self.fngr_jnt, mo = False)
                self.fngr_ctrl.attr('s') >> self.fngr_jnt.attr('s')

                #-- Setup Slide, Scruch, Stretch
                self.fngrDrv_mdv = node.MultiplyDivide('{}{}Drv{}Mdv'.format(name, index, self.side))
                self.fngrRx_pma = node.PlusMinusAverage('{}{}Rx{}Pma'.format(name, index, self.side))
                self.fngrRy_pma = node.PlusMinusAverage('{}{}Ry{}Pma'.format(name, index, self.side))
                self.fngrRz_pma = node.PlusMinusAverage('{}{}Rz{}Pma'.format(name, index, self.side))
                self.fngrTy_pma = node.PlusMinusAverage('{}{}Ty{}Pma'.format(name, index, self.side))

                self.fngrAttr_ctrl.attr('slide') >> self.fngrDrv_mdv.attr('i1x')
                self.fngrAttr_ctrl.attr('scruch') >> self.fngrDrv_mdv.attr('i1y')
                self.fngrAttr_ctrl.attr('stretch') >> self.fngrDrv_mdv.attr('i1z')

                self.fngrDrv_mdv.attr('ox') >> self.fngrRx_pma.attr('i1').last() # slide(x)
                self.fngrDrv_mdv.attr('oy') >> self.fngrRx_pma.attr('i1').last() # scruch(y)
                self.fngrDrv_mdv.attr('oz') >> self.fngrTy_pma.attr('i1').last() # stretch(z)

                self.fngrRx_pma.attr('o1') >> self.fngr_drv.attr('rx')
                self.fngrRy_pma.attr('o1') >> self.fngr_drv.attr('ry')
                self.fngrRz_pma.attr('o1') >> self.fngr_drv.attr('rz')
                self.fngrTy_pma.attr('o1') >> self.fngr_drv.attr('ty')

                #-- Setup attribute value
                if ix == 0:
                    self.fngrDrv_mdv.attr('i2z').value = 0
                else:
                    self.fngrDrv_mdv.attr('i2z').value = side_value
                
                #-- Append to list
                self.fngrCtrl_list.append(self.fngr_ctrl)
                self.fngrZro_list.append(self.fngr_zro)
                self.fngrDrv_list.append(self.fngr_drv)
                self.fngrDrvMdv_list.append(self.fngrDrv_mdv)
                self.fngrRxPma_list.append(self.fngrRx_pma)
                self.fngrRyPma_list.append(self.fngrRy_pma)
                self.fngrRzPma_list.append(self.fngrRz_pma)
                self.fngrTyPma_list.append(self.fngrTy_pma)

        #-- Setup Fold, Twist, Spread
        self.fngrFold_mult = node.MultDoubleLinear('{}Fold{}Mult'.format(name, self.side))
        self.fngrTwist_mult = node.MultDoubleLinear('{}Twist{}Mult'.format(name, self.side))
        self.fngrSpread_mult = node.MultDoubleLinear('{}Spread{}Mult'.format(name, self.side))
            
        self.fngrAttr_ctrl.attr('fold') >> self.fngrFold_mult.attr('i1')
        self.fngrAttr_ctrl.attr('twist') >> self.fngrTwist_mult.attr('i1')
        self.fngrAttr_ctrl.attr('spread') >> self.fngrSpread_mult.attr('i1')

        self.fngrFold_mult.attr('i2').value = -9
        self.fngrTwist_mult.attr('i2').value = 1
        self.fngrSpread_mult.attr('i2').value = 1
        
        fngr_num = list(range(fngr_member-1))

        for i in fngr_num:
            if not i == 0:
                self.fngrFold_mult.attr('o') >> self.fngrRxPma_list[i].attr('i1').last()
                self.fngrTwist_mult.attr('o') >> self.fngrRyPma_list[i].attr('i1').last()

        self.fngrSpread_mult.attr('o') >> self.fngrRzPma_list[0].attr('i1').last()
        self.fngrAttr_ctrl.shape.attr('detailControls') >> self.fngrZro_list[0].attr('v')

        #-- Additional attribute (Attr, Axis, Order)
        fngr_info_list = [('Fist', 'xyz', fngr_num),
                          ('Slide', 'x', fngr_num),
                          ('Scruch', 'x', fngr_num),
                          ('BaseSpread', 'z', 1),
                          ('Spread', 'z', 2),
                          ('RelaxIn', 'x', fngr_num),
                          ('RelaxOut', 'x', fngr_num)]
    
        hand_info_list = [('Smart', 'xz', list(range(2))),
                          ('Cup', 'y', 1 )]

        for ctrl, info in zip([arm_ctrl, smart_ctrl], [fngr_info_list, hand_info_list]):
            if ctrl:
                ctrl = util.register_node(ctrl)
                if ctrl == arm_ctrl:
                    ctrl.add_divide_attr('finger')

                ctrl.shape.add_divide_attr('{}'.format(fngr))

                for fngr_attr, fngr_axis, fngr_order in info:
                    if not fngr_attr == 'Cup':
                        if not str(ctrl) == str(smart_ctrl):
                            ctrl_attr = '{}.{}'.format(ctrl, fngr_attr)
                            if not mc.objExists(ctrl_attr):
                                if fngr_attr == 'Fist':
                                    ctrl.add_attr(fngr_attr, min = -2.5, max = 10)
                                else:
                                    ctrl.add_attr(fngr_attr)
                        
                        order = fngr_order
                        if not type(fngr_order) == list:
                            order = [fngr_order-1]

                        for i in order:
                            if i < (fngr_member-1):
                                index = i+1
                                fngr_index = '{}{}'.format(fngr, index)
                                fngr_mdv = node.MultiplyDivide('{}{}{}{}Mdv'.format(name, index, fngr_attr, self.side))
                                fngr_mdv.attr('i2').value = (0,0,0)

                                fngr_mdv.attr('ox') >> self.fngrRxPma_list[i].attr('i1').last()
                                fngr_mdv.attr('oy') >> self.fngrRyPma_list[i].attr('i1').last()
                                fngr_mdv.attr('oz') >> self.fngrRzPma_list[i].attr('i1').last()
                    
                                for axis in fngr_axis:
                                    axis_attr = '{}{}R{}'.format(fngr_index, fngr_attr, axis)
                                    ctrl.shape.add_attr(axis_attr)
                                    ctrl.shape.attr(axis_attr) >> fngr_mdv.attr('i2{}'.format(axis))
                                    
                                    if str(ctrl) == str(smart_ctrl):
                                        ctrl.attr('r{}'.format(axis)) >> fngr_mdv.attr('i1{}'.format(axis))
                                    else :
                                        ctrl.attr(fngr_attr) >> fngr_mdv.attr('i1{}'.format(axis))

                                        if fngr_attr == 'Scruch':
                                            ctrl.shape.attr(axis_attr) >> self.fngrDrvMdv_list[i].attr('i2y')
                                        
                                        if fngr_attr == 'Slide':
                                            ctrl.shape.attr(axis_attr) >> self.fngrDrvMdv_list[i].attr('i2x')
                    else:
                        cup_attr = '{}{}{}R{}'.format(fngr, fngr_order, fngr_attr, fngr_axis)
                        ctrl.shape.add_attr(cup_attr)

                        cup_mult = node.MultDoubleLinear('{}{}CupR{}{}Mult'.format(name, fngr_order, fngr_axis, self.side))
                        ctrl.attr('r{}'.format(fngr_axis)) >> cup_mult.attr('input1')
                        ctrl.shape.attr(cup_attr) >> cup_mult.attr('input2')
                        cup_mult.attr('output') >> self.fngrCup_grp.attr('r{}'.format(fngr_axis))
        
        #-- Setup position finger attr control
        if fngr_member > 2:
            util.trs_constraint(self.fngrJnt_list[1], self.fngrAttr_zro, mo = False)
        else:
            util.trs_constraint(self.fngrJnt_list[0], self.fngrAttr_zro, mo = False)

        #-- Manage hierarchy
        mc.parent(self.fngrJnt_list[0], parent)

        for i in range(fngr_member):
            if not i == 0:
                mc.parent(self.fngrJnt_list[i], self.fngrJnt_list[i-1])

                if not i == (fngr_member-1):
                    mc.parent(self.fngrZro_list[i], self.fngrCtrl_list[i-1])
        
        if setup_value == True:
            FingerSetUp(fngr, arm_ctrl, smart_ctrl)
        
        mc.select(cl = True)

class FingerSetUp(object):

    def __init__( self , fngr = '', 
                         main_ctrl = '' ,
                         smart_ctrl = '' ):

        '''
        '''

        fngr_info = dict()
        smart_info = dict()

        if 'Thumb' in fngr:
            fngr_info = { 1 : [( 'Fist', 'xyz', [0,0,0]),
                               ( 'Slide', 'x', [0]),
                               ( 'Scruch', 'x', [0]),
                               ( 'BaseSpread', 'z', [0]),
                               ( 'BaseBreak', 'z', [0]),
                               ( 'BaseFlex', 'x', [0]),
                               ( 'RelaxIn', 'x', [0]),
                               ( 'RelaxOut', 'x', [0])],

                          2 : [( 'Fist', 'xyz', [-4.5,0,0]),
                               ( 'Slide', 'x', [3.5]),
                               ( 'Scruch', 'x', [3.5]),
                               ( 'Spread', 'z', [0]),
                               ( 'Break', 'z', [0]),
                               ( 'Flex', 'x', [0]),
                               ( 'FanIn', 'x', [0]),
                               ( 'FanOut', 'x', [0]),
                               ( 'RelaxIn', 'x', [0]),
                               ( 'RelaxOut', 'x', [0])],
 
                          3 : [( 'Fist', 'xyz', [-9,0,0]),
                               ( 'Slide', 'x', [-8]),
                               ( 'Scruch', 'x', [-8]),
                               ( 'RelaxIn', 'x', [0]),
                               ( 'RelaxOut', 'x', [0])] }


        if 'Index' in fngr:
            fngr_info = { 1 : [( 'Fist', 'xyz', [0,0,0]),
                               ( 'Slide', 'x', [0]),
                               ( 'Scruch', 'x', [1.5]),
                               ( 'BaseSpread', 'z', [-1.5]),
                               ( 'BaseBreak', 'z', [-4.5]),
                               ( 'BaseFlex', 'x', [-9]),
                               ( 'RelaxIn', 'x', [-0.5]),
                               ( 'RelaxOut', 'x', [0])],

                          2 : [( 'Fist', 'xyz', [-9,0,0]),
                               ( 'Slide', 'x', [3.5]),
                               ( 'Scruch', 'x', [3.5]),
                               ( 'Spread', 'z', [-1.5]),
                               ( 'Break', 'z', [-4.5]),
                               ( 'Flex', 'x', [-9]),
                               ( 'RelaxIn', 'x', [-7.5]),
                               ( 'RelaxOut', 'x', [-1])],
 
                          3 : [( 'Fist', 'xyz', [-9,0,0]),
                               ( 'Slide', 'x', [-8]),
                               ( 'Scruch', 'x', [-8]),
                               ( 'RelaxIn', 'x', [-7.5]),
                               ( 'RelaxOut', 'x', [-1])],
 
                          4 : [( 'Fist', 'xyz', [-9,0,0]),
                               ( 'Slide', 'x', [4.5]),
                               ( 'Scruch', 'x', [-8]),
                               ( 'RelaxIn', 'x', [-7.5]),
                               ( 'RelaxOut', 'x', [-1])] }

            smart_info = { 1 : [( 'Smart', 'xz', [0.25,0.25]),
                               ( 'Cup', 'y', [0])],

                           2 : [( 'Smart', 'xz', [0.25,0.25])] }

        if 'Middle' in fngr:
            fngr_info = { 1 : [( 'Fist', 'xyz', [0,0,0]),
                               ( 'Slide', 'x', [0]),
                               ( 'Scruch', 'x', [1.5]),
                               ( 'BaseSpread', 'z', [0]),
                               ( 'BaseBreak', 'z', [-4.5]),
                               ( 'BaseFlex', 'x', [-9]),
                               ( 'RelaxIn', 'x', [-0.2]),
                               ( 'RelaxOut', 'x', [-0.5])],

                          2 : [( 'Fist', 'xyz', (-9,0,0)),
                               ( 'Slide', 'x', [3.5]),
                               ( 'Scruch', 'x', [3.5]),
                               ( 'Spread', 'z', [0]),
                               ( 'Break', 'z', [-4.5]),
                               ( 'Flex', 'x', [-9]),
                               ( 'RelaxIn', 'x', [-5]),
                               ( 'RelaxOut', 'x', [-2.5])],
 
                          3 : [( 'Fist', 'xyz', [-9,0,0]),
                               ( 'Slide', 'x', [-8]),
                               ( 'Scruch', 'x', [-8]),
                               ( 'RelaxIn', 'x', [-5]),
                               ( 'RelaxOut', 'x', [-2.5])],
 
                          4 : [( 'Fist', 'xyz', [-9,0,0]),
                               ( 'Slide', 'x', [4.5]),
                               ( 'Scruch', 'x', [-8]),
                               ( 'RelaxIn', 'x', [-5]),
                               ( 'RelaxOut', 'x', [-2.5])] }

            smart_info = { 1 : [( 'Smart', 'xz', [0.75,0.75]),
                                ( 'Cup', 'y', [0.25])],

                           2 : [( 'Smart', 'xz', [0.75,0.75])] }

        if 'Ring' in fngr:
            fngr_info = { 1 : [( 'Fist', 'xyz', [0,0,0]),
                               ( 'Slide', 'x', [0]),
                               ( 'Scruch', 'x', [1.5]),
                               ( 'BaseSpread', 'z', [1.5]),
                               ( 'BaseBreak', 'z', [-4.5]),
                               ( 'BaseFlex', 'x', [-9]),
                               ( 'RelaxIn', 'x', [-0.05]),
                               ( 'RelaxOut', 'x', [-1]),
                               ( 'HandCupOut', 'xyz', [-1.65,-2,0])],

                          2 : [( 'Fist', 'xyz', [-9,0,0]),
                               ( 'Slide', 'x', [3.5]),
                               ( 'Scruch', 'x', [3.5]),
                               ( 'Spread', 'z', [1.5]),
                               ( 'Break', 'z', [-4.5]),
                               ( 'Flex', 'x', [-9]),
                               ( 'RelaxIn', 'x', [-2.5]),
                               ( 'RelaxOut', 'x', [-5])],
 
                          3 : [( 'Fist', 'xyz', [-9,0,0]),
                               ( 'Slide', 'x', [-8]),
                               ( 'Scruch', 'x', [-8]),
                               ( 'RelaxIn', 'x', [-2.5]),
                               ( 'RelaxOut', 'x', [-5]),
                               ( 'HandCupOut', 'xyz', [0,0,0])],
 
                          4 : [( 'Fist', 'xyz', [-9,0,0]),
                               ( 'Slide', 'x', [4.5]),
                               ( 'Scruch', 'x', [-8]),
                               ( 'RelaxIn', 'x', [-2.5]),
                               ( 'RelaxOut', 'x', [-5]),
                               ( 'HandCupOut', 'xyz', [0,0,0])] }

            smart_info = { 1 : [( 'Smart', 'xz', [1.25,1.25]),
                               ( 'Cup', 'y', [1])],

                          2 : [( 'Smart', 'xz', [1.25,1.25])] }

        if 'Pinky' in fngr:
            fngr_info = { 1 : [( 'Fist', 'xyz', [0,0,0]),
                               ( 'Slide', 'x', [0]),
                               ( 'Scruch', 'x', [1.5]),
                               ( 'BaseSpread', 'z', [3.5]),
                               ( 'BaseBreak', 'z', [-4.5]),
                               ( 'BaseFlex', 'x', [-9]),
                               ( 'RelaxOut', 'x', [-2]),
                               ( 'HandCupOut', 'xyz', [-2.45,-2.15,-0.6])],

                          2 : [( 'Fist', 'xyz', [-9,0,0]),
                               ( 'Slide', 'x', [3.5]),
                               ( 'Scruch', 'x', [3.5]),
                               ( 'Spread', 'z', [3.5]),
                               ( 'Break', 'z', [-4.5]),
                               ( 'Flex', 'x', [-9]),
                               ( 'RelaxIn', 'x', [-1]),
                               ( 'RelaxOut', 'x', [-7.5])],
 
                          3 : [( 'Fist', 'xyz', [-9,0,0]),
                               ( 'Slide', 'x', [-8]),
                               ( 'Scruch', 'x', [-8]),
                               ( 'RelaxIn', 'x', [-1]),
                               ( 'RelaxOut', 'x', [-7.5])],
 
                          4 : [( 'Fist', 'xyz', [-9,0,0]),
                               ( 'Slide', 'x', [4.5]),
                               ( 'Scruch', 'x', [-8]),
                               ( 'RelaxIn', 'x', [-1]),
                               ( 'RelaxOut', 'x', [-7.5])] }

            smart_info = { 1 : [( 'Smart', 'xz', [1.75,1.75]),
                                ( 'Cup', 'y', [2])],

                           2 : [( 'Smart', 'xz', [1.75,1.75])] }

        #-- Set finger value
        for ctrl, info in zip([main_ctrl, smart_ctrl], [fngr_info, smart_info]):
            if ctrl:
                for i in range(1, len(info)+1):
                    for fngr_attr, fngr_axis, fngr_value in info[i]:
                        for j in range(len(fngr_axis)):
                            name_attr = '{}{}{}R{}'.format(fngr, i, fngr_attr, fngr_axis[j])
                            if mc.objExists('{}.{}'.format(ctrl.shape, name_attr)):
                                ctrl.shape.attr('{}'.format(name_attr)).value = (fngr_value[j])