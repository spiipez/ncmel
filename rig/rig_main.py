# System modules.
from imp import reload

# Maya modules.
import maya.cmds as mc

# ncscript modules.
from ncTools.rig import node
from ncTools.rig import util
reload(node)
reload(util)

class Main(object):

    def __init__(self, asset_name = '', fly_pivot = ''):

        '''
        '''

        #-- Create main group
        self.rig_grp = node.Transform('Rig_Grp')
        self.geo_grp = node.Transform('Geo_Grp')
        self.ctrl_grp = node.Transform('Ctrl_Grp')
        self.mainctrl_grp = node.Transform('MainCtrl_Grp')
        self.facialctrl_grp = node.Transform('FacialCtrl_Grp')
        self.allmover_grp = node.Transform('AllMover_Grp')
        self.skin_grp = node.Transform('Skin_Grp')
        self.still_grp = node.Transform('Still_Grp')

        #-- Create main controls
        self.allmover_ctrl = util.controller('AllMover_Ctrl', 'arrowCircle', 'yellow')
        self.offset_ctrl = util.controller('Offset_Ctrl', None, 'black')
        self.scale_ctrl = util.controller('Scale_Ctrl', 'null')

        #-- Adjust shape controls
        self.allmover_ctrl.scale_shape(6)
        self.offset_ctrl.scale_shape(13)

        #-- Rig process
        for _ctrl in (self.allmover_ctrl, self.scale_ctrl):
            _ctrl.attr('sy') >> _ctrl.attr('sx')
            _ctrl.attr('sy') >> _ctrl.attr('sz')
        
        #-- Manage hierarchy
        mc.parent(self.scale_ctrl, self.offset_ctrl)
        mc.parent(self.offset_ctrl, self.allmover_ctrl)
        mc.parent(self.allmover_ctrl, self.allmover_grp)
        mc.parent(self.facialctrl_grp, self.mainctrl_grp, self.ctrl_grp)
        mc.parent(self.ctrl_grp, self.skin_grp, self.scale_ctrl)
        mc.parent(self.geo_grp, self.allmover_grp, self.still_grp, self.rig_grp)
        
        #-- Cleanup
        self.allmover_ctrl.lock_hide('sx', 'sz', 'v')
        self.offset_ctrl.lock_hide('sx', 'sy', 'sz', 'v')
        self.scale_ctrl.lock_hide('t', 'r', 'sx', 'sz')

        self.still_grp.hide()
        self.scale_ctrl.shape.hide()

        if fly_pivot:
            #-- Create controls
            self.fly_ctrl = util.controller('Fly_Ctrl', 'wing', 'pink')
            self.fly_grp = util.group(self.fly_ctrl)
            self.fly_grp.snap(fly_pivot)

            #-- Rig process
            self.allmover_ctrl.shape.add_divide_attr('specialControl')
            self.allmover_ctrl.shape.add_attr('flyControl', min = 0, max = 1)
            self.allmover_ctrl.shape.attr('flyControl') >> self.fly_ctrl.shape.attr('v')

            #-- Manage hierarchy
            mc.parent(self.fly_grp, self.scale_ctrl)
            mc.parent(self.ctrl_grp, self.skin_grp, self.fly_ctrl)

            #-- Cleanup
            self.fly_ctrl.lock_hide('sx', 'sy', 'sz', 'v')
        
        if asset_name:
            self.asset_ctrl = util.text_curves(asset_name)
            self.asset_ctrl.name = '{}_Ctrl'.format(asset_name)
            self.asset_ctrl.color = 'black'
            self.asset_ctrl_grp = util.group(self.asset_ctrl)
            mc.parent(self.asset_ctrl_grp, self.offset_ctrl)
            self.asset_ctrl.lhtrs()
            self.asset_ctrl.lhv()

            self.asset_ctrl.add_divide_attr('controls')
            self.asset_ctrl.add_attr('blocking', min = 0, max = 1)
            self.asset_ctrl.add_attr('secondary', min = 0, max = 1)
            self.asset_ctrl.add_attr('addRig', min = 0, max = 1)
            self.asset_ctrl.add_divide_attr('facial')
            self.asset_ctrl.add_attr('facialMain', min = 0, max = 1)
            self.asset_ctrl.add_attr('facialDetail', min = 0, max = 1)
            self.asset_ctrl.add_divide_attr('geome')
            self.asset_ctrl.add_attr('geo', min = 0, max = 1)
        
        mc.select(cl = True)