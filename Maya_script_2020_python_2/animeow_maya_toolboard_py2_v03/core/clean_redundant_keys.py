# -*- coding: utf-8 -*-
import maya.cmds as cmds

def clean_redundant_keys_on_curve(curve, tolerance=1e-5):
    """
    Don dep cac keyframe thua co gia tri bang nhau lien tiep tren mot animCurve.
    Chi xoa cac keyframe o giua trong mot chuoi gom 3 keyframe tro len co cung gia tri.
    """
    num_keys = cmds.keyframe(curve, query=True, keyframeCount=True)
    if num_keys < 3:
        return 0
        
    # Lay thong tin thoi gian va gia tri cua tat ca keyframe
    times = cmds.keyframe(curve, query=True, timeChange=True) or []
    values = cmds.keyframe(curve, query=True, valueChange=True) or []
    
    if len(times) != num_keys or len(values) != num_keys:
        return 0
        
    keys_to_delete = []
    
    # Duyet qua cac keyframe de tim chuoi key co gia tri bang nhau lien tiep
    i = 0
    while i < num_keys:
        val = values[i]
        start_idx = i
        # Tim xem chuoi gia tri bang val keo dai den dau
        while i + 1 < num_keys and abs(values[i + 1] - val) < tolerance:
            i += 1
        end_idx = i
        
        # Neu chuoi co tu 3 keyframe tro len cung gia tri
        if end_idx - start_idx >= 2:
            # Xoa cac keyframe o giua (giu lai key dau start_idx va key cuoi end_idx)
            for mid_idx in range(start_idx + 1, end_idx):
                keys_to_delete.append(times[mid_idx])
                
        i += 1
        
    if keys_to_delete:
        # Xoa cac keyframe thua tai cac moc thoi gian da chon
        for t in keys_to_delete:
            cmds.cutKey(curve, time=(t, t), option="keys", clear=True)
        return len(keys_to_delete)
        
    return 0

def clean_redundant_keys(objects=None, channels=None, tolerance=1e-5):
    """
    Don dep keyframe bang nhau lien tiep tren cac doi tuong duoc chon hoac cac channels duoc chon.
    """
    if not objects:
        objects = cmds.ls(sl=True) or []
        
    if not objects:
        cmds.warning("Vui long chon it nhat mot doi tuong de don dep keyframe!")
        return 0
        
    # Neu khong truyen channels, thu lay cac kenh dang boi xanh trong Channel Box
    if not channels:
        try:
            pkg_name = __name__.split('.')[0]
            round_tool = __import__(pkg_name + ".core.round_tool", fromlist=["get_selected_channels"])
            get_selected_channels = round_tool.get_selected_channels
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
            # Lay tat ca cac curve ket noi vao doi tuong
            obj_curves = cmds.keyframe(obj, query=True, name=True) or []
            curves.extend(obj_curves)
            
    curves = list(set(curves))
    if not curves:
        print("[CleanKey] Khong tim thay animCurve nao tren doi tuong duoc chon.")
        return 0
        
    total_deleted = 0
    cmds.undoInfo(openChunk=True, chunkName="CleanRedundantKeys")
    try:
        for curve in curves:
            deleted = clean_redundant_keys_on_curve(curve, tolerance)
            total_deleted += deleted
    except Exception as e:
        cmds.warning("Loi khi don dep keyframe: %s" % str(e))
    finally:
        cmds.undoInfo(closeChunk=True)
        
    if total_deleted > 0:
        print("[CleanKey] Da don dep thanh cong %d keyframe thua co gia tri bang nhau." % total_deleted)
    else:
        print("[CleanKey] Khong tim thay keyframe thua nao co gia tri bang nhau de don dep.")
        
    return total_deleted
