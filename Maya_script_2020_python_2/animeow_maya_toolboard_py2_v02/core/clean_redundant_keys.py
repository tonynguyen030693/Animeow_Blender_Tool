# -*- coding: utf-8 -*-
import maya.cmds as cmds

def clean_redundant_keys_on_curve(curve, tolerance=1e-5):
    """
    Dọn dẹp các keyframe thừa có giá trị bằng nhau liên tiếp trên một animCurve.
    Chỉ xóa các keyframe ở giữa trong một chuỗi gồm 3 keyframe trở lên có cùng giá trị.
    """
    num_keys = cmds.keyframe(curve, query=True, keyframeCount=True)
    if num_keys < 3:
        return 0
        
    # Lấy thông tin thời gian và giá trị của tất cả keyframe
    times = cmds.keyframe(curve, query=True, timeChange=True) or []
    values = cmds.keyframe(curve, query=True, valueChange=True) or []
    
    if len(times) != num_keys or len(values) != num_keys:
        return 0
        
    keys_to_delete = []
    
    # Duyệt qua các keyframe để tìm chuỗi key có giá trị bằng nhau liên tiếp
    i = 0
    while i < num_keys:
        val = values[i]
        start_idx = i
        # Tìm xem chuỗi giá trị bằng val kéo dài đến đâu
        while i + 1 < num_keys and abs(values[i + 1] - val) < tolerance:
            i += 1
        end_idx = i
        
        # Nếu chuỗi có từ 3 keyframe trở lên cùng giá trị
        if end_idx - start_idx >= 2:
            # Xóa các keyframe ở giữa (giữ lại key đầu start_idx và key cuối end_idx)
            for mid_idx in range(start_idx + 1, end_idx):
                keys_to_delete.append(times[mid_idx])
                
        i += 1
        
    if keys_to_delete:
        # Xóa các keyframe thừa tại các mốc thời gian đã chọn
        for t in keys_to_delete:
            cmds.cutKey(curve, time=(t, t), option="keys", clear=True)
        return len(keys_to_delete)
        
    return 0

def clean_redundant_keys(objects=None, channels=None, tolerance=1e-5):
    """
    Dọn dẹp keyframe bằng nhau liên tiếp trên các đối tượng được chọn hoặc các channels được chọn.
    """
    if not objects:
        objects = cmds.ls(sl=True) or []
        
    if not objects:
        cmds.warning("Vui lòng chọn ít nhất một đối tượng để dọn dẹp keyframe!")
        return 0
        
    # Nếu không truyền channels, thử lấy các kênh đang bôi xanh trong Channel Box
    if not channels:
        try:
            from .round_tool import get_selected_channels
            channels = get_selected_channels()
        except Exception:
            channels = None
            
    curves = []
    for obj in objects:
        if channels:
            for ch in channels:
                attr_path = "%s.%s" % (obj, ch)
                if cmds.objExists(attr_path):
                    ch_curves = cmds.keyframe(obj, attribute=ch, query=True, name=True) or []
                    curves.extend(ch_curves)
        else:
            # Lấy tất cả các curve kết nối vào đối tượng
            obj_curves = cmds.keyframe(obj, query=True, name=True) or []
            curves.extend(obj_curves)
            
    curves = list(set(curves))
    if not curves:
        print("[CleanKey] Không tìm thấy animCurve nào trên đối tượng được chọn.")
        return 0
        
    total_deleted = 0
    cmds.undoInfo(openChunk=True, chunkName="CleanRedundantKeys")
    try:
        for curve in curves:
            deleted = clean_redundant_keys_on_curve(curve, tolerance)
            total_deleted += deleted
    except Exception as e:
        cmds.warning("Lỗi khi dọn dẹp keyframe: %s" % str(e))
    finally:
        cmds.undoInfo(closeChunk=True)
        
    if total_deleted > 0:
        print("[CleanKey] Đã dọn dẹp thành công %d keyframe thừa có giá trị bằng nhau." % total_deleted)
    else:
        print("[CleanKey] Không tìm thấy keyframe thừa nào có giá trị bằng nhau để dọn dẹp.")
        
    return total_deleted
