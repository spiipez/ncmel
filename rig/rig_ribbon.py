# System modules.
from imp import reload

# Maya modules.
import maya.cmds as mc

# ncscript modules.
from ncTools.rig import node
from ncTools.rig import util
reload(node)
reload(util)

def run(name = '', posiA = '', posiB = '', axis = '', side = '', subdiv = 1, constraint = True):
    ''' Subdiv 0 = 3 Detail Joint, Subdiv 1 = 5 Detail Joint
    '''
    
    dist = util.distance_between(util.get_position(posiA), 
                                 util.get_position(posiB))
    
    ribbon = Ribbon(name, axis, side, dist, subdiv)
    ribbon.rbnCtrl_grp.snap_point(posiA)
    ribbon.rbnCtrl_grp.snap_aim(posiB,
                                aim = ribbon.aimvec, 
                                u = ribbon.upvec, 
                                wuo = posiA, 
                                wu = ribbon.upvec)

    if constraint:
        util.parent_constraint(posiA, ribbon.rbnCtrl_grp, mo = True)
        util.parent_constraint(posiA, ribbon.rbn_root_ctrl)
        util.parent_constraint(posiB, ribbon.rbn_end_ctrl)
        
        for _ctrl, _zro in zip([ribbon.rbn_root_ctrl, ribbon.rbn_end_ctrl],
                               [ribbon.rbn_root_zro, ribbon.rbn_end_zro]):
            
            _ctrl.lock_hide('tx', 'ty', 'tz', 'rx', 'ry', 'rz')
            _zro.hide()

    return ribbon.rbnCtrl_grp, ribbon.rbnSkin_grp, ribbon.rbnStill_grp, \
           ribbon.rbn_ctrl, ribbon.rbn_root_ctrl, ribbon.rbn_end_ctrl

class RibbonData(object):
    
    def __init__(self, axis):

        if axis == 'x+':
            self.aimvec = (1, 0, 0)
            self.upvec = (0, 0, 1)
            self.rotate = (0, 0, -90)
            self.rotate_order = 'xyz'
            
        elif axis == 'x-':
            self.aimvec = (-1, 0, 0)
            self.upvec = (0, 0, 1)
            self.rotate = (0, 0, 90)
            self.rotate_order = 'xyz'

        elif axis == 'y+':
            self.aimvec =  (0, 1, 0)
            self.upvec = (0, 0, 1)
            self.rotate = (0, 0, 0)
            self.rotate_order = 'yzx'
            
        elif axis == 'y-':
            self.aimvec = (0, -1, 0)
            self.upvec = (0, 0, 1)
            self.rotate = (0, 0, 180)
            self.rotate_order = 'yzx'
        
        elif axis == 'z+':
            self.aimvec = (0, 0, 1)
            self.upvec = (0, 1, 0)
            self.rotate = (90, 0, 180)
            self.rotate_order = 'zxy'
        
        elif axis == 'z-':
            self.aimvec = (0, 0, -1)
            self.upvec = (0, 1, 0)
            self.rotate = (-90, 0, 0)
            self.rotate_order = 'zxy'

