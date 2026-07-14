# -*- coding: utf-8 -*-
"""
Overlapper - Tool for creating overlapping action & follow-through in Maya.
Converted from Overlapper release 1.2 (MEL) by Dmitrii Kolpakov.
Ported to Python 3 for Animeow Toolboard v02.
"""

import random
import maya.cmds as cmds
import maya.mel as mel

def clean_up():
    """Dọn dẹp tất cả các đối tượng tạm của Overlapper"""
    temp_patterns = [
        "*_OverlapJoint*",
        "*:*_OverlapJoint*",
        "*:*:*_OverlapJoint*",
        "*overlapOffsetLocator*",
        "overlapResultLocatorOut*",
        "TEMP_Offset_locator*",
        "*overlapOffsetIKLocator*",
        "OverlapperSet",
        "OverlapperWorkSet",
        "OverlapperOverlapResultLocatorSet",
        "overlapOffsetLocatorWind*"
    ]
    for pattern in temp_patterns:
        try:
            objs = cmds.ls(pattern)
            if objs:
                cmds.delete(objs)
        except Exception:
            pass
            
    # Kết thúc progress window nếu đang hiển thị
    try:
        if cmds.progressWindow(query=True, isInterruptable=True):
            cmds.progressWindow(endProgress=True)
    except Exception:
        pass

def get_control_chains(selected_roots):
    """
    Trích xuất các chuỗi control liên kết trực tiếp trong phân cấp từ các roots được chọn.
    """
    all_nurbs = set(cmds.listTransforms(type="nurbsCurve") or [])
    chains = []
    
    for root in selected_roots:
        current_chain = [root]
        current_node = root
        
        while True:
            children = cmds.listRelatives(current_node, children=True, type="transform") or []
            nurbs_children = [c for c in children if c in all_nurbs]
            if not nurbs_children:
                break
            # Đi theo nhánh đầu tiên (pickWalk down)
            next_node = nurbs_children[0]
            current_chain.append(next_node)
            current_node = next_node
            
        chains.append(current_chain)
            
    return chains

def execute_overlapper(softness=3.0, scale=1.0, wind_enabled=False, wind_scale=1.0, wind_speed=1.0,
                       first_ctrl_skip=False, translate_mode=False, hierarchy_mode=False,
                       cycle_mode=False, bake_on_layer=False, adaptive_scale=True, create_sel_set=True):
    """
    Điểm bắt đầu chạy của Overlapper starter logic.
    """
    sel = cmds.ls(sl=True) or []
    if not sel:
        cmds.warning("Vui lòng chọn ít nhất một đối tượng điều khiển!")
        return False, "Vui lòng chọn ít nhất một đối tượng điều khiển!"
        
    # Xóa set tạm nếu có
    if cmds.objExists("OverlapperWorkSet"):
        cmds.delete("OverlapperWorkSet")
        
    cmds.progressWindow(
        title="Animeow Overlapper",
        progress=0,
        status="Chuẩn bị...",
        isInterruptable=True
    )
    
    # Chế độ Hierarchy: Lọc các chuỗi con dưới phân cấp
    if hierarchy_mode:
        chains = get_control_chains(sel)
        for chain in chains:
            if len(chain) > 1 or (len(chain) == 1 and first_ctrl_skip):
                overlap_chain(
                    chain, softness, scale, wind_enabled, wind_scale, wind_speed,
                    first_ctrl_skip, translate_mode, cycle_mode, bake_on_layer,
                    adaptive_scale, create_sel_set
                )
            else:
                cmds.warning(f"Bỏ qua node {chain[0]} vì phân cấp không đủ 2 control.")
    else:
        # Không có Hierarchy: Áp dụng trực tiếp cho danh sách được chọn
        if len(sel) > 1:
            overlap_chain(
                sel, softness, scale, wind_enabled, wind_scale, wind_speed,
                first_ctrl_skip, translate_mode, cycle_mode, bake_on_layer,
                adaptive_scale, create_sel_set
            )
        else:
            cmds.progressWindow(endProgress=True)
            cmds.warning("Vui lòng chọn nhiều hơn 1 control hoặc bật tùy chọn Hierarchy!")
            return False, "Vui lòng chọn nhiều hơn 1 control hoặc bật tùy chọn Hierarchy!"
            
    return True, "Overlapping hoàn tất thành công!"

