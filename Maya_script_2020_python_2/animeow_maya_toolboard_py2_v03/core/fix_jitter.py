# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import maya.cmds as cmds

def smooth_anim_curves(smooth_strength):
    """
    Lam muot cac duong cong dien hoat duoc chon (Smooth Animation Curves / Fix Jitter)
    smooth_strength: float tu 0.0 den 1.0 (cuong do smooth)
    """
    # Lay cac animation curves dang chon
    selected_anim_curves = cmds.keyframe(query=True, name=True)
    if not selected_anim_curves:
        cmds.warning("Vui long chon it nhat mot controller hoac animation curve de lam muot!")
        return False, "Vui long chon it nhat mot controller hoac animation curve!"
        
    success_count = 0
    skipped_count = 0
    
    # Bat dau Undo Chunk
    cmds.undoInfo(openChunk=True, chunkName="AnimeowFixJitter")
    try:
        for each_curve in selected_anim_curves:
            # Query keyframes duoc chon tren curve nay, neu khong co thi lay tat ca keyframe
            keyframes_selected = cmds.keyframe(each_curve, query=True, time=(), selected=True)
            if not keyframes_selected:
                keyframes = cmds.keyframe(each_curve, query=True, time=())
            else:
                keyframes = keyframes_selected
                
            if not keyframes or len(keyframes) < 3:
                skipped_count += 1
                keys_count = str(len(keyframes)) if keyframes else "0"
                print(each_curve + u" Chi co " + keys_count + u" keys duoc chon. Bo qua (yeu cau it nhat 3 keys).")
                continue
                
            # Duplicate curve tam thoi de tinh toan
            duplicated_nodes = cmds.duplicate(each_curve, name=each_curve + '_temp')
            if not duplicated_nodes:
                continue
            duplicated_anim_curve = duplicated_nodes[0]
            
            # Tinh toan lam muot trung binh cong (1st Pass: luu vao curve tam)
            index = 1
            while index < len(keyframes) - 1:
                # Gia tri frame truoc
                last_frame_value = cmds.keyframe(each_curve, query=True,
                                                 time=(keyframes[index - 1], keyframes[index - 1]), valueChange=True)
                # Gia tri frame hien tai
                current_frame_value = cmds.keyframe(each_curve, query=True, 
                                                    time=(keyframes[index], keyframes[index]), valueChange=True)
                # Gia tri frame sau
                next_frame_value = cmds.keyframe(each_curve, query=True,
                                                 time=(keyframes[index + 1], keyframes[index + 1]), valueChange=True)
                
                if last_frame_value and current_frame_value and next_frame_value:
                    average_value = (last_frame_value[0] + current_frame_value[0] + next_frame_value[0]) / 3.0
                    cmds.keyframe(duplicated_anim_curve, absolute=True, time=(keyframes[index], keyframes[index]),
                                  valueChange=average_value)
                index += 1
                
            # Ap dung cuong do smooth vao curve goc (2nd Pass)
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
                
            # Xoa curve tam
            if cmds.objExists(duplicated_anim_curve):
                cmds.delete(duplicated_anim_curve)
            success_count += 1
            
        msg = "Da lam muot %d curves (Bo qua %d curves)" % (success_count, skipped_count)
        print("[AnimeowTool] %s" % msg)
        return True, msg
    except Exception as e:
        cmds.warning("Loi lam muot curve: %s" % e)
        return False, str(e)
    finally:
        cmds.undoInfo(closeChunk=True)
