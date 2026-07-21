# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import os
import sys
import re
import shutil
import maya.cmds as cmds
import maya.mel as mel

def ensure_scripts_2022_path():
    """Tá»± Ä‘á»™ng kiá»ƒm tra vÃ  thÃªm thÆ° má»¥c chá»©a plugin bá»• trá»£ vÃ o sys.path"""
    core_dir = os.path.dirname(os.path.abspath(__file__))
    package_dir = os.path.dirname(core_dir)
    python3_dir = os.path.dirname(package_dir)
    workspace_root = os.path.dirname(python3_dir)
    
    dynamic_path = os.path.join(workspace_root, "Maya_script_2020_python_2", "Tool_reference", "scripts_2022")
    hardcoded_path = r"E:\AI_Work\Blender_Maya_Script\Maya_script_2020_python_2\Tool_reference\scripts_2022"
    
    thirdparty_path = os.path.join(package_dir, "thirdparty")
    path = ""
    if os.path.exists(thirdparty_path) and os.path.isdir(thirdparty_path) and len(os.listdir(thirdparty_path)) > 1:
        path = thirdparty_path
    elif os.path.exists(dynamic_path):
        path = dynamic_path
    elif os.path.exists(hardcoded_path):
        path = hardcoded_path

    if not path:
        print("[AnimeowShelf] Khong tim thay thu muc scripts_2022 hay thirdparty!")
        return ""
        
    if path not in sys.path:
        sys.path.insert(0, path)
        
    # ThÃªm thÆ° má»¥c src cá»§a Studio Library vÃ o sys.path
    sl_path = os.path.join(path, "studiolibrary-2.9.6.b3", "studiolibrary-2.9.6.b3", "src")
    if os.path.exists(sl_path) and sl_path not in sys.path:
        sys.path.insert(0, sl_path)
        
    return path

# =========================================================================
# --- CÃC HÃ€M TIá»†N ÃCH QUáº¢N LÃ Cáº¢NH (SCENE UTILITIES) ---
# =========================================================================

def toggle_graph_editor():
    """Báº­t/Táº¯t Graph Editor"""
    if cmds.window("graphEditor1Window", exists=True):
        cmds.deleteUI("graphEditor1Window", window=True)
        print("[AnimeowShelf] ÄÃ£ Ä‘Ã³ng Graph Editor.")
    else:
        mel.eval("GraphEditor;")
        print("[AnimeowShelf] ÄÃ£ má»Ÿ Graph Editor.")

def toggle_reference_editor():
    """Báº­t/Táº¯t Reference Editor"""
    if cmds.window("referenceEditorPanel1Window", exists=True):
        cmds.deleteUI("referenceEditorPanel1Window", window=True)
        print("[AnimeowShelf] ÄÃ£ Ä‘Ã³ng Reference Editor.")
    else:
        mel.eval("ReferenceEditor;")
        print("[AnimeowShelf] ÄÃ£ má»Ÿ Reference Editor.")

def toggle_outliner():
    """Báº­t/Táº¯t Outliner"""
    if cmds.window("outlinerPanel1Window", exists=True):
        cmds.deleteUI("outlinerPanel1Window", window=True)
        print("[AnimeowShelf] ÄÃ£ Ä‘Ã³ng Outliner.")
    else:
        mel.eval("OutlinerWindow;")
        print("[AnimeowShelf] ÄÃ£ má»Ÿ Outliner.")

def run_anti_virus():
    """Khá»Ÿi cháº¡y quÃ©t vÃ  diá»‡t virus trong scene"""
    from . import clean_virus
    cleaned = clean_virus.clean_virus()
    if cleaned:
        cmds.confirmDialog(
            title=u"Káº¿t quáº£ diá»‡t Virus",
            message=u"ÄÃ£ tÃ¬m tháº¥y vÃ  tiÃªu diá»‡t thÃ nh cÃ´ng %d node virus Ä‘á»™c háº¡i:\n%s" % (len(cleaned), ", ".join(cleaned)),
            button=[u"Tuyá»‡t vá»i"]
        )
    else:
        cmds.confirmDialog(
            title=u"Káº¿t quáº£ diá»‡t Virus",
            message=u"ChÃºc má»«ng! Scene cá»§a báº¡n hoÃ n toÃ n sáº¡ch sáº½, khÃ´ng phÃ¡t hiá»‡n virus nÃ o.",
            button=[u"Tuyá»‡t vá»i"]
        )

