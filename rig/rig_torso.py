# System modules.
from imp import reload

# Maya modules.
import maya.cmds as mc

# ncscript modules.
from ncTools.rig import node
from ncTools.rig import util
from ncTools.rig import tools_rivet as rvt
reload(node)
reload(util)
reload(rvt)

class Torso(object):

    def __init__(self, pelvis_tmpJnt = '',
                       spine1_tmpJnt = '' ,
                       spine2_tmpJnt = '' ,
                       spine3_tmpJnt = '' ,
                       spine4_tmpJnt = '' ,
                       parent = '',
                       ctrl_grp = '',
                       still_grp = '',
                       part = '',
                       axis = '',
                       subdiv = 1
                ):

        '''
        '''

        ##-- Prepare
        numjnts = (subdiv*2)+3
        part = part.capitalize()
        dist = util.distance_between(util.get_position(spine1_tmpJnt), 
                                     util.get_position(spine4_tmpJnt))
        
        if axis == 'y':
            sqshax = 'xz'
            aimvec = 'y'
            upvec = 'z'
        
        elif axis == 'z':
            sqshax = 'xy'
            aimvec = 'z'
            upvec = 'y'
        
        rotate_order = 'xzy'

        #-- Setting preference turn on weight tangent
        mc.keyTangent(e = True, g = True, wt = True)
        
        #-- Create main group
        self.torsoCtrl_grp = node.Transform('Torso{}Ctrl_Grp'.format(part))
        self.torsoStill_grp = node.Transform('Torso{}Still_Grp'.format(part))
        mc.parent(self.torsoCtrl_grp, ctrl_grp)
        mc.parent(self.torsoStill_grp, still_grp)

        util.parent_constraint(parent, self.torsoCtrl_grp, mo = False)

        self.torsoDtl_grp = node.Transform('Torso{}DtlCtrl_Grp'.format(part))
        mc.parent(self.torsoDtl_grp, self.torsoCtrl_grp)

        #-- Create rig joint
        self.hip_rigJnt = node.Joint('Hip{}_RigJnt'.format(part), position = spine1_tmpJnt)
        self.chest_rigJnt = node.Joint('Chest{}_RigJnt'.format(part), position = spine4_tmpJnt)
        self.body_rigJnt = node.Joint('Body{}_RigJnt'.format(part))

        tmp_jntList = [spine1_tmpJnt, spine2_tmpJnt, spine3_tmpJnt, spine4_tmpJnt]
        tmp_cuv = util.create_ep_curve_to_joint('Tmp_Cuv', tmp_jntList, 4)
        lenght = mc.arclen(tmp_cuv)
        mid_position = util.get_point_at_param(tmp_cuv, lenght/2)
        
        self.body_rigJnt.attr('t').value = mid_position
        self.body_rigJnt.snap_orient(spine2_tmpJnt, spine3_tmpJnt)

        mc.delete(tmp_cuv)

        #-- Create main controls
        self.spineLow_fk_ctrl = util.controller('Spine{}LowFk_Ctrl'.format(part), 'octagon', 'red')
        self.spineLow_fk_gmbl = util.gimbal(self.spineLow_fk_ctrl)
        self.spineLow_fk_zro = util.group(self.spineLow_fk_ctrl, 'Zro')
        self.spineLow_fk_zro.snap(self.hip_rigJnt)

        self.spineUp_fk_ctrl = util.controller('Spine{}UpFk_Ctrl'.format(part), 'octagon', 'red')
        self.spineUp_fk_gmbl = util.gimbal(self.spineUp_fk_ctrl)
        self.spineUp_fk_zro = util.group(self.spineUp_fk_ctrl, 'Zro')
        self.spineUp_fk_zro.snap(self.body_rigJnt)

        self.chest_ctrl = util.controller('Chest{}_Ctrl'.format(part), 'cube', 'yellow')
        self.chest_gmbl = util.gimbal(self.chest_ctrl)
        self.chest_zro = util.group(self.chest_ctrl, 'Zro')
        self.chest_zro.snap(self.chest_rigJnt)

        self.hip_ctrl = util.controller('Hip{}_Ctrl'.format(part), 'cube', 'yellow')
        self.hip_gmbl = util.gimbal(self.hip_ctrl)
        self.hip_zro = util.group(self.hip_ctrl, 'Zro')
        self.hip_zro.snap(self.body_rigJnt)

        self.body_ctrl = util.controller('Body{}_Ctrl'.format(part), 'octagon', 'cyan')
        self.body_gmbl = util.gimbal(self.body_ctrl)
        self.body_zro = util.group(self.body_ctrl, 'Zro')
        self.body_zro.snap(self.body_rigJnt)

        #-- Adjust shape controls
        for __ctrl in (self.spineLow_fk_ctrl, self.spineLow_fk_gmbl, self.spineUp_fk_ctrl, self.spineUp_fk_gmbl, self.chest_ctrl, self.chest_gmbl):
            __ctrl.scale_shape(1.25)
        
        for __ctrl in (self.hip_ctrl, self.hip_gmbl, self.body_ctrl, self.body_gmbl):
            __ctrl.scale_shape(1.75)
        
        #-- Set rotate order
        for __ctrl in (self.spineLow_fk_ctrl, self.spineUp_fk_ctrl, self.chest_ctrl):
            __ctrl.rotate_order = rotate_order
        
        #-- Manage hierarchy
        mc.parent(self.body_rigJnt, self.body_gmbl)
        mc.parent(self.chest_rigJnt, self.chest_gmbl)
        mc.parent(self.hip_rigJnt, self.hip_gmbl)

        mc.parent(self.spineUp_fk_zro, self.spineLow_fk_gmbl)
        mc.parent(self.spineLow_fk_zro, self.hip_zro, self.chest_zro, self.body_zro, self.torsoCtrl_grp)

        #-- Connect hide detail controls
        self.chest_ctrl.shape.add_attr('fkControl', min = 0, max = 1, dv = 1)
        self.chest_ctrl.shape.add_attr('detailControl', min = 0, max = 1)
        self.chest_ctrl.shape.attr('fkControl') >> self.spineLow_fk_zro.attr('v')
        self.chest_ctrl.shape.attr('detailControl') >> self.torsoDtl_grp.attr('v')

        #-- Create nurbSurface
        mid_tmp_cuv = util.create_ep_curve_to_joint('MidTmp_Cuv', tmp_jntList, 3)
        spine_tmp_cuv = util.create_ep_curve_to_joint('SpineTmp_Cuv', tmp_jntList, 2)

        mid_expand_cuv = util.expand_curve(mid_tmp_cuv, 'x', dist*0.05)
        spine_expand_cuv = util.expand_curve(spine_tmp_cuv, 'x', dist*0.05)

        id = [1,0]
        if axis == 'z':
            id = [0,1]
        
        self.body_nrb = util.register_node(mc.loft( mid_expand_cuv[id[0]],
                                                    mid_expand_cuv[id[1]],
                                                    ch = False, d = 3,
                                                    n = 'Body{}_Nrb'.format(part))[0])
        
        mc.rebuildSurface(self.body_nrb, ch = False, su = 1, sv = 3, du = 1, dv = 3, kr = 0)
        
        self.spine_nrb = util.register_node(mc.loft( spine_expand_cuv[id[0]],
                                                     spine_expand_cuv[id[1]],
                                                     ch = False, d = 3,
                                                     n = 'Spine{}_Nrb'.format(part))[0])
        
        mc.rebuildSurface(self.spine_nrb, ch = False, su = 1, sv = 2, du = 1, dv = 3, kr = 0)
        
        if axis == 'z':
            mc.reverseSurface(self.body_nrb, ch = False, d = 2, rpo = 1)
            mc.reverseSurface(self.spine_nrb, ch = False, d = 2, rpo = 1)
        
        mc.parent(self.body_nrb, self.spine_nrb, self.torsoStill_grp)
        mc.delete(mid_tmp_cuv, spine_tmp_cuv, mid_expand_cuv, spine_expand_cuv)
        
        #-- Sticky middle control to nurbSurface
        body_rvt = rvt.rivet_on_surface('Body{}'.format(part), '',
                                         self.body_nrb,
                                         self.body_zro,
                                         [0.5, 0.5],
                                         aimvec,
                                         upvec)
        
        #-- Bind skin nurbSurface
        body_skc = mc.skinCluster(self.hip_rigJnt, self.chest_rigJnt, self.body_nrb, dr = 2, mi = 2, tsb = 1, n = 'Body{}Nrb_Skc'.format(part))[0]
        spine_skc = mc.skinCluster(self.hip_rigJnt, self.body_rigJnt, self.chest_rigJnt, self.spine_nrb, dr = 2, mi = 2, tsb = 1, n = 'Spine{}Nrb_Skc'.format(part))[0]

        jnt_skin = { 'y' : [self.chest_rigJnt, self.hip_rigJnt],
                     'z' : [self.hip_rigJnt, self.chest_rigJnt]}
        
        mc.skinPercent(body_skc, '{}.cv[0:1][5]'.format(self.body_nrb), tv = [jnt_skin[axis][0], 1.0])
        mc.skinPercent(body_skc, '{}.cv[0:1][4]'.format(self.body_nrb), tv = [jnt_skin[axis][0], 0.8])
        mc.skinPercent(body_skc, '{}.cv[0:1][3]'.format(self.body_nrb), tv = [jnt_skin[axis][0], 0.6])
        mc.skinPercent(body_skc, '{}.cv[0:1][2]'.format(self.body_nrb), tv = [jnt_skin[axis][1], 0.6])
        mc.skinPercent(body_skc, '{}.cv[0:1][1]'.format(self.body_nrb), tv = [jnt_skin[axis][1], 0.8])
        mc.skinPercent(body_skc, '{}.cv[0:1][0]'.format(self.body_nrb), tv = [jnt_skin[axis][1], 1.0])

        mc.skinPercent(spine_skc, '{}.cv[0:1][4]'.format(self.spine_nrb), tv = [jnt_skin[axis][0], 1])
        mc.skinPercent(spine_skc, '{}.cv[0:1][3]'.format(self.spine_nrb), tv = [self.body_rigJnt, 0.6])
        mc.skinPercent(spine_skc, '{}.cv[0:1][2]'.format(self.spine_nrb), tv = [self.body_rigJnt, 1])
        mc.skinPercent(spine_skc, '{}.cv[0:1][1]'.format(self.spine_nrb), tv = [self.body_rigJnt, 0.6])
        mc.skinPercent(spine_skc, '{}.cv[0:1][0]'.format(self.spine_nrb), tv = [jnt_skin[axis][1], 1])
        
        #-- Setup fk controls
        util.parent_constraint(self.spineUp_fk_gmbl, self.chest_zro, mo = True)

        self.low_ori_pma = node.PlusMinusAverage('Spine{}LowOri_Pma'.format(part))
        self.spineLow_fk_ctrl.attr('r') >> self.low_ori_pma.attr('i3').last()
        self.spineLow_fk_gmbl.attr('r') >> self.low_ori_pma.attr('i3').last()
        self.low_ori_pma.attr('o3') >> self.hip_rigJnt.attr('r')
        
        #-- Setup squash
        self.body_ctrl.add_divide_attr('squash')
        self.body_ctrl.add_attr('autoSquash', min = 0, max = 1)
        self.body_ctrl.shape.add_attr('ampSquash', k = False)
        self.body_ctrl.shape.add_attr('currentSquash', k = False)
        self.body_ctrl.shape.add_attr('originalLen', k = False)
        self.body_ctrl.shape.add_attr('currentLen', k = False)
        self.body_ctrl.shape.add_divide_attr('gobal')
        self.body_ctrl.shape.add_attr('gobalAmp', min = 0, dv = 1)

        self.body_ctrl.add_attr('chestSquash')
        self.body_ctrl.add_attr('bodySquash')
        self.body_ctrl.add_attr('hipSquash')
        
        self.chestgbl_mult = node.MultDoubleLinear('Chest{}SqshGbl_Mult'.format(part))
        self.bodygbl_mult = node.MultDoubleLinear('Body{}SqshGbl_Mult'.format(part))
        self.hipgbl_mult = node.MultDoubleLinear('Hip{}SqshGbl_Mult'.format(part))
        
        self.body_ctrl.attr('chestSquash') >> self.chestgbl_mult.attr('i2')
        self.body_ctrl.attr('bodySquash') >> self.bodygbl_mult.attr('i2')
        self.body_ctrl.attr('hipSquash') >> self.hipgbl_mult.attr('i2')

        for gbl_mult in (self.chestgbl_mult, self.bodygbl_mult, self.hipgbl_mult):
            self.body_ctrl.shape.attr('gobalAmp') >> gbl_mult.attr('i1')
        
        self.spine_origlen_grp = node.Transform('Spine{}OrigLen_Grp'.format(part))
        self.spine_origlen_nrb = util.duplicate_and_clean(self.spine_nrb)
        self.spine_origlen_nrb.name = 'Spine{}OrigLen_Nrb'.format(part)

        mc.parent(self.spine_origlen_nrb, self.spine_origlen_grp)
        mc.parent(self.spine_origlen_grp, self.torsoCtrl_grp)

        self.spine_origlen_Cfsi = node.CurveFromSurfaceIso('Spine{}OrigLen_Cfsi'.format(part))
        self.spine_origlen_Cif = node.CurveInfo('Spine{}OrigLen_Cif'.format(part))

        self.spine_currlen_Cfsi = node.CurveFromSurfaceIso('Spine{}CurrLen_Cfsi'.format(part))
        self.spine_currlen_Cif = node.CurveInfo('Spine{}CurrLen_Cif'.format(part))

        self.spine_origlen_nrb.shape.attr('worldSpace[0]') >> self.spine_origlen_Cfsi.attr('inputSurface')
        self.spine_origlen_Cfsi.attr('outputCurve') >> self.spine_origlen_Cif.attr('inputCurve')
        self.spine_origlen_Cfsi.attr('isoparmDirection').value = 1
        self.spine_origlen_Cfsi.attr('isoparmValue').value = 0.5
        self.spine_origlen_Cfsi.attr('maxValue').value = 0

        self.spine_nrb.shape.attr('worldSpace[0]') >> self.spine_currlen_Cfsi.attr('inputSurface')
        self.spine_currlen_Cfsi.attr('outputCurve') >> self.spine_currlen_Cif.attr('inputCurve')
        self.spine_currlen_Cfsi.attr('isoparmDirection').value = 1
        self.spine_currlen_Cfsi.attr('isoparmValue').value = 0.5
        self.spine_currlen_Cfsi.attr('maxValue').value = 0

        self.spine_origlen_Cif.attr('arcLength') >> self.body_ctrl.shape.attr('originalLen')
        self.spine_currlen_Cif.attr('arcLength') >> self.body_ctrl.shape.attr('currentLen')

        self.stretch_div = node.MultiplyDivide('Spine{}Stretch_Div'.format(part))
        self.auto_squash_pow = node.MultiplyDivide('Spine{}AutoSqsh_Pow'.format(part))
        self.auto_squash_div = node.MultiplyDivide('Spine{}AutoSqsh_Div'.format(part))
        self.auto_squash_sub = node.AddDoubleLinear('Spine{}AutoSqsh_Sub'.format(part))
        self.auto_squash_amp = node.MultDoubleLinear('Spine{}AutoSqsh_Amp'.format(part))
        self.auto_squash_gbl = node.MultDoubleLinear('Spine{}AutoSqsh_Gbl'.format(part))
        self.auto_squash_blend = node.BlendTwoAttr('Spine{}AutoSqsh_Bta'.format(part))

        self.stretch_div.attr('op').value = 2
        self.auto_squash_pow.attr('op').value = 3
        self.auto_squash_pow.attr('i2x').value = 2
        self.auto_squash_div.attr('op').value = 2
        self.auto_squash_div.attr('i1x').value = 1
        self.auto_squash_sub.attr('i2').value = -1

        self.body_ctrl.shape.attr('originalLen') >> self.stretch_div.attr('i2x')
        self.body_ctrl.shape.attr('currentLen') >> self.stretch_div.attr('i1x')
        
        self.stretch_div.attr('ox') >> self.auto_squash_pow.attr('i1x')
        self.auto_squash_pow.attr('ox') >> self.auto_squash_div.attr('i2x')
        self.auto_squash_div.attr('ox') >> self.auto_squash_sub.attr('i1')

        self.auto_squash_blend.add_attr('default')
        self.auto_squash_blend.attr('default') >> self.auto_squash_blend.attr('i[0]')
        self.auto_squash_sub.attr('o') >> self.auto_squash_blend.attr('i[1]')

        self.body_ctrl.attr('autoSquash') >> self.auto_squash_blend.attr('attributesBlender')
        self.auto_squash_blend.attr('o') >> self.auto_squash_amp.attr('i1')
        self.body_ctrl.shape.attr('ampSquash') >> self.auto_squash_amp.attr('i2')
        self.auto_squash_amp.attr('o') >> self.auto_squash_gbl.attr('i1')
        self.body_ctrl.shape.attr('gobalAmp') >> self.auto_squash_gbl.attr('i2')
        self.auto_squash_gbl.attr('o') >> self.body_ctrl.shape.attr('currentSquash')
        self.body_ctrl.shape.attr('ampSquash').value = 1

        #-- Setup detail joint
        self.spine_ctrl_list = list()
        self.spine_ctrl_zro_list = list()
        self.spine_jnt_list = list()
        self.spine_jnt_zro_list = list()

        anim_cuv = node.AnimCurveTU()
        mc.setKeyframe(anim_cuv, t = 1, v = 0.1)
        mc.setKeyframe(anim_cuv, t = numjnts, v = 0.1)
        mc.setKeyframe(anim_cuv, t = (numjnts/2)+1, v = 0.9)
        mc.keyTangent(anim_cuv, e = True, a = True, t = (1,1), outAngle = 90, outWeight = 0)
        mc.keyTangent(anim_cuv, e = True, a = True, t = (numjnts,numjnts), inAngle = 90, inWeight = 0)
        mc.keyTangent(anim_cuv, e = True, a = True, t = ((numjnts/2)+1,(numjnts/2)+1), inAngle = 0, inWeight = 0.25*numjnts)

        for i in range(1, numjnts+1):
            detail_ctrl = util.controller('Spine{}{}_Ctrl'.format(part, i), 'plus', 'pink')
            detail_ctrl_zro = util.group(detail_ctrl, 'Zro')
            detail_ctrl.add_attr('squash')
            mc.parent(detail_ctrl_zro, self.torsoDtl_grp)

            detail_jnt = node.Joint('Spine{}{}_Jnt'.format(part, i))
            detail_jnt_grp = util.group(detail_jnt)
            detail_jnt.rotate_order = rotate_order

            self.spine_ctrl_list.append(detail_ctrl)
            self.spine_ctrl_zro_list.append(detail_ctrl_zro)
            self.spine_jnt_list.append(detail_jnt)
            self.spine_jnt_zro_list.append(detail_jnt_grp)
            
            #-- Setup position and sticky to nurbSurface
            if not i == numjnts:
                paramV = (1.0 / (numjnts-1) * (i-1))
                
                if axis == 'z':
                   paramV = 1-paramV

                detail_rvt = rvt.rivet_on_surface('Spine{}{}'.format(part, i), '',
                                                   self.spine_nrb,
                                                   detail_ctrl_zro, 
                                                   [0.5, paramV], 
                                                   aimvec, 
                                                   upvec )
            else:
                detail_ctrl_zro.snap(self.chest_rigJnt)
                detail_ctrl_zro.snap_orient(self.spine_jnt_zro_list[i-2])
                util.parent_constraint(self.chest_rigJnt, detail_ctrl_zro)
            
            util.parent_constraint(detail_ctrl, detail_jnt_grp, mo = False)

            if i == 1:
                mc.parent(detail_jnt_grp, parent)
            else:
                mc.parent(detail_jnt_grp, self.spine_jnt_zro_list[i-2])

            #-- Add auto squash
            auto_sqsh_amp_attr = 'autoSquashAmp{}'.format(i)
            self.body_ctrl.shape.add_divide_attr('amplitude')
            self.body_ctrl.shape.add_attr(auto_sqsh_amp_attr, min = 0, max = 1)
            amp = mc.keyframe(anim_cuv, t = (i,i), q = True, eval = True)[0]
            self.body_ctrl.shape.attr(auto_sqsh_amp_attr).value = round(amp, 2)

            auto_sqsh_amp = node.MultDoubleLinear('Spine{}{}AutoSqsh_Amp'.format(part, i))
            sqsh_amp = node.MultDoubleLinear('Spine{}{}Sqsh_Amp'.format(part, i))
            sqsh_add = node.AddDoubleLinear('Spine{}{}Sqsh_Add'.format(part, i))
            sqsh_sum = node.PlusMinusAverage('Spine{}{}SqshDef_Sum'.format(part, i))

            sqsh_sum.add_attr('constant', dv = 1)

            self.body_ctrl.shape.attr('currentSquash') >> auto_sqsh_amp.attr('i1')
            self.body_ctrl.shape.attr(auto_sqsh_amp_attr) >> auto_sqsh_amp.attr('i2')
            auto_sqsh_amp.attr('o') >> sqsh_add.attr('i1')
            sqsh_amp.attr('o') >> sqsh_add.attr('i2')
            sqsh_sum.attr('constant') >> sqsh_sum.attr('i1').last()
            sqsh_add.attr('o') >> sqsh_sum.attr('i1').last()

            sqsh_sum.attr('o1') >> detail_ctrl.attr('s{}'.format(sqshax[0]))
            sqsh_sum.attr('o1') >> detail_ctrl.attr('s{}'.format(sqshax[1]))
            
            detail_ctrl.attr('s') >> detail_jnt.attr('s')

            detail_ctrl.attr('squash') >> sqsh_amp.attr('i1')
            sqsh_amp.attr('i2').value = 0.1
            
            #-- Setup lower, middle, upper squash
            midjnt = (numjnts/2)+1
            sqsh_amp_attr = 'sqshAmp{}'.format(i)
            
            self.body_ctrl.shape.add_attr(sqsh_amp_attr, k = False, dv = round(amp, 2))
            body_amp = node.MultDoubleLinear('Body{}{}Sqsh_Amp'.format(part, i))
            body_amp_rev = node.Reverse('Body{}{}SqshAmp_Rev'.format(part, i))
            self.bodygbl_mult.attr('o') >> body_amp.attr('i1')
            self.body_ctrl.shape.attr(sqsh_amp_attr) >> body_amp.attr('i2')
            body_amp.attr('i2') >> body_amp_rev.attr('ix')
            body_amp.attr('o') >> sqsh_sum.attr('i1').last()

            if i == midjnt:
                body_div = node.MultDoubleLinear('Body{}{}Sqsh_Div'.format(part, i))
                body_div.attr('i2').value = 0.5
                body_amp_rev.attr('ox') >> body_div.attr('i1')

            sqsh_list = list()
            if i <= midjnt:
                sqsh_list.append(['Hip', self.hipgbl_mult])
            if i >= midjnt:
                sqsh_list.append(['Chest', self.chestgbl_mult])

            for each, gblmdl in sqsh_list:
                each_amp = node.MultDoubleLinear('{}{}{}Sqsh_Amp'.format(each, part, i))
                gblmdl.attr('o') >> each_amp.attr('i1')
                each_amp.attr('o') >> sqsh_sum.attr('i1').last()
                body_amp_rev.attr('ox') >> each_amp.attr('i2')
                
                if i == midjnt:
                    body_div.attr('o') >> each_amp.attr('i2')

        mc.delete(anim_cuv)

        #-- Setup Breast
        self.breastJnt_grp = node.Transform('Breast{}Jnt_Grp'.format(part))
        self.breastJnt_grp.snap(spine4_tmpJnt)

        self.breastPos_jnt = node.Joint('Breast{}Pos_Jnt'.format(part), position = spine4_tmpJnt)
        self.breast_jnt = node.Joint('Breast{}_Jnt'.format(part), position = spine4_tmpJnt)
        
        mc.parent(self.breastPos_jnt, self.spine_jnt_zro_list[-1])
        mc.parent(self.breastJnt_grp, self.breastPos_jnt)
        mc.parent(self.breast_jnt, self.breastJnt_grp)

        breast_position = util.distance_between(util.get_position(self.spine_jnt_list[0]),
                                                util.get_position(self.spine_jnt_list[1])) / 2
        
        self.breastPos_jnt.attr('t{}'.format(axis)).value = breast_position

        #-- Create controls
        self.breast_ctrl = util.controller('Breast{}_Ctrl'.format(part, i), 'octagon', 'pink')
        self.breast_zro = util.group(self.breast_ctrl, 'Zro')
        self.breast_zro.snap(self.breast_jnt)

        self.chest_ctrl.shape.add_attr('breastControl', min = 0, max = 1)
        self.chest_ctrl.shape.attr('breastControl') >> self.breast_zro.attr('v')

        #-- Set rotate order
        for __obj in (self.breast_ctrl, self.breast_jnt, self.breastJnt_grp):
            __obj.rotate_order = rotate_order
        
        #-- Rig process
        util.parent_constraint(self.breast_ctrl, self.breastJnt_grp, mo = True)

        #-- Manage hierarchy
        mc.parent(self.breast_zro, self.chest_gmbl)

        self.chest_ctrl.add_attr('breath', min = 0, max = 10)
        self.chest_ctrl.shape.add_divide_attr('amplitude')

        for ax in ('s{}'.format(sqshax[0]),
                   's{}'.format(sqshax[1]),
                   't{}'.format(axis)):
            
            breath_attr = 'breathAmp{}'.format(ax.upper())
            self.chest_ctrl.shape.add_attr(breath_attr)

            breath_amp_mult = node.MultDoubleLinear('Spine{}BreathMult{}_Amp'.format(part, i))
            breath_amp_add = node.AddDoubleLinear('Spine{}BreathAdd{}_Amp'.format(part, i))      

            self.chest_ctrl.shape.attr(breath_attr) >> breath_amp_mult.attr('i1')
            self.chest_ctrl.attr('breath') >> breath_amp_mult.attr('i2')
            breath_amp_mult.attr('o') >> breath_amp_add.attr('i1')
            
            if not ax == 't{}'.format(axis):
                self.breast_ctrl.attr('{}'.format(ax)) >> breath_amp_add.attr('i2')
                breath_amp_add.attr('o') >> self.breast_jnt.attr('{}'.format(ax))
            else:
                self.breast_ctrl.attr('s{}'.format(axis)) >> self.breast_jnt.attr('s{}'.format(axis))
                breath_amp_add.attr('i2').value = self.breast_zro.attr('{}'.format(ax)).value
                breath_amp_add.attr('o') >> self.breast_zro.attr('{}'.format(ax))

        #-- Setup Pelvis
        self.pelvisJnt_grp = node.Transform('Pelvis{}Jnt_Grp'.format(part))

        self.pelvisPos_jnt = node.Joint('Pelvis{}Pos_Jnt'.format(part))
        self.pelvis_jnt = node.Joint('Pelvis{}_Jnt'.format(part))

        mc.parent(self.pelvis_jnt, self.pelvisPos_jnt)
        mc.parent(self.pelvisPos_jnt, self.pelvisJnt_grp)

        self.pelvisJnt_grp.snap(pelvis_tmpJnt)

        #-- Create controls
        self.pelvis_ctrl = util.controller('Pelvis{}_Ctrl'.format(part), 'octagon', 'pink')
        self.pelvis_zro = util.group(self.pelvis_ctrl, 'Zro')
        self.pelvis_zro.snap(self.pelvis_jnt)

        self.hip_ctrl.shape.add_attr('pelvisControl', min = 0, max = 1)
        self.hip_ctrl.shape.attr('pelvisControl') >> self.pelvis_zro.attr('v')
        
        self.pelvis_ctrl.scale_shape(1.25)

        #-- Set rotate order
        for __obj in (self.pelvis_ctrl, self.pelvis_jnt, self.pelvisJnt_grp):
            __obj.rotate_order = rotate_order

        #-- Rig process
        util.parent_constraint(self.pelvis_ctrl, self.pelvisPos_jnt, mo = False)
        self.pelvis_ctrl.attr('s') >> self.pelvis_jnt.attr('s')

        #-- Adjust hierarchy
        mc.parent(self.pelvis_zro, self.hip_gmbl)
        mc.parent(self.pelvisJnt_grp, parent)

        #-- Cleanup
        for __obj in (self.spineLow_fk_ctrl, self.spineUp_fk_ctrl, self.chest_ctrl, self.hip_ctrl, self.body_ctrl):
            __obj.lock_hide('sx', 'sy', 'sz', 'v')
        
        for __obj in (self.spine_ctrl_list):
            __obj.lock_hide('sx', 'sy', 'sz', 'v')
        
        self.pelvis_ctrl.lock_hide('s{}'.format(axis))

        for __jnt in (self.hip_rigJnt, self.body_rigJnt, self.chest_rigJnt, self.breastPos_jnt, self.pelvisPos_jnt):
            __jnt.attr('drawStyle').value = 2
        
        self.spine_origlen_grp.hide()

        mc.select(cl = True)