# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import maya.cmds as cmds

def smooth_anim_curves(smooth_strength):
    """
    Làm mượt các đường cong diễn hoạt được chọn (Smooth Animation Curves / Fix Jitter)
    smooth_strength: float từ 0.0 đến 1.0 (cường độ smooth)
    """
    # Lấy các animation curves đang chọn
    selected_anim_curves = cmds.keyframe(query=True, name=True)
    if not selected_anim_curves:
        cmds.warning("Vui lòng chọn ít nhất một controller hoặc animation curve để làm mượt!")
        return False, "Vui lòng chọn ít nhất một controller hoặc animation curve!"
        
    success_count = 0
    skipped_count = 0
    
    # Bắt đầu Undo Chunk
    cmds.undoInfo(openChunk=True, chunkName="AnimeowFixJitter")
    try:
        for each_curve in selected_anim_curves:
            # Query keyframes được chọn trên curve này, nếu không có thì lấy tất cả keyframe
            keyframes_selected = cmds.keyframe(each_curve, query=True, time=(), selected=True)
            if not keyframes_selected:
                keyframes = cmds.keyframe(each_curve, query=True, time=())
            else:
                keyframes = keyframes_selected
                
            if not keyframes or len(keyframes) < 3:
                skipped_count += 1
                keys_count = str(len(keyframes)) if keyframes else "0"
                print(each_curve + u" Chỉ có " + keys_count + u" keys được chọn. Bỏ qua (yêu cầu ít nhất 3 keys).")
                continue
                
            # Duplicate curve tạm thời để tính toán
            duplicated_nodes = cmds.duplicate(each_curve, name=each_curve + '_temp')
            if not duplicated_nodes:
                continue
            duplicated_anim_curve = duplicated_nodes[0]
            
            # Tính toán làm mượt trung bình cộng (1st Pass: lưu vào curve tạm)
            index = 1
            while index < len(keyframes) - 1:
                # Giá trị frame trước
                last_frame_value = cmds.keyframe(each_curve, query=True,
                                                 time=(keyframes[index - 1], keyframes[index - 1]), valueChange=True)
                # Giá trị frame hiện tại
                current_frame_value = cmds.keyframe(each_curve, query=True, 
                                                    time=(keyframes[index], keyframes[index]), valueChange=True)
                # Giá trị frame sau
                next_frame_value = cmds.keyframe(each_curve, query=True,
                                                 time=(keyframes[index + 1], keyframes[index + 1]), valueChange=True)
                
                if last_frame_value and current_frame_value and next_frame_value:
                    average_value = (last_frame_value[0] + current_frame_value[0] + next_frame_value[0]) / 3.0
                    cmds.keyframe(duplicated_anim_curve, absolute=True, time=(keyframes[index], keyframes[index]),
                                  valueChange=average_value)
                index += 1
                
            # Áp dụng cường độ smooth vào curve gốc (2nd Pass)
            index = 1
            while index < len(keyframes) - 1:
                current_frame_value_duplicate_curve = cmds.keyframe(duplicated_anim_curve, query=True,
                                                                    time=(keyframes[index], keyframes[index]),
                                                                    valueChange=True)
                current_frame_value_orig_curve = cmds.keyframe(each_curve, query=True,
                                                               time=(keyframes[index], keyframes[index]),
                                                               valueChange=True)
                if current_frame_value_duplicate_curve and current_frame_value_orig_curve:
                    deviation_value = current_frame_value_orig_curve[0] - current_frame_value_duplicate_curve[0]
                    final_value = current_frame_value_orig_curve[0] - deviation_value * smooth_strength
                    cmds.keyframe(each_curve, absolute=True, time=(keyframes[index], keyframes[index]),
                                  valueChange=final_value)
                index += 1
                
            # Xóa curve tạm
            if cmds.objExists(duplicated_anim_curve):
                cmds.delete(duplicated_anim_curve)
            success_count += 1
            
        msg = "Đã làm mượt %d curves (Bỏ qua %d curves)" % (success_count, skipped_count)
        print("[AnimeowTool] %s" % msg)
        return True, msg
    except Exception as e:
        cmds.warning("Lỗi làm mượt curve: %s" % e)
        return False, str(e)
    finally:
        cmds.undoInfo(closeChunk=True)
