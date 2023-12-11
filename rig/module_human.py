# System modules.
from imp import reload

# Maya modules.
import maya.cmds as mc

# ncscript core modules.
from ncTools.rig import core
from ncTools.rig import util
reload(core)
reload(util)

# ncscript rig modules.
from ncTools.rig import rig_main
from ncTools.rig import rig_root
from ncTools.rig import rig_torso
from ncTools.rig import rig_neck
from ncTools.rig import rig_head
from ncTools.rig import rig_jaw
from ncTools.rig import rig_eye
from ncTools.rig import rig_clavicle
from ncTools.rig import rig_arm
from ncTools.rig import rig_leg
from ncTools.rig import rig_hindleg
from ncTools.rig import rig_finger
reload(rig_main)
reload(rig_root)
reload(rig_torso)
reload(rig_neck)
reload(rig_head)
reload(rig_jaw)
reload(rig_eye)
reload(rig_clavicle)
reload(rig_arm)
reload(rig_leg)
reload(rig_hindleg)
reload(rig_finger)


def run():
    '''
    '''
    print("## -- Build >> Main Group")
    main = rig_main.Main( asset_name = '',
                          fly_pivot = '' )
    
    print("## -- Build >> Root")
    root = rig_root.Root( root_tmpJnt = 'Root_TmpJnt',
                          ctrl_grp = main.mainctrl_grp,
                          skin_grp = main.skin_grp,
                          part = '' )
    
    print("## -- Build >> Torso")
    torso = rig_torso.Torso( pelvis_tmpJnt = 'Pelvis_TmpJnt',
                             spine1_tmpJnt = 'Spine1_TmpJnt' ,
                             spine2_tmpJnt = 'Spine2_TmpJnt' ,
                             spine3_tmpJnt = 'Spine3_TmpJnt' ,
                             spine4_tmpJnt = 'Spine4_TmpJnt' ,
                             parent = root.root_jnt,
                             ctrl_grp = main.mainctrl_grp,
                             still_grp = main.still_grp,
                             part = '',
                             axis = 'y',
                             subdiv = 1 )
    
    print("## -- Build >> Neck")
    neck = rig_neck.Neck( neck_tmpJnt = 'Neck_TmpJnt',
                          head_tmpJnt = 'Head_TmpJnt',
                          parent = torso.breast_jnt,
                          ctrl_grp = main.mainctrl_grp,
                          still_grp = main.still_grp,
                          part = '',
                          ribbon = True,
                          subdiv = 0,
                          axis = 'y' )
    
    print("## -- Build >> Head")
    head = rig_head.Head( head_tmpJnt = 'Head_TmpJnt',
                          headEnd_tmpJnt = 'HeadEnd_TmpJnt',
                          parent = neck.neckEnd_jnt,
                          ctrl_grp = main.mainctrl_grp,
                          part = '' )
    
    print("## -- Build >> Eye")
    eye = rig_eye.Eye( target_tmpJnt = 'EyeTrgt_TmpJnt',
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
                       parent = head.head_jnt,
                       ctrl_grp = main.mainctrl_grp,
                       eye_scale = (1, 1, 1),
                       part = '' )
    
    print("## -- Build >> Jaw")
    jaw = rig_jaw.Jaw( jawUpr1_tmpJnt = 'JawUpr1_TmpJnt',
                       jawUprEnd_tmpJnt = 'JawUprEnd_TmpJnt',
                       jawLwr1_tmpJnt = 'JawLwr1_TmpJnt',
                       jawLwr2_tmpJnt = 'JawLwr2_TmpJnt',
                       jawLwrEnd_tmpJnt = 'JawLwrEnd_TmpJnt',
                       parent = head.head_jnt,
                       ctrl_grp = main.mainctrl_grp,
                       part = '' )
    
    print("## -- Build >> Clavicle Left")
    clav_left = rig_clavicle.Clavicle( clav_tmpJnt = 'Clav_L_TmpJnt',
                                       uparm_tmpJnt = 'UpArm_L_TmpJnt',
                                       wrist_tmpJnt = 'Wrist_L_TmpJnt',
                                       parent = torso.breastPos_jnt,
                                       ctrl_grp = main.mainctrl_grp,
                                       part = '',
                                       side = 'L',
                                       auto_clav = True )
    
    print("## -- Build >> Clavicle Right")
    clav_right = rig_clavicle.Clavicle( clav_tmpJnt = 'Clav_R_TmpJnt',
                                        uparm_tmpJnt = 'UpArm_R_TmpJnt',
                                        wrist_tmpJnt = 'Wrist_R_TmpJnt',
                                        parent = torso.breastPos_jnt,
                                        ctrl_grp = main.mainctrl_grp,
                                        part = '',
                                        side = 'R',
                                        auto_clav = True )
    
    print("## -- Build >> Arm Left")
    arm_left = rig_arm.Arm( uparm_tmpJnt = 'UpArm_L_TmpJnt',
                            forearm_tmpJnt = 'Forearm_L_TmpJnt',
                            wrist_tmpJnt = 'Wrist_L_TmpJnt',
                            hand_tmpJnt = 'Hand_L_TmpJnt',
                            elbow_tmpJnt = 'Elbow_L_TmpJnt',
                            parent = clav_left.clavEnd_jnt,
                            ctrl_grp = main.mainctrl_grp,
                            still_grp = main.still_grp,
                            part = '',
                            side = 'L',
                            ribbon = True )
    
    print("## -- Connect >> Auto Clavicle Left")
    clav_auto_left = rig_clavicle.ClavicleAuto( arm_ctrl = arm_left.arm_ctrl,
                                                clav_ctrl = clav_left.clav_ctrl,
                                                uparm_fk_ctrl = arm_left.uparm_fk_ctrl,
                                                wrist_ik_ctrl = arm_left.wrist_ik_ctrl )

    print("## -- Build >> Arm Right")
    arm_right = rig_arm.Arm( uparm_tmpJnt = 'UpArm_R_TmpJnt',
                             forearm_tmpJnt = 'Forearm_R_TmpJnt',
                             wrist_tmpJnt = 'Wrist_R_TmpJnt',
                             hand_tmpJnt = 'Hand_R_TmpJnt',
                             elbow_tmpJnt = 'Elbow_R_TmpJnt',
                             parent = clav_right.clavEnd_jnt,
                             ctrl_grp = main.mainctrl_grp,
                             still_grp = main.still_grp,
                             part = '',
                             side = 'R',
                             ribbon = True )
    
    print("## -- Connect >> Auto Clavicle Right")
    clav_auto_right = rig_clavicle.ClavicleAuto( arm_ctrl = arm_right.arm_ctrl,
                                                 clav_ctrl = clav_right.clav_ctrl,
                                                 uparm_fk_ctrl = arm_right.uparm_fk_ctrl,
                                                 wrist_ik_ctrl = arm_right.wrist_ik_ctrl )
    
    print("## -- Build >> Leg Left")
    leg_left = rig_leg.Leg( upleg_tmpJnt = 'UpLeg_L_TmpJnt',
                            lowleg_tmpJnt = 'LowLeg_L_TmpJnt',
                            ankle_tmpJnt = 'Ankle_L_TmpJnt',
                            ball_tmpJnt = 'Ball_L_TmpJnt',
                            toe_tmpJnt = 'Toe_L_TmpJnt',
                            heel_tmpJnt = 'Heel_L_TmpJnt',
                            footIn_tmpJnt = 'FootIn_L_TmpJnt',
                            footOut_tmpJnt = 'FootOut_L_TmpJnt',
                            knee_tmpJnt = 'Knee_L_TmpJnt',
                            footSmart_tmpJnt = 'FootSmart_L_TmpJnt',
                            parent = torso.pelvis_jnt, 
                            ctrl_grp = main.mainctrl_grp,
                            still_grp = main.still_grp,
                            part = '',
                            side = 'L',
                            ribbon = True,
                            foot = True,
                            footSmart = True,
                            scapular = False )
    
    print("## -- Build >> Leg Right")
    leg_right = rig_leg.Leg( upleg_tmpJnt = 'UpLeg_R_TmpJnt',
                             lowleg_tmpJnt = 'LowLeg_R_TmpJnt',
                             ankle_tmpJnt = 'Ankle_R_TmpJnt',
                             ball_tmpJnt = 'Ball_R_TmpJnt',
                             toe_tmpJnt = 'Toe_R_TmpJnt',
                             heel_tmpJnt = 'Heel_R_TmpJnt',
                             footIn_tmpJnt = 'FootIn_R_TmpJnt',
                             footOut_tmpJnt = 'FootOut_R_TmpJnt',
                             knee_tmpJnt = 'Knee_R_TmpJnt',
                             footSmart_tmpJnt = 'FootSmart_R_TmpJnt',
                             parent = torso.pelvis_jnt, 
                             ctrl_grp = main.mainctrl_grp,
                             still_grp = main.still_grp,
                             part = '',
                             side = 'R',
                             ribbon = True,
                             foot = True,
                             footSmart = True,
                             scapular = False )

    # print("## -- Build >> Leg Left")
    # leg_left = rig_hindleg.HindLeg( upleg_tmpJnt = 'UpLegBack_L_TmpJnt',
    #                                 midleg_tmpJnt = 'MidLegBack_L_TmpJnt',
    #                                 lowleg_tmpJnt = 'LowLegBack_L_TmpJnt',
    #                                 ankle_tmpJnt = 'AnkleBack_L_TmpJnt',
    #                                 ball_tmpJnt = 'BallBack_L_TmpJnt',
    #                                 toe_tmpJnt = 'ToeBack_L_TmpJnt',
    #                                 heel_tmpJnt = 'HeelBack_L_TmpJnt',
    #                                 footIn_tmpJnt = 'FootInBack_L_TmpJnt',
    #                                 footOut_tmpJnt = 'FootOutBack_L_TmpJnt',
    #                                 knee_tmpJnt = 'KneeBack_L_TmpJnt',
    #                                 footSmart_tmpJnt = 'FootSmartBack_L_TmpJnt',
    #                                 parent = torso.pelvis_jnt, 
    #                                 ctrl_grp = main.mainctrl_grp,
    #                                 still_grp = main.still_grp,
    #                                 part = '',
    #                                 side = 'L',
    #                                 ribbon = True,
    #                                 foot = True,
    #                                 footSmart = True)
    
    # print("## -- Build >> Leg Right")
    # leg_right = rig_hindleg.HindLeg( upleg_tmpJnt = 'UpLegBack_R_TmpJnt',
    #                                  midleg_tmpJnt = 'MidLegBack_R_TmpJnt',
    #                                  lowleg_tmpJnt = 'LowLegBack_R_TmpJnt',
    #                                  ankle_tmpJnt = 'AnkleBack_R_TmpJnt',
    #                                  ball_tmpJnt = 'BallBack_R_TmpJnt',
    #                                  toe_tmpJnt = 'ToeBack_R_TmpJnt',
    #                                  heel_tmpJnt = 'HeelBack_R_TmpJnt',
    #                                  footIn_tmpJnt = 'FootInBack_R_TmpJnt',
    #                                  footOut_tmpJnt = 'FootOutBack_R_TmpJnt',
    #                                  knee_tmpJnt = 'KneeBack_R_TmpJnt',
    #                                  footSmart_tmpJnt = 'FootSmartBack_R_TmpJnt',
    #                                  parent = torso.pelvis_jnt, 
    #                                  ctrl_grp = main.mainctrl_grp,
    #                                  still_grp = main.still_grp,
    #                                  part = '',
    #                                  side = 'R',
    #                                  ribbon = True,
    #                                  foot = True,
    #                                  footSmart = True)







    # print("## -- Build >> Hand Left")
    # hand_left = rig_finger.HandSmart( handSmart_tmpJnt = 'HandSmart_L_TmpJnt',
    #                                   parent = arm_left.hand_jnt,
    #                                   ctrl_grp = main.mainctrl_grp,
    #                                   part = '',
    #                                   side = 'L' )
    
    # print("## -- Build >> Thumb Left")
    # thumb_left = rig_finger.Finger( fngr = 'Thumb',
    #                                 fngr_tmpJnt = ['Thumb1_L_TmpJnt',
    #                                                'Thumb2_L_TmpJnt',
    #                                                'Thumb3_L_TmpJnt',
    #                                                'Thumb4_L_TmpJnt'],
    #                                 arm_ctrl = arm_left.arm_ctrl,
    #                                 smart_ctrl = '',
    #                                 parent = arm_left.hand_jnt,
    #                                 ctrl_grp = main.mainctrl_grp,
    #                                 setup_value = True,
    #                                 part = '',
    #                                 side = 'L' )
    
    # print("## -- Build >> Index Left")
    # index_left = rig_finger.Finger( fngr = 'Index',
    #                                 fngr_tmpJnt = ['Index1_L_TmpJnt',
    #                                                'Index2_L_TmpJnt',
    #                                                'Index3_L_TmpJnt',
    #                                                'Index4_L_TmpJnt',
    #                                                'Index5_L_TmpJnt'],
    #                                 arm_ctrl = arm_left.arm_ctrl,
    #                                 smart_ctrl = hand_left.smart_ctrl,
    #                                 parent = arm_left.hand_jnt,
    #                                 ctrl_grp = main.mainctrl_grp,
    #                                 setup_value = True,
    #                                 part = '',
    #                                 side = 'L' )
    
    # print("## -- Build >> Middle Left")
    # middle_left = rig_finger.Finger( fngr = 'Middle',
    #                                  fngr_tmpJnt = ['Middle1_L_TmpJnt',
    #                                                 'Middle2_L_TmpJnt',
    #                                                 'Middle3_L_TmpJnt',
    #                                                 'Middle4_L_TmpJnt',
    #                                                 'Middle5_L_TmpJnt'],
    #                                  arm_ctrl = arm_left.arm_ctrl,
    #                                  smart_ctrl = hand_left.smart_ctrl,
    #                                  parent = arm_left.hand_jnt,
    #                                  ctrl_grp = main.mainctrl_grp,
    #                                  setup_value = True,
    #                                  part = '',
    #                                  side = 'L' )
    
    # print("## -- Build >> Ring Left")
    # ring_left = rig_finger.Finger( fngr = 'Ring',
    #                                fngr_tmpJnt = ['Ring1_L_TmpJnt',
    #                                               'Ring2_L_TmpJnt',
    #                                               'Ring3_L_TmpJnt',
    #                                               'Ring4_L_TmpJnt',
    #                                               'Ring5_L_TmpJnt'],
    #                                arm_ctrl = arm_left.arm_ctrl,
    #                                smart_ctrl = hand_left.smart_ctrl,
    #                                parent = arm_left.hand_jnt,
    #                                ctrl_grp = main.mainctrl_grp,
    #                                setup_value = True,
    #                                part = '',
    #                                side = 'L' )
    
    # print("## -- Build >> Pinky Left")
    # pinky_left = rig_finger.Finger( fngr = 'Pinky',
    #                                 fngr_tmpJnt = ['Pinky1_L_TmpJnt',
    #                                                'Pinky2_L_TmpJnt',
    #                                                'Pinky3_L_TmpJnt',
    #                                                'Pinky4_L_TmpJnt',
    #                                                'Pinky5_L_TmpJnt'],
    #                                 arm_ctrl = arm_left.arm_ctrl,
    #                                 smart_ctrl = hand_left.smart_ctrl,
    #                                 parent = arm_left.hand_jnt,
    #                                 ctrl_grp = main.mainctrl_grp,
    #                                 setup_value = True,
    #                                 part = '',
    #                                 side = 'L' )