def create_parent_constraint(mo=True, skip_translate="none", skip_rotate="none"):
    """Táº¡o Parent Constraint cÃ³ tÃ¹y chá»n Maintain Offset vÃ  Skip Trá»¥c riÃªng cho Translate vÃ  Rotate"""
    sel = cmds.ls(sl=True) or []
    if len(sel) >= 2:
        try:
            cmds.parentConstraint(sel[:-1], sel[-1], mo=mo, skipTranslate=skip_translate, skipRotate=skip_rotate)
            print("[AnimeowShelf] ÄÃ£ táº¡o Parent Constraint thÃ nh cÃ´ng.")
        except Exception as e:
            cmds.warning("KhÃ´ng thá»ƒ táº¡o Parent Constraint: %s" % str(e))
    else:
        cmds.warning("Vui lÃ²ng chá»n Ã­t nháº¥t 2 Ä‘á»‘i tÆ°á»£ng (Ä‘á»‘i tÆ°á»£ng Ä‘áº§u lÃ  driver, Ä‘á»‘i tÆ°á»£ng cuá»‘i lÃ  driven)!")

def create_point_constraint(mo=True, skip_axes="none"):
    """Táº¡o Point Constraint cÃ³ tÃ¹y chá»n Maintain Offset vÃ  Skip Trá»¥c"""
    sel = cmds.ls(sl=True) or []
    if len(sel) >= 2:
        try:
            cmds.pointConstraint(sel[:-1], sel[-1], mo=mo, skip=skip_axes)
            print("[AnimeowShelf] ÄÃ£ táº¡o Point Constraint thÃ nh cÃ´ng.")
        except Exception as e:
            cmds.warning("KhÃ´ng thá»ƒ táº¡o Point Constraint: %s" % str(e))
    else:
        cmds.warning("Vui lÃ²ng chá»n Ã­t nháº¥t 2 Ä‘á»‘i tÆ°á»£ng!")

def create_orient_constraint(mo=True, skip_axes="none"):
    """Táº¡o Orient Constraint cÃ³ tÃ¹y chá»n Maintain Offset vÃ  Skip Trá»¥c"""
    sel = cmds.ls(sl=True) or []
    if len(sel) >= 2:
        try:
            cmds.orientConstraint(sel[:-1], sel[-1], mo=mo, skip=skip_axes)
            print("[AnimeowShelf] ÄÃ£ táº¡o Orient Constraint thÃ nh cÃ´ng.")
        except Exception as e:
            cmds.warning("KhÃ´ng thá»ƒ táº¡o Orient Constraint: %s" % str(e))
    else:
        cmds.warning("Vui lÃ²ng chá»n Ã­t nháº¥t 2 Ä‘á»‘i tÆ°á»£ng!")

def create_scale_constraint(mo=True, skip_axes="none"):
    """Táº¡o Scale Constraint cÃ³ tÃ¹y chá»n Maintain Offset vÃ  Skip Trá»¥c"""
    sel = cmds.ls(sl=True) or []
    if len(sel) >= 2:
        try:
            cmds.scaleConstraint(sel[:-1], sel[-1], mo=mo, skip=skip_axes)
            print("[AnimeowShelf] ÄÃ£ táº¡o Scale Constraint thÃ nh cÃ´ng.")
        except Exception as e:
            cmds.warning("KhÃ´ng thá»ƒ táº¡o Scale Constraint: %s" % str(e))
    else:
        cmds.warning("Vui lÃ²ng chá»n Ã­t nháº¥t 2 Ä‘á»‘i tÆ°á»£ng!")

def delete_obj_constraints():
    """XÃ³a táº¥t cáº£ constraint cá»§a Ä‘á»‘i tÆ°á»£ng Ä‘ang chá»n"""
    sel = cmds.ls(sl=True) or []
    if not sel:
        cmds.warning("Vui lÃ²ng chá»n Ã­t nháº¥t má»™t Ä‘á»‘i tÆ°á»£ng Ä‘á»ƒ xÃ³a constraint!")
        return
        
    deleted_count = 0
    for obj in sel:
        cons = cmds.listConnections(obj, type="constraint") or []
        for c in list(set(cons)):
            if cmds.objExists(c):
                try:
                    cmds.delete(c)
                    deleted_count += 1
                except Exception:
                    pass
    if deleted_count > 0:
        print("[AnimeowShelf] ÄÃ£ xÃ³a thÃ nh cÃ´ng %d constraint trÃªn cÃ¡c Ä‘á»‘i tÆ°á»£ng Ä‘Æ°á»£c chá»n." % deleted_count)
    else:
        print("[AnimeowShelf] KhÃ´ng tÃ¬m tháº¥y constraint nÃ o trÃªn cÃ¡c Ä‘á»‘i tÆ°á»£ng Ä‘Æ°á»£c chá»n.")

def save_increment():
    """LÆ°u increment phá»¥ dáº¡ng .0001, .0002..."""
    mel.eval("IncrementAndSave;")
    print("[AnimeowShelf] ÄÃ£ thá»±c hiá»‡n Save Increment.")