class RibbonMain(RibbonData):

    def __init__( self , name = '',
                         axis = 'y+',
                         side = 'L',
                         dist = 1 
                ):
    
        super(RibbonMain, self).__init__(axis)
        
        ##-- Prepare
        self.side = util.set_side(side)
        self.aim_axis = axis[0]
        self.sqsh_axis = 'xyz'.replace(self.aim_axis,'')
    
        #-- Create main group
        self.rbnCtrl_grp = node.Transform('{}RbnCtrl{}Grp'.format(name, self.side))

        #-- Create controls
        self.rbn_root_ctrl = util.controller('{}RbnRoot{}Ctrl'.format(name, self.side), 'locator', 'yellow')
        self.rbn_root_zro = util.group(self.rbn_root_ctrl, 'Zro')

        self.rbn_end_ctrl = util.controller('{}RbnEnd{}Ctrl'.format(name, self.side), 'locator', 'yellow')
        self.rbn_end_zro = util.group(self.rbn_end_ctrl, 'Zro')

        self.rbn_ctrl = util.controller('{}Rbn{}Ctrl'.format(name, self.side), 'circle', 'yellow')
        self.rbn_zro = util.group(self.rbn_ctrl, 'Zro')
        self.rbn_aim = util.group(self.rbn_ctrl, 'Aim')

        #-- Create joint aim group
        self.rbn_root_aim = node.Transform('{}RbnRootJntAim{}Grp'.format(name, self.side))
        self.rbn_end_aim = node.Transform('{}RbnEndJntAim{}Grp'.format(name, self.side))

        mc.parent(self.rbn_root_aim, self.rbn_root_ctrl)
        mc.parent(self.rbn_end_aim, self.rbn_end_ctrl)
        
        #-- Adjust shape controls
        for _ctrl in (self.rbn_root_ctrl, self.rbn_end_ctrl, self.rbn_ctrl):
            _ctrl.scale_shape(dist*0.16)

        self.rbn_ctrl.rotate_shape(self.rotate)
        
        #-- Set rotate order
        self.rbn_ctrl.rotate_order = self.rotate_order
        
        #-- Rig process
        _val = 1
        if '-' in axis[-1]:
            _val = -1

        self.rbn_zro.attr('t{}'.format(self.aim_axis)).value = (dist/2.0) * _val
        self.rbn_end_zro.attr('t{}'.format(self.aim_axis)).value = dist * _val

        util.point_constraint( self.rbn_root_ctrl, 
                               self.rbn_end_ctrl, 
                               self.rbn_zro, 
                               mo = False )
        
        util.aim_constraint( self.rbn_end_ctrl,
                             self.rbn_root_aim,
                             aim = self.aimvec,
                             u = self.upvec,
                             wut = "objectrotation",
                             wu = self.upvec,
                             wuo = self.rbn_root_zro,
                             mo = False )
        
        util.aim_constraint( self.rbn_root_ctrl,
                             self.rbn_end_aim,
                             aim = [(a*-1) for a in self.aimvec],
                             u = self.upvec,
                             wut = "objectrotation",
                             wu = self.upvec,
                             wuo = self.rbn_end_zro,
                             mo = False )
         
        util.aim_constraint( self.rbn_end_ctrl,
                             self.rbn_aim,
                             aim = self.aimvec,
                             u = self.upvec,
                             wut = "objectrotation",
                             wu = self.upvec,
                             wuo = self.rbn_zro,
                             mo = False )
        
        #-- Manage hierarchy
        mc.parent(self.rbn_zro, self.rbn_root_zro, self.rbn_end_zro, self.rbnCtrl_grp)
        
        #-- Cleanup
        for _obj in (self.rbn_root_ctrl, self.rbn_end_ctrl):
            _obj.lock_hide('s{}'.format(self.aim_axis))
        
        self.rbn_ctrl.lock_hide('s{}'.format(self.aim_axis), 'v')