def overlap_chain(controls, softness, scale, wind_enabled, wind_scale, wind_speed,
                  first_ctrl_skip, translate_mode, cycle_mode, bake_on_layer,
                  adaptive_scale, create_sel_set):
    """
    Xử lý Overlapping core trên 1 chuỗi control cụ thể.
    """
    if not controls:
        return
        
    cmds.cycleCheck(evaluation=False)
    
    # 1. Xác định Time Range từ Timeline slider
    try:
        gPlayBackSlider = mel.eval('$tmp = $gPlayBackSlider')
        time_range = cmds.timeControl(gPlayBackSlider, query=True, rangeArray=True)
    except Exception:
        time_range = None
        
    if time_range and (time_range[1] - time_range[0]) > 1:
        time_start = int(time_range[0])
        time_end = int(time_range[1])
    else:
        time_start = int(cmds.playbackOptions(query=True, minTime=True))
        time_end = int(cmds.playbackOptions(query=True, maxTime=True))
        
    current_time = cmds.currentTime(query=True)
    cmds.currentTime(time_start)
    
    i_loop = len(controls)
    controls_clean = [c.split(":")[-1] for c in controls]
    
    # 2. Tạo Locators tạm TEMP_Offset_locator
    temp_locators = []
    for i, ctrl in enumerate(controls):
        loc = cmds.spaceLocator(name=f"TEMP_Offset_locator{i}")[0]
        temp_locators.append(loc)
        cmds.delete(cmds.parentConstraint(ctrl, loc, weight=1))
        
    # 3. Tạo khớp xương Joint tạm
    overlap_joints = []
    cmds.select(clear=True)
    for i, ctrl in enumerate(controls):
        world_pos = cmds.xform(f"TEMP_Offset_locator{i}", query=True, worldSpace=True, translation=True)
        # Đặt tên khớp xương tạm
        j_name = f"{ctrl}_OverlapJoint"
        if cmds.objExists(j_name):
            cmds.delete(j_name)
        joint_name = cmds.joint(radius=1, name=j_name, position=world_pos)
        overlap_joints.append(joint_name)
        if i > 0:
            cmds.joint(overlap_joints[i-1], edit=True, zeroScaleOrient=True, orientJoint="xyz", secondaryAxisOrient="yup")
            
    cmds.delete(temp_locators)
    
    # Định hướng cho Joint cuối cùng
    last_joint = overlap_joints[-1]
    cmds.select(last_joint)
    dup_joint = cmds.duplicate(last_joint, renameChildren=True)[0]
    cmds.move(2, 0, 0, dup_joint, relative=True, objectSpace=True, worldSpaceDistance=True)
    world_pos_last = cmds.xform(dup_joint, query=True, worldSpace=True, translation=True)
    
    cmds.select(last_joint)
    orient_joint = cmds.joint(radius=1, name=f"{controls[-1]}LastOrientJoint", position=world_pos_last)
    cmds.joint(last_joint, edit=True, zeroScaleOrient=True, orientJoint="xyz", secondaryAxisOrient="yup")
    cmds.delete(dup_joint)
    
    overlap_joints.append(orient_joint)
    
    # Cấu hình secondary axis orient
    cmds.joint(overlap_joints[0], edit=True, orientJoint="xyz", secondaryAxisOrient="zup", children=True, zeroScaleOrient=True)
    
    # Đo khoảng cách joints
    joints_lengths = []
    for i in range(1, i_loop + 1):
        dist = cmds.getAttr(f"{overlap_joints[i]}.translateX")
        joints_lengths.append(dist)
        
    sum_length = sum(joints_lengths)
    average_length = (sum_length - 2.0) / len(joints_lengths) if joints_lengths else 1.0
    cmds.setAttr(f"{controls[-1]}LastOrientJoint.translateX", average_length)
    
    # Constrain Joints -> Controls
    start_idx = 1 if first_ctrl_skip and not translate_mode else 0
    for i in range(start_idx, i_loop):
        cmds.pointConstraint(controls[i], overlap_joints[i], maintainOffset=True, weight=1)
        cmds.orientConstraint(controls[i], overlap_joints[i], maintainOffset=True, weight=1)
        
    # Nướng (Bake) joints
    cmds.bakeResults(
        overlap_joints[:-1],
        simulation=False,
        time=(time_start, time_end),
        sampleBy=1,
        disableImplicitControl=True,
        preserveOutsideKeys=True,
        sparseAnimCurveBake=False,
        bakeOnOverrideLayer=False,
        minimizeRotation=False
    )
    cmds.delete(cmds.listConnections(overlap_joints[:-1], type="constraint") or [])
    
    # Cycle lặp
    cycle_length = time_end - time_start
    if cycle_mode:
        for i in range(start_idx, i_loop):
            joint_clean = controls[i] + "_OverlapJoint"
            curves = cmds.keyframe(joint_clean, query=True, name=True) or []
            if curves:
                cmds.selectKey(curves, time=(time_start, time_end))
                cmds.copyKey()
                cmds.pasteKey(time=time_end, option="insert", copies=2, connect=False)
        time_end = time_end + 2 * cycle_length
        
    # Tạo Locators offset và dịch trễ keyframe
    offset_locators = []
    offset_ik_locators = []
    result_locators = []
    
    progress_step = 100.0 / i_loop
    current_progress = 0
    
    for i in range(i_loop):
        current_progress += progress_step
        cmds.progressWindow(edit=True, progress=int(current_progress), status=f"Overlapping: {int(current_progress)}%")
        
        # 1. Offset locator
        offset_loc = cmds.spaceLocator(name=f"overlapOffsetLocator{i}")[0]
        offset_locators.append(offset_loc)
        cmds.delete(cmds.pointConstraint(overlap_joints[i], offset_loc, offset=(0,0,0), weight=1))
        cmds.delete(cmds.orientConstraint(overlap_joints[i], offset_loc, offset=(0,0,0), weight=1))
        
        # 2. Offset IK locator
        offset_ik_loc = cmds.spaceLocator(name=f"overlapOffsetIKLocator{i}")[0]
        offset_ik_locators.append(offset_ik_loc)
        cmds.delete(cmds.pointConstraint(overlap_joints[i], offset_ik_loc, offset=(0,0,0), weight=1))
        cmds.delete(cmds.orientConstraint(overlap_joints[i], offset_ik_loc, offset=(0,0,0), weight=1))
        
        # Dịch chuyển offset
        cmds.select(offset_loc)
        scale_val = average_length if adaptive_scale else 1.0
        intensity_mult = average_length / (scale if scale > 0 else 0.001) * 5.0
        cmds.move(intensity_mult, 0, 0, relative=True, objectSpace=True, localSpace=True)
        
        cmds.parentConstraint(overlap_joints[i], offset_loc, maintainOffset=True, weight=1)
        cmds.parentConstraint(overlap_joints[i], offset_ik_loc, maintainOffset=True, weight=1)
        
        cmds.bakeResults(
            [offset_loc, offset_ik_loc],
            simulation=False,
            time=(time_start, time_end),
            sampleBy=1,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            sparseAnimCurveBake=False,
            bakeOnOverrideLayer=False,
            minimizeRotation=False,
            controlPoints=False,
            shape=True
        )
        cmds.delete(cmds.listConnections([offset_loc, offset_ik_loc], type="constraint") or [])
        
        # Lọc xoay euler
        offset_rot_curves = cmds.keyframe(offset_loc, query=True, name=True) or []
        rot_curves_only = [c for c in offset_rot_curves if "rotate" in c.lower()]
        if rot_curves_only:
            cmds.filterCurve(rot_curves_only)
            
        # Tạo Wind Locator (Gió)
        wind_loc = cmds.spaceLocator(name=f"overlapOffsetLocatorWind{i}")[0]
        cmds.parent(wind_loc, offset_loc)
        cmds.makeIdentity(wind_loc, apply=False, translate=True, rotate=True, scale=True)
        
        # Dịch trễ keyframe
        time_shift_neg = -1 * softness
        time_shift_current = softness + 1
        
        loc_curves = cmds.keyframe(offset_loc, query=True, name=True) or []
        ik_curves = cmds.keyframe(offset_ik_loc, query=True, name=True) or []
        
        for curve in loc_curves + ik_curves:
            cmds.keyframe(curve, edit=True, includeUpperBound=True, relative=True, option="over", timeChange=softness)
            cmds.selectKey(curve, add=True, time=(time_shift_current, time_shift_current))
            cmds.keyframe(animation="keys", option="over", relative=True, timeChange=time_shift_neg)
            
        # Locator trung gian
        in_loc_first = cmds.spaceLocator(name=f"overlapInLocator_first_{i}")[0]
        in_loc_second = cmds.spaceLocator(name=f"overlapInLocator_second_{i}")[0]
        res_loc = cmds.spaceLocator(name=f"overlapResultLocator_{i}")[0]
        result_locators.append(res_loc)
        
        cmds.parent(in_loc_first, overlap_joints[i])
        cmds.parent(in_loc_second, overlap_joints[i])
        cmds.parent(res_loc, overlap_joints[i])
        
        cmds.makeIdentity([in_loc_first, in_loc_second, res_loc], apply=False, translate=True, rotate=True, scale=True)
        
        cmds.select(in_loc_second)
        cmds.move(intensity_mult, 0, 0, relative=True, objectSpace=True, localSpace=True)
        
        in_loc_first_grp = cmds.group(in_loc_first, name=f"overlapInLocator_first_{i}grp")
        
        if translate_mode:
            cmds.pointConstraint(offset_ik_loc, in_loc_first_grp, maintainOffset=True, weight=1)
            
        cmds.parentConstraint(wind_loc, in_loc_second, maintainOffset=True, weight=1)
        cmds.aimConstraint(
            in_loc_second, in_loc_first_grp,
            maintainOffset=True, weight=1,
            aimVector=(1, 0, 0), upVector=(0, 1, 0),
            worldUpType="object", worldUpObject=in_loc_second
        )
        cmds.orientConstraint(in_loc_second, in_loc_first, maintainOffset=True, skip=["y", "z"], weight=1)
        cmds.parentConstraint(in_loc_first, res_loc, maintainOffset=True, weight=1)
        
        # Thổi gió
        if i == 0 and wind_enabled:
            wind_mult = 0.07 * intensity_mult * wind_scale
            speed_mult = 20.0 / (wind_speed if wind_speed > 0 else 0.001)
            
            cmds.setKeyframe(wind_loc, attribute=["translateY", "translateZ"], time=time_start)
            cmds.bakeResults(
                wind_loc,
                simulation=False,
                time=(time_start, time_end + speed_mult),
                sampleBy=speed_mult,
                disableImplicitControl=True,
                preserveOutsideKeys=True,
                sparseAnimCurveBake=False,
                bakeOnOverrideLayer=False,
                minimizeRotation=False,
                attribute=["translateY", "translateZ"]
            )
            
            wind_curves = cmds.keyframe(wind_loc, query=True, name=True) or []
            for curve in wind_curves:
                key_times = cmds.keyframe(curve, time=(time_start, time_end), query=True, timeChange=True) or []
                for kt in key_times:
                    vals = cmds.keyframe(curve, time=(kt, kt), query=True, valueChange=True) or []
                    if vals:
                        val_noise = vals[0] + wind_mult * random.uniform(-1.0, 1.0)
                        cmds.keyframe(curve, edit=True, includeUpperBound=True, option="over", valueChange=val_noise, time=(kt, kt))
            cmds.keyframe(f"{wind_loc}_translateY", edit=True, includeUpperBound=True, relative=True, option="over", timeChange=(speed_mult / 2.0))
            cmds.selectKey(f"{wind_loc}_translateY", add=True, time=((speed_mult / 2.0) + 1, (speed_mult / 2.0) + 1))
            cmds.keyframe(animation="keys", option="over", relative=True, timeChange=(speed_mult / -2.0))
            
        cmds.bakeResults(
            res_loc,
            simulation=False,
            time=(time_start, time_end),
            sampleBy=1,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            sparseAnimCurveBake=False,
            bakeOnOverrideLayer=False,
            minimizeRotation=False,
            controlPoints=False,
            shape=True
        )
        
        cmds.delete([in_loc_first, in_loc_first_grp, offset_loc, in_loc_second])
        
        res_loc_out = cmds.spaceLocator(name=f"overlapResultLocatorOut_{i}")[0]
        if not cmds.objExists("OverlapperOverlapResultLocatorSet"):
            cmds.sets(name="OverlapperOverlapResultLocatorSet", empty=True)
        cmds.sets(res_loc_out, forceElement="OverlapperOverlapResultLocatorSet")
        
        cmds.parentConstraint(res_loc, res_loc_out, weight=1)
        cmds.bakeResults(
            res_loc_out,
            simulation=False,
            time=(time_start, time_end),
            sampleBy=1,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            sparseAnimCurveBake=False,
            bakeOnOverrideLayer=False,
            minimizeRotation=False,
            controlPoints=False,
            shape=True
        )
        cmds.delete(res_loc)
        cmds.parentConstraint(res_loc_out, overlap_joints[i], weight=1, maintainOffset=True)
        
    # Constrain controls back to joints
    for i in range(i_loop):
        ctrl = controls[i]
        joint_temp = overlap_joints[i]
        
        r_channels = ["rx", "ry", "rz"]
        r_valid = True
        for ch in r_channels:
            if not cmds.getAttr(f"{ctrl}.{ch}", keyable=True) or cmds.getAttr(f"{ctrl}.{ch}", lock=True):
                r_valid = False
                break
        if r_valid:
            cmds.orientConstraint(joint_temp, ctrl, maintainOffset=True, weight=1)
            
        if translate_mode:
            t_channels = ["tx", "ty", "tz"]
            t_valid = True
            for ch in t_channels:
                if not cmds.getAttr(f"{ctrl}.{ch}", keyable=True) or cmds.getAttr(f"{ctrl}.{ch}", lock=True):
                    t_valid = False
                    break
            if t_valid:
                cmds.pointConstraint(joint_temp, ctrl, maintainOffset=True, weight=1)
                
    if cycle_mode:
        time_start_pb = int(cmds.playbackOptions(query=True, minTime=True))
        time_end_pb = int(cmds.playbackOptions(query=True, maxTime=True))
        cycle_len = time_end_pb - time_start_pb
        
        euler_objs = cmds.sets("OverlapperOverlapResultLocatorSet", query=True) or []
        for obj in euler_objs:
            for attr in ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]:
                curve = f"{obj}_{attr}"
                if cmds.objExists(curve):
                    cmds.keyframe(curve, edit=True, includeUpperBound=True, relative=True, option="over", timeChange=(-2 * cycle_len))
                    
    # Lọc các controls thực để bake
    bake_controls = list(controls)
    if first_ctrl_skip and not translate_mode:
        if controls[0] in bake_controls:
            bake_controls.remove(controls[0])
            
    time_start_final = int(cmds.playbackOptions(query=True, minTime=True))
    time_end_final = int(cmds.playbackOptions(query=True, maxTime=True))
    
    # Bake kết quả trả về các controls thực
    anim_layer = None
    if bake_on_layer:
        anim_layer = cmds.animLayer("Overlapper_Layer", override=True)
        cmds.select(bake_controls)
        cmds.animLayer(anim_layer, edit=True, addSelectedObjects=True)
        
    cmds.bakeResults(
        bake_controls,
        simulation=False,
        time=(time_start_final, time_end_final),
        sampleBy=1,
        disableImplicitControl=True,
        preserveOutsideKeys=True,
        sparseAnimCurveBake=False,
        bakeOnOverrideLayer=bake_on_layer,
        overrideLayer=anim_layer,
        minimizeRotation=False,
        controlPoints=False,
        shape=False,
        attribute=["tx", "ty", "tz", "rx", "ry", "rz"]
    )
    
    # Tạo selection set để dễ chọn lại
    if create_sel_set:
        if not cmds.objExists("OverlapperSet"):
            cmds.sets(name="OverlapperSet", empty=True)
        cmds.sets(bake_controls, forceElement="OverlapperSet")
        
    if not cmds.objExists("OverlapperWorkSet"):
        cmds.sets(name="OverlapperWorkSet", empty=True)
    cmds.sets(bake_controls, forceElement="OverlapperWorkSet")
    
    # Dọn dẹp joints tạm
    cmds.delete(overlap_joints[:-1])
    cmds.delete(cmds.ls("overlapResultLocatorOut*"))
    cmds.delete(cmds.ls("*overlapOffsetIKLocator*"))
    
    cmds.currentTime(current_time)
    cmds.select(bake_controls)
    cmds.cycleCheck(evaluation=True)
    cmds.progressWindow(endProgress=True)
    
    # Euler filter animCurves của controls
    euler_curves = []
    work_objs = cmds.sets("OverlapperWorkSet", query=True) or []
    for obj in work_objs:
        attrs = cmds.listAttr(obj, keyable=True) or []
        for attr in attrs:
            anim_curve = cmds.listConnections(f"{obj}.{attr}", type="animCurve") or []
            euler_curves.extend(anim_curve)
            
    if euler_curves:
        cmds.filterCurve(list(set(euler_curves)))
        
    cmds.delete("OverlapperWorkSet")
    
    if cmds.objExists("OverlapperSet"):
        cmds.select("OverlapperSet")