def save_up_version():
    """LÆ°u nÃ¢ng version chÃ­nh (_v01 -> _v02)"""
    scene_path = cmds.file(q=True, sceneName=True)
    if not scene_path:
        cmds.warning("Scene chÆ°a Ä‘Æ°á»£c lÆ°u! HÃ£y lÆ°u file trÆ°á»›c khi nÃ¢ng Version.")
        return
        
    scene_dir, scene_file = os.path.split(scene_path)
    file_name, ext = os.path.splitext(scene_file)
    
    # Regex tÃ¬m version _v01, _v02,... hoáº·c .v01, .v02...
    version_pattern = re.compile(r'([_\.]v)(\d+)(.*)', re.IGNORECASE)
    match = version_pattern.search(file_name)
    if match:
        prefix = file_name[:match.start()]
        v_prefix = match.group(1) # '_v' hoáº·c '.v'
        v_num_str = match.group(2) # '01', '1', '001'
        new_v_num = int(v_num_str) + 1
        new_v_num_str = str(new_v_num).zfill(len(v_num_str))
        new_file_name = prefix + v_prefix + new_v_num_str + ext
    else:
        # Náº¿u khÃ´ng cÃ³ _vXX nhÆ°ng cÃ³ háº­u tá»‘ increment (.0005)
        inc_pattern = re.compile(r'\.(\d{3,5})$')
        inc_match = inc_pattern.search(file_name)
        if inc_match:
            prefix = file_name[:inc_match.start()]
            new_file_name = prefix + "_v02" + ext
        else:
            new_file_name = file_name + "_v02" + ext
            
    new_scene_path = os.path.join(scene_dir, new_file_name).replace('\\', '/')
    
    # XÃ¡c nháº­n trÆ°á»›c khi nÃ¢ng
    res = cmds.confirmDialog(
        title="XÃ¡c nháº­n nÃ¢ng Version",
        message="Báº¡n cÃ³ muá»‘n nÃ¢ng version hiá»‡n táº¡i lÃªn phiÃªn báº£n má»›i khÃ´ng?\nTÃªn file má»›i:\n%s" % new_file_name,
        button=["Yes", "No"],
        defaultButton="Yes",
        cancelButton="No",
        dismissString="No"
    )
    if res == "No":
        return
        
    try:
        cmds.file(rename=new_scene_path)
        file_type = "mayaAscii" if ext.lower() == ".ma" else "mayaBinary"
        cmds.file(save=True, type=file_type)
        cmds.confirmDialog(
            title="ThÃ nh cÃ´ng",
            message="ÄÃ£ nÃ¢ng version thÃ nh cÃ´ng!\nTÃªn file má»›i: %s" % new_file_name,
            button=["OK"]
        )
        print("[AnimeowShelf] ÄÃ£ nÃ¢ng version thÃ nh cÃ´ng: %s" % new_file_name)
    except Exception as e:
        cmds.warning("Lá»—i xáº£y ra khi nÃ¢ng version: %s" % str(e))