class Ribbon(RibbonMain):

    def __init__( self , name = '',
                         axis = 'y+',
                         side = 'L',
                         dist = 1,
                         subdiv = 1
                ):
    
        super(Ribbon, self).__init__(name, axis, side, dist)
        
        ##-- Prepare
        numjnts = (subdiv*2)+3

        #-- Create main group
        self.rbnSkin_grp = node.Transform('{}RbnSkin{}Grp'.format(name, self.side))
        self.rbnDtl_grp = node.Transform('{}RbnDtl{}Grp'.format(name, self.side))
        self.rbnStill_grp = node.Transform('{}RbnStill{}Grp'.format(name, self.side))

        util.parent_constraint(self.rbnCtrl_grp, self.rbnSkin_grp, mo = False)
        util.scale_constraint(self.rbnCtrl_grp, self.rbnSkin_grp, mo = False)

        self.rbn_ctrl.shape.add_attr('detailControl', min = 0, max = 1, dv = 0)
        
        #-- Setup distance
        for _ctrl in (self.rbn_root_ctrl.shape, self.rbn_end_ctrl.shape):
            for _attr in ('localTranslate', 'localRotate', 'localScale'):
                _ctrl.add_vector_attr(attr_name = _attr, k = False)
        
        self.rbn_ctrl.shape.add_attr('originalLen', k = False)
        self.rbn_ctrl.shape.add_attr('currentLen', k = False)
        
        self.rbn_ctrl.shape.attr('originalLen').value = dist
        self.rbn_ctrl.shape.attr('originalLen').lock = True

        self.dist = node.DistanceBetween('{}Rbn{}Dist'.format(name, self.side))
        self.root_multMtx = node.MultMatrix('{}RbnRoot{}MultMtx'.format(name, self.side))
        self.end_multMtx = node.MultMatrix('{}RbnEnd{}MultMtx'.format(name, self.side))
        self.root_decMtx = node.DecomposeMatrix('{}RbnRoot{}DecMtx'.format(name, self.side))
        self.end_decMtx = node.DecomposeMatrix('{}RbnEnd{}DecMtx'.format(name, self.side))
        self.dist_div = node.MultiplyDivide('{}RbnDist{}Div'.format(name, self.side))

        self.rbn_root_ctrl.attr('matrix') >> self.root_multMtx.attr('matrixIn[0]')
        self.rbn_root_zro.attr('matrix') >> self.root_multMtx.attr('matrixIn[1]')

        self.root_multMtx.attr('matrixSum') >> self.root_decMtx.attr('inputMatrix')
        self.rbn_root_ctrl.attr('ro') >> self.root_decMtx.attr('inputRotateOrder')

        self.root_decMtx.attr('outputTranslate') >> self.rbn_root_ctrl.shape.attr('localTranslate')
        self.root_decMtx.attr('outputRotate') >> self.rbn_root_ctrl.shape.attr('localRotate')
        self.root_decMtx.attr('outputScale') >> self.rbn_root_ctrl.shape.attr('localScale')

        self.rbn_end_ctrl.attr('matrix') >> self.end_multMtx.attr('matrixIn[0]')
        self.rbn_end_zro.attr('matrix') >> self.end_multMtx.attr('matrixIn[1]')

        self.end_multMtx.attr('matrixSum') >> self.end_decMtx.attr('inputMatrix')
        self.rbn_end_ctrl.attr('ro') >> self.end_decMtx.attr('inputRotateOrder')

        self.end_decMtx.attr('outputTranslate') >> self.rbn_end_ctrl.shape.attr('localTranslate')
        self.end_decMtx.attr('outputRotate') >> self.rbn_end_ctrl.shape.attr('localRotate')
        self.end_decMtx.attr('outputScale') >> self.rbn_end_ctrl.shape.attr('localScale')

        self.rbn_root_ctrl.shape.attr('localTranslate') >> self.dist.attr('p1')
        self.rbn_end_ctrl.shape.attr('localTranslate') >> self.dist.attr('p2')
        self.dist.attr('d') >> self.rbn_ctrl.shape.attr('currentLen')

        self.dist_div.attr('op').value = 2
        self.rbn_ctrl.shape.attr('currentLen') >> self.dist_div.attr('i1x')
        self.rbn_ctrl.shape.attr('originalLen') >> self.dist_div.attr('i2x')
        
        #-- Setup nurbsSurface
        self.rbn_nrb = util.register_node(mc.nurbsPlane( p = (0, dist/2.0, 0), 
                                                         ax = (0, 0, 1), 
                                                         lr = dist, 
                                                         d = 3, 
                                                         u = 1, 
                                                         v = 2, 
                                                         ch = 0, 
                                                         n = '{}Rbn{}Nrb'.format(name, self.side))[0])

        self.rbn_nrb.attr('r').value = (self.rotate)
        self.rbn_nrb.freeze()

        mc.rebuildSurface(self.rbn_nrb, ch = 0, su = 1, sv = 2, du = 1, dv = 3)
        
        rbn_clstr, rbn_handle = util.register_node(mc.cluster(self.rbn_nrb))
        rbn_all_clstr, rbn_all_handle = util.register_node(mc.cluster(self.rbn_nrb))
        
        rbn_handle.name = '{}Rbn{}Handle'.format(name, self.side)
        rbn_all_handle.name = '{}RbnAll{}Handle'.format(name, self.side)

        self.rbn_ctrl.attr('t') >> rbn_handle.attr('t')
        self.rbn_ctrl.attr('r') >> rbn_handle.attr('r')

        rbn_handle.hide()
        rbn_all_handle.hide()
        
        val_wgt = [0, 0.4, 1, 0.4, 0]
        lst_wgt = [(0,5), (1,6), (2,7), (3,8), (4,9)]
        
        for i in range(5):
            wgt_index = 'w{}'.format(i)
            self.rbn_nrb.add_attr(wgt_index, min = 0, max = 1)
            self.rbn_nrb.attr(wgt_index).value = val_wgt[i]
            
            for j in range(2):
                self.rbn_nrb.attr(wgt_index) >> rbn_clstr.attr('weightList[0].weights[{}]'.format(lst_wgt[i][j]))
        
        self.dist_div.attr('ox') >> rbn_all_handle.attr('s{}'.format(self.aim_axis))
        
        #-- Setup twist
        self.rbn_ctrl.add_divide_attr('twist')
        self.rbn_ctrl.add_attr('autoTwist', min = 0, max = 1)
        self.rbn_ctrl.add_attr('rootTwist')
        self.rbn_ctrl.add_attr('endTwist')

        self.rbn_ctrl.shape.add_attr('rootTwistAmp', k = False)
        self.rbn_ctrl.shape.add_attr('endTwistAmp', k = False)

        self.rbn_ctrl.shape.add_attr('rootAbsTwist', k = False)
        self.rbn_ctrl.shape.add_attr('endAbsTwist', k = False)

        self.rbn_ctrl.shape.attr('rootTwistAmp').value = 1
        self.rbn_ctrl.shape.attr('endTwistAmp').value = 1
        
        self.root_twist_amp = node.MultDoubleLinear('{}RbnAmpRootTwist{}Mult'.format(name, self.side))
        self.end_twist_amp = node.MultDoubleLinear('{}RbnAmpEndTwist{}Mult'.format(name, self.side))
        self.root_auto_twist_mult = node.MultDoubleLinear('{}RbnAutoRootTwist{}Mult'.format(name, self.side))
        self.end_auto_twist_mult = node.MultDoubleLinear('{}RbnAutoEndTwist{}Mult'.format(name, self.side))
        self.root_twist_add = node.AddDoubleLinear('{}RbnRootTwist{}Add'.format(name, self.side))
        self.end_twist_add = node.AddDoubleLinear('{}RbnEndTwist{}Add'.format(name, self.side))

        self.rbn_ctrl.shape.attr('rootAbsTwist') >> self.root_twist_amp.attr('i1')
        self.rbn_ctrl.shape.attr('rootTwistAmp') >> self.root_twist_amp.attr('i2')
        self.rbn_ctrl.shape.attr('endAbsTwist') >> self.end_twist_amp.attr('i1')
        self.rbn_ctrl.shape.attr('endTwistAmp') >> self.end_twist_amp.attr('i2')

        self.rbn_ctrl.attr('autoTwist') >> self.root_auto_twist_mult.attr('i1')
        self.root_twist_amp.attr('o') >> self.root_auto_twist_mult.attr('i2')
        self.rbn_ctrl.attr('autoTwist') >> self.end_auto_twist_mult.attr('i1')
        self.end_twist_amp.attr('o') >> self.end_auto_twist_mult.attr('i2')

        self.rbn_ctrl.attr('rootTwist') >> self.root_twist_add.attr('i1')
        self.root_auto_twist_mult.attr('o') >> self.root_twist_add.attr('i2')
        self.rbn_ctrl.attr('endTwist') >> self.end_twist_add.attr('i1')
        self.end_auto_twist_mult.attr('o') >> self.end_twist_add.attr('i2')

        #-- Setup squash
        self.rbn_ctrl.add_divide_attr('squash')
        self.rbn_ctrl.add_attr('autoSquash', min = 0, max = 1)
        self.rbn_ctrl.add_attr('rootSquash')
        self.rbn_ctrl.add_attr('midSquash')
        self.rbn_ctrl.add_attr('endSquash')
        self.rbn_ctrl.shape.add_attr('ampSquash', k = False)
        self.rbn_ctrl.shape.add_attr('currentSquash', k = False)
        self.rbn_ctrl.shape.add_attr('originalLen', k = False)
        self.rbn_ctrl.shape.add_attr('currentLen', k = False)
        self.rbn_ctrl.shape.add_divide_attr('gobal')
        self.rbn_ctrl.shape.add_attr('gobalAmp', min = 0, dv = 1)
        
        midgbl_mdv = node.MultiplyDivide('{}MidRbnSqshGbl{}Mdv'.format(name, self.side))
        rootgbl_mdv = node.MultiplyDivide('{}RootRbnSqshGbl{}Mdv'.format(name, self.side))
        endgbl_mdv = node.MultiplyDivide('{}EndRbnSqshGbl{}Mdv'.format(name, self.side))

        mid_sub = node.PlusMinusAverage('{}MidRbnSqsh{}Sub'.format(name, self.side))
        root_sub = node.PlusMinusAverage('{}RootRbnSqsh{}Sub'.format(name, self.side))
        end_sub = node.PlusMinusAverage('{}EndRbnSqsh{}Sub'.format(name, self.side))

        mid_add = node.PlusMinusAverage('{}MidRbnSqsh{}Add'.format(name, self.side))
        root_add = node.PlusMinusAverage('{}RootRbnSqsh{}Add'.format(name, self.side))
        end_add = node.PlusMinusAverage('{}EndRbnSqsh{}Add'.format(name, self.side))
        
        for _sub in (mid_sub, root_sub, end_sub):
            _sub.add_vector_attr('constant', k = False)
            _sub.attr('constant').value = [-1]*3
            _sub.attr('constant') >>_sub.attr('i3').last()
        
        self.rbn_ctrl.attr('s') >> mid_sub.attr('i3').last()
        self.rbn_root_ctrl.attr('s') >> root_sub.attr('i3').last()
        self.rbn_end_ctrl.attr('s') >> end_sub.attr('i3').last()
        
        for _posi, _add in zip(['root','mid','end'], [root_add,mid_add,end_add]):
            for ax in self.sqsh_axis:
                sqsh_attr = '{}Squash'.format(_posi)
                self.rbn_ctrl.attr(sqsh_attr) >> _add.attr('i3[1].i3{}'.format(ax))

        mid_sub.attr('o3') >> mid_add.attr('i3').last()
        root_sub.attr('o3') >> root_add.attr('i3').last()
        end_sub.attr('o3') >> end_add.attr('i3').last()

        mid_add.attr('o3') >> midgbl_mdv.attr('i1')
        root_add.attr('o3') >> rootgbl_mdv.attr('i1')
        end_add.attr('o3') >> endgbl_mdv.attr('i1')

        for gbl_mdv in (midgbl_mdv, rootgbl_mdv, endgbl_mdv):
            for v in 'xyz':
                self.rbn_ctrl.shape.attr('gobalAmp') >> gbl_mdv.attr('i2{}'.format(v))

        stretch_div = node.MultiplyDivide('{}Stretch{}Div'.format(name, self.side))
        auto_sqsh_pow = node.MultiplyDivide('{}AutoSqsh{}Pow'.format(name, self.side))
        auto_sqsh_div = node.MultiplyDivide('{}AutoSqsh{}Div'.format(name, self.side))
        auto_sqsh_sub = node.AddDoubleLinear('{}AutoSqsh{}Sub'.format(name, self.side))
        auto_sqsh_amp = node.MultDoubleLinear('{}AutoSqsh{}Amp'.format(name, self.side))
        auto_sqsh_gbl = node.MultDoubleLinear('{}AutoSqshGbl{}Mult'.format(name, self.side))
        auto_sqsh_blend = node.BlendTwoAttr('{}AutoSqsh{}Bta'.format(name, self.side))
        
        stretch_div.attr('op').value = 2
        auto_sqsh_div.attr('op').value = 2
        auto_sqsh_pow.attr('op').value = 3
        auto_sqsh_div.attr('i1x').value = 1
        auto_sqsh_pow.attr('i2x').value = 2
        auto_sqsh_sub.attr('i2').value = -1

        self.rbn_ctrl.shape.attr('originalLen') >> stretch_div.attr('i2x')
        self.rbn_ctrl.shape.attr('currentLen') >> stretch_div.attr('i1x')

        stretch_div.attr('ox') >> auto_sqsh_pow.attr('i1x')
        auto_sqsh_pow.attr('ox') >> auto_sqsh_div.attr('i2x')
        auto_sqsh_div.attr('ox') >> auto_sqsh_sub.attr('i1')

        auto_sqsh_blend.add_attr('default')
        auto_sqsh_blend.attr('default') >> auto_sqsh_blend.attr('i[0]')
        auto_sqsh_sub.attr('o') >> auto_sqsh_blend.attr('i[1]')
        self.rbn_ctrl.attr('autoSquash') >> auto_sqsh_blend.attr('attributesBlender')
        auto_sqsh_blend.attr('o') >> auto_sqsh_amp.attr('i1')
        self.rbn_ctrl.shape.attr('ampSquash') >> auto_sqsh_amp.attr('i2')
        auto_sqsh_amp.attr('o') >> auto_sqsh_gbl.attr('i1')
        self.rbn_ctrl.shape.attr('gobalAmp') >> auto_sqsh_gbl.attr('i2')
        auto_sqsh_gbl.attr('o') >> self.rbn_ctrl.shape.attr('currentSquash')

        self.rbn_ctrl.shape.attr('ampSquash').value = 1
        
        #-- Setup detail joint
        self.rbnDtl_grp_ctrl_list = list()
        self.rbnDtl_grp_jnt_list = list()

        anim_cuv = node.AnimCurveTU()
        mc.setKeyframe(anim_cuv, t = 1, v = 0.1)
        mc.setKeyframe(anim_cuv, t = numjnts, v = 0.1)
        mc.setKeyframe(anim_cuv, t = (numjnts/2)+1, v = 0.9)
        mc.keyTangent(anim_cuv, e = True, a = True, t = (1,1), outAngle = 90, outWeight = 0)
        mc.keyTangent(anim_cuv, e = True, a = True, t = (numjnts,numjnts), inAngle = 90, inWeight = 0)
        mc.keyTangent(anim_cuv, e = True, a = True, t = ((numjnts/2)+1,(numjnts/2)+1), inAngle = 0, inWeight = 0.15*numjnts)
        
        pv_list = util.calculate_uv_parameter(numjnts, offset = None)

        for i in range(1, numjnts+1):
            #-- Create controls
            detail_ctrl = util.controller('{}{}Rbn{}Ctrl'.format(name, i, self.side), 'circle', 'cyan')
            detail_ctrl_zro = util.group(detail_ctrl, 'Zro')
            detail_ctrl_tws = util.group(detail_ctrl, 'Twist')
            mc.parent(detail_ctrl_zro, self.rbnDtl_grp)

            self.rbnDtl_grp_ctrl_list.append(detail_ctrl)

            #-- Create joint
            detail_jnt = util.joint('{}{}Rbn{}Jnt'.format(name, i, self.side))
            detail_jnt_grp = util.group(detail_jnt)
            mc.parent(detail_jnt_grp, self.rbnSkin_grp)

            self.rbnDtl_grp_jnt_list.append(detail_jnt)

            #-- Adjust shape controls
            detail_ctrl.scale_shape(dist*0.14)
            detail_ctrl.rotate_shape(self.rotate)

            #-- Rig process
            util.parent_constraint(detail_ctrl, detail_jnt_grp, mo = False)

            #-- Setup position and sticky to nurbSurface
            posi = node.PointOnSurfaceInfo('{}{}Rbn{}Posi'.format(name, i, self.side))
            compmtx = node.ComposeMatrix('{}{}Rbn{}CompMtx'.format(name, i, self.side))
            multmtx = node.MultMatrix('{}{}Rbn{}MultMtx'.format(name, i, self.side))
            decmtx = node.DecomposeMatrix('{}{}Rbn{}DecMtx'.format(name, i, self.side))
            
            posi.attr('turnOnPercentage').value = 1
            posi.attr('parameterU').value = 0.5
            posi.attr('parameterV').value = pv_list[i-1]

            self.rbn_nrb.shape.attr('worldSpace[0]') >> posi.attr('inputSurface')
            posi.attr('position') >> compmtx.attr('inputTranslate')
            compmtx.attr('outputMatrix') >> multmtx.attr('matrixIn[0]')
            detail_ctrl_zro.attr('parentInverseMatrix[0]') >> multmtx.attr('matrixIn[1]')
            multmtx.attr('matrixSum') >> decmtx.attr('inputMatrix')
            decmtx.attr('outputTranslate') >> detail_ctrl_zro.attr('t')
            decmtx.attr('outputRotate') >> detail_ctrl_zro.attr('r')
            detail_ctrl_zro.attr('ro') >> decmtx.attr('inputRotateOrder')

            aimcons = node.AimConstraint('{}{}Rbn{}aimConstraint'.format(name, i, self.side))
            aimcons.attr('a').value = self.aimvec
            aimcons.attr('u').value = self.upvec
            posi.attr('n') >> aimcons.attr('wu')
            posi.attr('tv') >> aimcons.attr('tg[0].tt')
            aimcons.attr('cr') >> compmtx.attr('inputRotate')
            
            mc.parent(aimcons, detail_ctrl_zro)
            
            #-- Setup twist
            root_twist_mult = node.MultDoubleLinear('{}{}RbnRootTwist{}Mult'.format(name, i, self.side))
            end_twist_mult = node.MultDoubleLinear('{}{}RbnEndTwist{}Mult'.format(name, i, self.side))
            twist_sum = node.AddDoubleLinear('{}{}RbnTwist{}Sum'.format(name, i, self.side))

            self.root_twist_add.attr('o') >> root_twist_mult.attr('i1')
            self.end_twist_add.attr('o') >> end_twist_mult.attr('i1')

            root_twist_mult.attr('o') >> twist_sum.attr('i1')
            end_twist_mult.attr('o') >> twist_sum.attr('i2')
            twist_sum.attr('o') >> detail_ctrl_tws.attr('r{}'.format(self.aim_axis))

            tws_val = (1.0 / (numjnts-1)) * (i-1)
            root_twist_mult.attr('i2').value = 1-tws_val
            end_twist_mult.attr('i2').value = tws_val
            
            #-- Setup squash
            self.rbn_ctrl.shape.add_divide_attr('amplitude')

            auto_sqsh_attr = 'autoSquashAmp{}'.format(i)
            self.rbn_ctrl.shape.add_attr(auto_sqsh_attr, min = 0, max = 1)
            amp = mc.keyframe(anim_cuv, t = (i,i), q = True, eval = True)[0]
            self.rbn_ctrl.shape.attr(auto_sqsh_attr).value = round(amp,2)
            
            sqsh_amp = node.MultiplyDivide('{}{}RbnAutoSqsh{}Amp'.format(name, i, self.side))
            sqsh_add = node.PlusMinusAverage('{}{}RbnSqsh{}Add'.format(name, i, self.side))
            sqsh_sum = node.PlusMinusAverage('{}{}RbnSqsh{}Sum'.format(name, i, self.side))
            
            for ax in 'xyz':
                self.rbn_ctrl.shape.attr('currentSquash') >> sqsh_amp.attr('i1{}'.format(ax))
                self.rbn_ctrl.shape.attr(auto_sqsh_attr) >> sqsh_amp.attr('i2{}'.format(ax))
            
            sqsh_amp.attr('o') >> sqsh_add.attr('i3').last()
            sqsh_add.attr('o3') >> sqsh_sum.attr('i3').last()
            sqsh_sum.attr('o3') >> detail_jnt.attr('s')
            detail_ctrl.attr('s') >> sqsh_add.attr('i3').last()

            #-- Setup lower, middle, upper squash
            midjnt = (numjnts/2)+1
            sqsh_amp_attr = 'sqshAmp{}'.format(i)
            
            self.rbn_ctrl.shape.add_attr(sqsh_amp_attr, k = False, dv = round(amp, 2))
            mid_amp = node.MultiplyDivide('{}{}MidSqsh{}Amp'.format(name, i, self.side))
            mid_amp_rev = node.Reverse('{}{}MidSqshAmp{}Rev'.format(name, i, self.side))
            
            midgbl_mdv.attr('o') >> mid_amp.attr('i1')
            mid_amp.attr('i2') >> mid_amp_rev.attr('i')
            mid_amp.attr('o') >> sqsh_sum.attr('i3').last()

            for ax in 'xyz':
                self.rbn_ctrl.shape.attr(sqsh_amp_attr) >> mid_amp.attr('i2{}'.format(ax))

            if i == midjnt:
                mid_div = node.MultiplyDivide('{}{}MidSqsh{}Div'.format(name, i, self.side))
                mid_div.attr('i2').value = (0.5, 0.5, 0.5)
                mid_amp_rev.attr('o') >> mid_div.attr('i1')
                
            sqsh_list = list()
            if i <= midjnt:
                sqsh_list.append(['Root', rootgbl_mdv])
            if i >= midjnt:
                sqsh_list.append(['End', endgbl_mdv])

            for each, gblmdl in sqsh_list:
                each_amp = node.MultiplyDivide('{}{}{}Sqsh{}Amp'.format(name, each, i, self.side))
                gblmdl.attr('o') >> each_amp.attr('i1')
                each_amp.attr('o') >> sqsh_sum.attr('i3').last()
                mid_amp_rev.attr('o') >> each_amp.attr('i2')

                if i == midjnt:
                    mid_div.attr('o') >> each_amp.attr('i2')

            for _lock in (detail_ctrl_zro, detail_ctrl_tws):
                _lock.lhtrs()
                _lock.lhv()

        self.rbn_ctrl.shape.attr('detailControl') >> self.rbnDtl_grp.attr('v')
        mc.delete(anim_cuv)

        #-- Manage hierarchy
        mc.parent(rbn_all_handle, self.rbn_aim)
        mc.parent(self.rbn_nrb, rbn_handle, self.rbnStill_grp)
        mc.parent(self.rbnDtl_grp, self.rbnCtrl_grp)

        #-- Cleanup
        for _each in (rbn_handle, rbn_all_handle, self.rbnSkin_grp, self.rbnStill_grp, self.rbnDtl_grp):
            _each.lhtrs()

        for _dtl_jnt in self.rbnDtl_grp_jnt_list:
            _dtl_jnt.lhtrs()

        for _dtl_ctrl in self.rbnDtl_grp_ctrl_list:
            _dtl_ctrl.lock_hide('s{}'.format(self.aim_axis), 'v')
        
        self.rbn_nrb.lhtrs()
    mc.select(cl = True)