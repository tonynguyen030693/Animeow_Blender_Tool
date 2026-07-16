# -*- coding: UTF-8 -*-
# Original design intention: In the process of processing motion compensation data, because it is a frame-by-frame animation, when there is jitter and needs to be modified, manual adjustment is very laborious and the effect is not good. The function of this plug-in is to assist smooth and intensive animation curves,
# Plug-in name: Suzhou Fang Ao_Animation curve smoothing tool
# designer:
# Official website: www.SuZhouFangHaoCulture.com
# Installation method: Copy the command to the python window of Maya and run it. You can also save it to the tool shelf and run it.
# How to use: Select a controller or a specific animation curve, execute the command, and the plug-in will automatically smooth your animation curve.
# Update history: v1.0(2020.04.02) - initial release
# v1.1(2020.04.04) Add a panel and add smooth intensity control options
# Update preview: update the smooth calculation method
# Option to increase smoothness strength - already implemented

import maya.cmds as cmds


def szfa_anim_curves_smooth():
     # Query the selected animation curve and determine whether the animation curve is selected.
     selected_anim_curves = cmds.keyframe(query=True, name=True)
     # print selected_anim_curves
     # current_selected = cmds.ls(sl=True)
     # for each_selected in current_selected:
     # type = cmds.nodeType(each_selected)
     # print each_selected +':'+ type
     # node_type = 1 if type == "transform" or type == "joint" else 0
     # print node_type
     # noinspection PyBroadException
     try:
         len(selected_anim_curves)
     except BaseException:
         cmds.error('Please select at least one animated object or animation curve!')
     # Start the smooth curve. The smooth curve does not need to move the first and last frames. For each frame in the middle, calculate an average value based on the values ​​of the previous and next key frames and assign it.
     # Based on the obtained animation curve, determine whether the number of key frames exceeds 3 frames (if it does not exceed 3 frames, smooth calculation cannot be performed).
     for each_curve in selected_anim_curves:
         # Get the frame on the animation curve
         # Determine whether the selected object is an animation curve
         # We need to distinguish whether we select a part of the animation curve or all the animation curves.
         keyframes_selected = cmds.keyframe(each_curve, query=True, time=(), selected=True)
         try:
             len(keyframes_selected)
         except BaseException:
             keyframes = cmds.keyframe(each_curve, query=True, time=())
         else:
             keyframes = cmds.keyframe(each_curve, query=True, time=(), selected=True)
             # print keyframes
         #else:
         # keyframes = cmds.keyframe(each_curve, query=True, time=(),selected=True)
         # print keyframes
         # Determine whether the number of key frames exceeds 3 frames. If not, no calculation will be performed and a result will be returned.
         if len(keyframes) < 3:
             keys_count = str(len(keyframes))
             # print each_curve+string_utf8+keys_count+string2_utf8
             print(each_curve + u' Only or only ' + keys_count + u' frame animation is selected, skip this curve (at least three frames of animation are required).')
             continue
         # If the number of key frames exceeds 3 frames, then we start smooth calculation
         else:
             # print each_curve+': '+str(keyframes)
             # If I directly assign the value to the current frame, it will change the state of the current curve. This will affect the final smooth effect.
             # I copied an animation curve, made changes to the copied curve, and then added it back to the original animation curve.
             duplicated_anim_curve = cmds.duplicate(each_curve, name=each_curve + '_temp')
             # The calculation needs to process every key frame on the animation curve except the beginning and end. You can use a while loop.
             index = 1
             while index < len(keyframes) - 1:
                 # print keyframes[index]
                 #The value of the previous frame
                 last_frame_value = cmds.keyframe(each_curve, query=True,
                                                  time=(keyframes[index - 1], keyframes[index - 1]), valueChange=True)
                 # print last_frame_value
                 #The value of the current frame
                 current_frame_value = cmds.keyframe(each_curve, query=True, time=(keyframes[index], keyframes[index]),
                                                     valueChange=True)
                 # print current_frame_value
                 # The value of the next frame
                 next_frame_value = cmds.keyframe(each_curve, query=True,
                                                  time=(keyframes[index + 1], keyframes[index + 1]), valueChange=True)
                 # print next_frame_value
                 # Average of three values
                 average_value = (last_frame_value[0] + current_frame_value[0] + next_frame_value[0]) / 3
                 # duplicated_anim_curve = cmds.duplicate[each_curve,name=each_curve+'_temp']
                 # Assign the calculated average value to the specified frame of the copied curve
                 cmds.keyframe(duplicated_anim_curve, absolute=True, time=(keyframes[index], keyframes[index]),
                               valueChange=average_value)
                 index += 1
             # Execute the loop again, this time to smooth the final animation curve
             index = 1
             while index < len(keyframes) - 1:
                 #Query the value of the specified frame on the copied curve
                 #
                 current_frame_value_duplicate_curve = cmds.keyframe(duplicated_anim_curve, query=True,
                                                                     time=(keyframes[index], keyframes[index]),
                                                                     valueChange=True)
                 current_frame_value_orig_curve = cmds.keyframe(each_curve, query=True,
                                                                time=(keyframes[index], keyframes[index]),
                                                                valueChange=True)
                 deviation_value = current_frame_value_orig_curve[0] - current_frame_value_duplicate_curve[0]
                 # print D-value
                 smooth_strength = cmds.floatSliderGrp('floatSlider_MDF', query=True, v=True)
                 final_value = current_frame_value_orig_curve[0] - deviation_value * smooth_strength
                 # Assign the queried value to the final curve

                 cmds.keyframe(each_curve, absolute=True, time=(keyframes[index], keyframes[index]),
                               valueChange=final_value)
                 index += 1
             # Delete the copied curve
             cmds.delete(duplicated_anim_curve)
             # Complete life.


#Create UI window
#Create the main window
def mainUI():
    if cmds.window('window_main_MDF', q=1, ex=1):
        cmds.deleteUI('window_main_MDF')
    cmds.window('window_main_MDF', ret=1, mnb=0, mxb=0, t='Motion compensation data jitter repair tool window', tb=1, vis=1, s=0, mb=1)
    #Create the main layout
    cmds.formLayout('formLayout_main_MDF', en=1, w=280, h=53, vis=1)
    #Create controls
    cmds.separator('separator01_MDF', st='single', en=1, vis=1, h=2, w=280, bgc=[0.0, 0.0, 0.0], hr=1)
    cmds.floatSliderGrp('floatSlider_MDF', v=1.0, en=1, w=190, cw=[[2, 40], [1, 55]], pre=2, max=1.0, f=1, s= 0.1, vis=1,
                        l='Smooth intensity', h=40, min=0.0, ann='Drag the slider or directly fill in the value (0-1) to set the smooth intensity')
    cmds.button('button_MDF', w=66, h=40, c=lambda *args: szfa_anim_curves_smooth(),
                bgc=[0.02439917601281758, 0.2574044403753719, 0.2684977492942702], l='Fix jitter', ann='Start smooth animation curve')
    cmds.separator('separator02_MDF', st='single', en=1, w=280, h=2, vis=1, bgc=[0.0, 0.0, 0.0], hr=1)
    # Edit layout
    cmds.formLayout('formLayout_main_MDF', e=1, af=[[u'separator01_MDF', 'left', 0], ['separator01_MDF', 'top', 1]],
                    ap=[['separator02_MDF', 'top', 42, 10], ['button_MDF', 'left', 185, 5], ['button_MDF', 'top', 3, 5],
                        ['floatSlider_MDF', 'top', 2, 5]])
    # show window
    cmds.showWindow('window_main_MDF')