def clean_folder():
    """Dá»n dáº¹p thÆ° má»¥c: Giá»¯ láº¡i 5 báº£n má»›i nháº¥t, chuyá»ƒn báº£n cÅ© vÃ o thÆ° má»¥c Old/"""
    scene_path = cmds.file(q=True, sceneName=True)
    if not scene_path:
        cmds.warning("Scene hiá»‡n táº¡i chÆ°a Ä‘Æ°á»£c lÆ°u trÃªn Ä‘Ä©a! HÃ£y lÆ°u file trÆ°á»›c khi thá»±c hiá»‡n dá»n dáº¹p.")
        return
        
    scene_dir, scene_file = os.path.split(scene_path)
    file_name, ext = os.path.splitext(scene_file)
    
    # RÃºt trÃ­ch tÃªn gá»‘c
    root_prefix = re.sub(r'([_\.]v\d+)?(\.\d{3,5})?(_org)?$', '', file_name, flags=re.IGNORECASE)
    
    try:
        files_in_dir = os.listdir(scene_dir)
    except Exception as e:
        cmds.warning("KhÃ´ng thá»ƒ truy cáº­p thÆ° má»¥c scene: %s" % str(e))
        return
        
    matched_files = []
    for f in files_in_dir:
        f_path = os.path.join(scene_dir, f).replace('\\', '/')
        if os.path.isfile(f_path) and f.lower().startswith(root_prefix.lower()) and f.lower().endswith(('.ma', '.mb')):
            mtime = os.path.getmtime(f_path)
            matched_files.append((f, f_path, mtime))
            
    if not matched_files:
        cmds.confirmDialog(title="ThÃ´ng bÃ¡o", message="KhÃ´ng tÃ¬m tháº¥y file nÃ o khá»›p trong thÆ° má»¥c Ä‘á»ƒ dá»n dáº¹p!", button=["OK"])
        return
        
    matched_files.sort(key=lambda x: x[2], reverse=True)
    keep_filenames = [x[0] for x in matched_files[:5]]
    
    if scene_file not in keep_filenames:
        keep_filenames.append(scene_file)
        
    files_to_move = [x for x in matched_files if x[0] not in keep_filenames]
    
    if not files_to_move:
        cmds.confirmDialog(
            title="ThÃ´ng bÃ¡o",
            message="ThÆ° má»¥c hiá»‡n táº¡i Ä‘ang ráº¥t sáº¡ch sáº½!\nChá»‰ cÃ³ %d tá»‡p khá»›p vÃ  toÃ n bá»™ Ä‘Ã£ Ä‘Æ°á»£c giá»¯ láº¡i (tá»‘i Ä‘a 5 tá»‡p gáº§n nháº¥t)." % len(matched_files),
            button=["OK"]
        )
        return
        
    confirm_msg = "Báº¡n cÃ³ muá»‘n dá»n dáº¹p thÆ° má»¥c nÃ y khÃ´ng?\n\n"
    confirm_msg += "- Giá»¯ láº¡i %d tá»‡p má»›i nháº¥t (bao gá»“m file Ä‘ang má»Ÿ).\n" % len(keep_filenames)
    confirm_msg += "- Di chuyá»ƒn %d tá»‡p cÅ© hÆ¡n vÃ o thÆ° má»¥c 'Old'.\n\nDanh sÃ¡ch file sáº½ di chuyá»ƒn:\n" % len(files_to_move)
    for f, _, _ in files_to_move[:10]:
        confirm_msg += "  + %s\n" % f
    if len(files_to_move) > 10:
        confirm_msg += "  + ... vÃ  %d file khÃ¡c.\n" % (len(files_to_move) - 10)
        
    res = cmds.confirmDialog(
        title="XÃ¡c nháº­n dá»n dáº¹p thÆ° má»¥c",
        message=confirm_msg,
        button=["Yes", "No"],
        defaultButton="Yes",
        cancelButton="No",
        dismissString="No"
    )
    if res == "No":
        return
        
    old_dir = os.path.join(scene_dir, "Old").replace('\\', '/')
    if not os.path.exists(old_dir):
        try:
            os.makedirs(old_dir)
        except Exception as e:
            cmds.warning("KhÃ´ng thá»ƒ táº¡o thÆ° má»¥c Old: %s" % str(e))
            return
            
    moved_count = 0
    errors = []
    for f, f_path, _ in files_to_move:
        dest_path = os.path.join(old_dir, f).replace('\\', '/')
        try:
            if os.path.exists(dest_path):
                os.remove(dest_path)
            shutil.move(f_path, dest_path)
            moved_count += 1
        except Exception as e:
            errors.append("%s: %s" % (f, str(e)))
            
    msg = "ÄÃ£ dá»n dáº¹p xong!\n- Di chuyá»ƒn thÃ nh cÃ´ng: %d file vÃ o thÆ° má»¥c 'Old'." % moved_count
    if errors:
        msg += "\n- Lá»—i xáº£y ra trÃªn %d file:\n" % len(errors)
        msg += "\n".join(errors[:5])
        if len(errors) > 5:
            msg += "\n... vÃ  %d lá»—i khÃ¡c." % (len(errors) - 5)
            
    cmds.confirmDialog(title="Káº¿t quáº£ dá»n dáº¹p", message=msg, button=["OK"])
    print("[AnimeowShelf] Clean folder hoÃ n táº¥t: di chuyá»ƒn %d file." % moved_count)

def fix_lost_shader():
    """Má»Ÿ khÃ³a default shading group Ä‘á»ƒ sá»­a lá»—i máº¥t shader (lÆ°á»›i xanh lÃ¡)"""
    try:
        if cmds.objExists('initialShadingGroup'):
            cmds.lockNode('initialShadingGroup', lock=False, lockUnpublished=False)
        if cmds.objExists('defaultTextureList1'):
            cmds.lockNode('defaultTextureList1', lock=False, lockUnpublished=False)
        cmds.confirmDialog(
            title="ThÃ nh cÃ´ng",
            message="ÄÃ£ má»Ÿ khÃ³a cÃ¡c node máº·c Ä‘á»‹nh thÃ nh cÃ´ng!\nBáº¡n cÃ³ thá»ƒ thá»­ gÃ¡n láº¡i shader hoáº·c import/export bÃ¬nh thÆ°á»ng.",
            button=["OK"]
        )
    except Exception as e:
        cmds.warning("KhÃ´ng thá»ƒ má»Ÿ khÃ³a cÃ¡c node máº·c Ä‘á»‹nh: %s" % str(e))

# =========================================================================
# --- CÃC HÃ€M KHá»žI CHáº Y á»¨NG Dá»¤NG PHá»¤ (LAUNCHERS CORES) ---
# =========================================================================

def launch_studiolibrary():
    """Khá»Ÿi cháº¡y Studio Library nhanh tá»« Shelf"""
    ensure_scripts_2022_path()
    try:
        import studiolibrary
        window = getattr(studiolibrary, "_window", None)
        if window is not None:
            try:
                window.close()
                studiolibrary._window = None
                print("[StudioLibrary] ÄÃ£ Ä‘Ã³ng Studio Library cÅ©.")
                return
            except Exception:
                pass
        studiolibrary._window = None
        studiolibrary.main()
    except Exception as e:
        cmds.warning("KhÃ´ng thá»ƒ cháº¡y Studio Library: %s" % str(e))

def launch_dwpicker():
    """Khá»Ÿi cháº¡y DWPicker nhanh tá»« Shelf"""
    ensure_scripts_2022_path()
    try:
        import dwpicker
        from dwpicker.main import WINDOW_CONTROL_NAME
        if cmds.workspaceControl(WINDOW_CONTROL_NAME, exists=True):
            dwpicker.close()
            print("[DWPicker] ÄÃ£ Ä‘Ã³ng DWPicker.")
        else:
            dwpicker.show()
    except Exception as e:
        cmds.warning("KhÃ´ng thá»ƒ cháº¡y DWPicker: %s" % str(e))

def launch_tweenmachine():
    """Khá»Ÿi cháº¡y Tween Machine nhanh tá»« Shelf"""
    path = ensure_scripts_2022_path()
    if not path:
        return
    tween_mel_path = os.path.join(path, "tweenMachine.mel").replace("\\", "/")
    if not os.path.exists(tween_mel_path):
        cmds.warning("KhÃ´ng tÃ¬m tháº¥y file tweenMachine.mel táº¡i: %s" % tween_mel_path)
        return
        
    # ThÃªm thÆ° má»¥c chá»©a tweenMachine vÃ o MAYA_SCRIPT_PATH cá»§a Maya
    try:
        current_script_path = os.environ.get("MAYA_SCRIPT_PATH", "")
        if path not in current_script_path:
            os.environ["MAYA_SCRIPT_PATH"] = path + os.pathsep + current_script_path
            # Äá»“ng bá»™ láº¡i vá»›i Maya
            mel.eval("rehash;")
    except Exception:
        pass
        
    try:
        if cmds.window("tweenMachineWin", exists=True):
            cmds.deleteUI("tweenMachineWin")
            print("[TweenMachine] ÄÃ£ Ä‘Ã³ng Tween Machine.")
        else:
            mel.eval('source "%s"; tweenMachine;' % tween_mel_path)
            print("[TweenMachine] ÄÃ£ má»Ÿ Tween Machine.")
    except Exception as e:
        cmds.warning("KhÃ´ng thá»ƒ cháº¡y Tween Machine: %s" % str(e))

def launch_atools():
    """Khá»Ÿi cháº¡y aTools nhanh tá»« Shelf"""
    ensure_scripts_2022_path()
    try:
        from aTools.animTools.animBar import animBarUI
        animBarUI.show(mode="toggle")
    except Exception as e:
        try:
            import aTools.general.main as aToolsMain
            aToolsMain.show()
        except Exception as e2:
            cmds.warning("KhÃ´ng thá»ƒ cháº¡y aTools: %s" % str(e))

def launch_animo():
    """Khá»Ÿi cháº¡y Animo nhanh tá»« Shelf"""
    thirdparty_dir = ensure_scripts_2022_path()
    if not thirdparty_dir:
        return
        
    animo_data_path = os.path.join(thirdparty_dir, "Animo_v5.9.6", "Animo_v5.9.6", "Animo_Data")
    if not os.path.exists(animo_data_path):
        cmds.warning("KhÃ´ng tÃ¬m tháº¥y thÆ° má»¥c Animo_Data táº¡i: %s" % animo_data_path)
        return
        
    animo_visible = False
    if cmds.workspaceControl('animo', exists=True):
        animo_visible = cmds.workspaceControl('animo', query=True, visible=True)
        
    qt_toolbar_visible = False
    existing_qt_toolbar = None
    try:
        import maya.OpenMayaUI as mui
        from PySide2 import QtWidgets as QtW
        from shiboken2 import wrapInstance
        maya_main_ptr = mui.MQtUtil.mainWindow()
        if maya_main_ptr:
            maya_main = wrapInstance(int(maya_main_ptr), QtW.QMainWindow)
            existing_qt_toolbar = maya_main.findChild(QtW.QWidget, "animo_qt_toolbar")
            if existing_qt_toolbar and existing_qt_toolbar.isVisible():
                qt_toolbar_visible = True
    except Exception:
        pass

    if animo_visible or qt_toolbar_visible:
        if cmds.workspaceControl('animo', exists=True):
            cmds.workspaceControl('animo', edit=True, visible=False)
        if existing_qt_toolbar:
            try:
                existing_qt_toolbar.hide()
            except Exception:
                pass
        print("[Animo] ÄÃ£ Ä‘Ã³ng Animo.")
    else:
        if cmds.workspaceControl('animo', exists=True):
            cmds.deleteUI('animo', control=True)
        if existing_qt_toolbar:
            try:
                existing_qt_toolbar.show()
                print("[Animo] ÄÃ£ báº­t láº¡i animo_qt_toolbar.")
                return
            except Exception:
                pass
                
        # XoÃ¡ cache sys.modules
        mods_to_delete = [mod for mod in list(sys.modules.keys()) 
                          if 'Animo' in mod or 'animo' in mod or 'styleMod' in mod or 'barMod' in mod]
        for mod in mods_to_delete:
            del sys.modules[mod]
            
        # ThÃªm cÃ¡c Ä‘Æ°á»ng dáº«n náº¡p vÃ o sys.path
        animo_launcher_dir = os.path.join(animo_data_path, "Animo_Launcher")
        for p in [animo_data_path, animo_launcher_dir]:
            if p not in sys.path:
                sys.path.insert(0, p)
                
        # Load vÃ  thá»±c thi khá»Ÿi Ä‘á»™ng UI Animo
        try:
            import importlib.util
            launcher_file = os.path.join(animo_launcher_dir, "Animo_Launcher.py")
            spec = importlib.util.spec_from_file_location("Animo_Launcher_Module", launcher_file)
            launcher_module = importlib.util.module_from_spec(spec)
            sys.modules["Animo_Launcher_Module"] = launcher_module
            spec.loader.exec_module(launcher_module)
            _tb = launcher_module.toolbar()
            _tb.startUI()
            print("[Animo] ÄÃ£ khá»Ÿi cháº¡y Animo thÃ nh cÃ´ng.")
        except Exception as e:
            cmds.warning("Lá»—i khá»Ÿi cháº¡y Animo: %s" % str(e))


def create_arc_trail():
    """Táº¡o Arc Trail cho cÃ¡c váº­t thá»ƒ Ä‘ang chá»n (cháº¡y nhanh tá»« Shelf)"""
    sel = cmds.ls(sl=True) or []
    if not sel:
        cmds.warning("Vui lÃ²ng chá»n Ã­t nháº¥t má»™t váº­t thá»ƒ Ä‘á»ƒ táº¡o Arc Trail!")
        return
        
    start_frame = cmds.playbackOptions(q=True, minTime=True)
    end_frame = cmds.playbackOptions(q=True, maxTime=True)
    
    show_ticks = cmds.optionVar(query="animeow_at_show_ticks") if cmds.optionVar(exists="animeow_at_show_ticks") else True
    show_keys = cmds.optionVar(query="animeow_at_show_keys") if cmds.optionVar(exists="animeow_at_show_keys") else True
    tick_size = cmds.optionVar(query="animeow_at_tick_size") if cmds.optionVar(exists="animeow_at_tick_size") else 0.1
    
    show_ticks = bool(show_ticks)
    show_keys = bool(show_keys)
    tick_size = float(tick_size)
    
    from . import arc_tracker
    tracker = arc_tracker.ArcTracker()
    
    cmds.undoInfo(openChunk=True, chunkName="CreateArcTrail")
    try:
        for obj in sel:
            tracker.create_trail(
                obj=obj,
                start_frame=start_frame,
                end_frame=end_frame,
                show_ticks=show_ticks,
                show_keys=show_keys,
                tick_size=tick_size
            )
        print("[AnimeowShelf] ÄÃ£ váº½ Arc Trail thÃ nh cÃ´ng cho %d váº­t thá»ƒ!" % len(sel))
    except Exception as e:
        cmds.warning("Lá»—i váº½ Trail: %s" % str(e))
    finally:
        cmds.undoInfo(closeChunk=True)

# =========================================================================
# --- LOGIC Táº O VÃ€ Cáº¬P NHáº¬T SHELF ---
# =========================================================================

def create_shelf():
    """Táº¡o hoáº·c cáº­p nháº­t Shelf 'Animeow' vá»›i Ä‘áº§y Ä‘á»§ 20 nÃºt cÃ´ng cá»¥ nhanh"""
    shelf_name = "Animeow"
    
    # 1. TÃ¬m shelf tab layout cá»§a Maya
    gShelfTopLevel = mel.eval("$tmpVar=$gShelfTopLevel")
    if not gShelfTopLevel:
        cmds.warning("KhÃ´ng tÃ¬m tháº¥y thanh Shelf cá»§a Maya!")
        return
        
    # 2. Táº¡o shelf náº¿u chÆ°a cÃ³
    if not cmds.shelfLayout(shelf_name, exists=True):
        cmds.shelfLayout(shelf_name, parent=gShelfTopLevel)
        print("[AnimeowShelf] ÄÃ£ táº¡o Shelf má»›i: %s" % shelf_name)
    else:
        # Náº¿u Ä‘Ã£ cÃ³, dá»n dáº¹p cÃ¡c nÃºt cÅ© trÆ°á»›c Ä‘á»ƒ cáº­p nháº­t sáº¡ch sáº½
        children = cmds.shelfLayout(shelf_name, query=True, childArray=True) or []
        for child in children:
            try:
                cmds.deleteUI(child)
            except Exception:
                pass
        print("[AnimeowShelf] ÄÃ£ lÃ m sáº¡ch Shelf cÅ© Ä‘á»ƒ cáº­p nháº­t.")
        
    # 3. TÃ¬m thÆ° má»¥c icons vÃ  hÃ m náº¡p icon tuyá»‡t Ä‘á»‘i
    core_dir = os.path.dirname(os.path.abspath(__file__))
    package_dir = os.path.dirname(core_dir)
    icons_dir = os.path.join(package_dir, "icons")
    
    def get_icon(icon_name, fallback):
        full_path = os.path.join(icons_dir, icon_name)
        if os.path.exists(full_path):
            return full_path
        return fallback

    # 4. Äá»‹nh nghÄ©a danh sÃ¡ch cÃ¡c nÃºt báº¥m
    tools = [
        {
            "label": "ATB",
            "annotation": "Má»Ÿ Animeow Toolboard Ä‘áº§y Ä‘á»§",
            "image": get_icon("atb_icon.png", "fileOpen.png"),
            "command": "import sys\nfor m in list(sys.modules.keys()):\n    if m.startswith('animeow_maya_toolboard_v01'):\n        del sys.modules[m]\nimport animeow_maya_toolboard_v01\nanimeow_maya_toolboard_v01.show()"
        },
        {
            "label": "Link",
            "annotation": "Má»Ÿ cá»­a sá»• Constraint & Smart Link Ä‘á»™c láº­p",
            "image": get_icon("link_icon.png", "parentConstraint.png"),
            "command": "import sys\nfor m in list(sys.modules.keys()):\n    if m.startswith('animeow_maya_toolboard_v01'):\n        del sys.modules[m]\nimport animeow_maya_toolboard_v01\nanimeow_maya_toolboard_v01.show(standalone_tab='smart_link')"
        },
        {
            "label": "Bake",
            "annotation": "Má»Ÿ cá»­a sá»• Smart World Bake & Pivot Ä‘á»™c láº­p",
            "image": get_icon("bake_icon.png", "save.png"),
            "command": "import sys\nfor m in list(sys.modules.keys()):\n    if m.startswith('animeow_maya_toolboard_v01'):\n        del sys.modules[m]\nimport animeow_maya_toolboard_v01\nanimeow_maya_toolboard_v01.show(standalone_tab='world_bake')"
        },
        {
            "label": "Curve",
            "annotation": "Má»Ÿ cá»­a sá»• Curve & Motion Ä‘á»™c láº­p",
            "image": get_icon("curve_icon.png", "menuIconWindow.png"),
            "command": "import sys\nfor m in list(sys.modules.keys()):\n    if m.startswith('animeow_maya_toolboard_v01'):\n        del sys.modules[m]\nimport animeow_maya_toolboard_v01\nanimeow_maya_toolboard_v01.show(standalone_tab=1)"
        },
        {
            "label": "Fav",
            "annotation": "Má»Ÿ cá»­a sá»• cÃ´ng cá»¥ yÃªu thÃ­ch (Favorite Tools: LÃ m trÃ²n sá»‘ & Dá»n Key)",
            "image": get_icon("fav_icon.png", "menuIconWindow.png"),
            "command": "import sys\nfor m in list(sys.modules.keys()):\n    if m.startswith('animeow_maya_toolboard_v01'):\n        del sys.modules[m]\nimport animeow_maya_toolboard_v01\nanimeow_maya_toolboard_v01.show(standalone_tab='fav_tools')"
        },
        {
            "label": "Rig",
            "annotation": "Má»Ÿ cá»­a sá»• Rig & Mirror Ä‘á»™c láº­p",
            "image": get_icon("rig_icon.png", "polyMesh.png"),
            "command": "import sys\nfor m in list(sys.modules.keys()):\n    if m.startswith('animeow_maya_toolboard_v01'):\n        del sys.modules[m]\nimport animeow_maya_toolboard_v01\nanimeow_maya_toolboard_v01.show(standalone_tab=2)"
        },
        {
            "label": "Play",
            "annotation": "Má»Ÿ cá»­a sá»• Output & Scene (Playblast) Ä‘á»™c láº­p",
            "image": get_icon("play_icon.png", "playblast.png"),
            "command": "import sys\nfor m in list(sys.modules.keys()):\n    if m.startswith('animeow_maya_toolboard_v01'):\n        del sys.modules[m]\nimport animeow_maya_toolboard_v01\nanimeow_maya_toolboard_v01.show(standalone_tab=3)"
        },
        {
            "label": "Arc",
            "annotation": "Má»Ÿ cá»­a sá»• cáº¥u hÃ¬nh váº½ Arc Tracker Ä‘á»™c láº­p",
            "image": get_icon("arc_icon.png", "motionTrail.png"),
            "command": "import sys\nfor m in list(sys.modules.keys()):\n    if m.startswith('animeow_maya_toolboard_v01'):\n        del sys.modules[m]\nimport animeow_maya_toolboard_v01\nanimeow_maya_toolboard_v01.show(standalone_tab='arc_tracker')"
        },
        {
            "label": "Graph",
            "annotation": "Báº­t/Táº¯t Graph Editor",
            "image": "menuIconWindow.png",
            "command": "import animeow_maya_toolboard_v01.core.shelf as shelf; shelf.toggle_graph_editor()"
        },
        {
            "label": "Ref",
            "annotation": "Báº­t/Táº¯t Reference Editor",
            "image": "fileOpen.png",
            "command": "import animeow_maya_toolboard_v01.core.shelf as shelf; shelf.toggle_reference_editor()"
        },
        {
            "label": "Out",
            "annotation": "Báº­t/Táº¯t Outliner Window",
            "image": "menuIconWindow.png",
            "command": "import animeow_maya_toolboard_v01.core.shelf as shelf; shelf.toggle_outliner()"
        },
        {
            "label": "Const",
            "annotation": "Má»Ÿ há»™p cÃ´ng cá»¥ Quick Constraint Ä‘á»™c láº­p",
            "image": "parentConstraint.png",
            "command": "import sys\nfor m in list(sys.modules.keys()):\n    if m.startswith('animeow_maya_toolboard_v01'):\n        del sys.modules[m]\nimport animeow_maya_toolboard_v01\nanimeow_maya_toolboard_v01.show(standalone_tab='quick_const')"
        },
        {
            "label": "S.Inc",
            "annotation": "LÆ°u Increment phiÃªn báº£n phá»¥",
            "image": "save.png",
            "command": "import animeow_maya_toolboard_v01.core.shelf as shelf; shelf.save_increment()"
        },
        {
            "label": "S.Up",
            "annotation": "LÆ°u nÃ¢ng Version chÃ­nh",
            "image": "save.png",
            "command": "import animeow_maya_toolboard_v01.core.shelf as shelf; shelf.save_up_version()"
        },
        {
            "label": "FixSh",
            "annotation": "Sá»­a lá»—i xanh lÆ°á»›i (Fix Lost Shader)",
            "image": "polyMesh.png",
            "command": "import animeow_maya_toolboard_v01.core.shelf as shelf; shelf.fix_lost_shader()"
        },
        {
            "label": "Clean",
            "annotation": "Dá»n dáº¹p scenes cÅ© vÃ o thÆ° má»¥c Old",
            "image": "delete.png",
            "command": "import animeow_maya_toolboard_v01.core.shelf as shelf; shelf.clean_folder()"
        },
        {
            "label": "AntiV",
            "annotation": "QuÃ©t vÃ  diá»‡t Virus trong Scene (vaccine, gene, fuckvirus...)",
            "image": "delete.png",
            "command": "import animeow_maya_toolboard_v01.core.shelf as shelf; shelf.run_anti_virus()"
        },
        {
            "label": "Studio",
            "annotation": "Khá»Ÿi cháº¡y Studio Library",
            "image": "fileOpen.png",
            "command": "import animeow_maya_toolboard_v01.core.shelf as shelf; shelf.launch_studiolibrary()"
        },
        {
            "label": "DWP",
            "annotation": "Khá»Ÿi cháº¡y DWPicker",
            "image": "menuIconWindow.png",
            "command": "import animeow_maya_toolboard_v01.core.shelf as shelf; shelf.launch_dwpicker()"
        },
        {
            "label": "Tween",
            "annotation": "Khá»Ÿi cháº¡y Tween Machine",
            "image": "commandButton.png",
            "command": "import animeow_maya_toolboard_v01.core.shelf as shelf; shelf.launch_tweenmachine()"
        },
        {
            "label": "aTools",
            "annotation": "Khá»Ÿi cháº¡y aTools Anim School",
            "image": "commandButton.png",
            "command": "import animeow_maya_toolboard_v01.core.shelf as shelf; shelf.launch_atools()"
        },
        {
            "label": "Animo",
            "annotation": "Khá»Ÿi cháº¡y Animo Toolset",
            "image": "commandButton.png",
            "command": "import animeow_maya_toolboard_v01.core.shelf as shelf; shelf.launch_animo()"
        }
    ]
    
    # 4. ThÃªm tá»«ng nÃºt vÃ o Shelf
    for t in tools:
        cmds.shelfButton(
            parent=shelf_name,
            label=t["label"],
            annotation=t["annotation"],
            image1=t["image"],
            command=t["command"],
            sourceType="python",
            style="iconOnly",
            imageOverlayLabel=t["label"]
        )
        
    # 5. LÆ°u láº¡i thiáº¿t láº­p shelf cá»§a Maya
    try:
        mel.eval("saveAllShelves $gShelfTopLevel")
    except Exception:
        pass
    
    # 6. Hiá»ƒn thá»‹ thÃ´ng bÃ¡o
    cmds.confirmDialog(
        title=u"ThÃ nh cÃ´ng",
        message=u"ÄÃ£ táº¡o/cáº­p nháº­t thÃ nh cÃ´ng Shelf 'Animeow' vá»›i Ä‘áº§y Ä‘á»§ 20 nÃºt cÃ´ng cá»¥ nhanh!",
        button=[u"Tuyá»‡t vá»i"]
    )
