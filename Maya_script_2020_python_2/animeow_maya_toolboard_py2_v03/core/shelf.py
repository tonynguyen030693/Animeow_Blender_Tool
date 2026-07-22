# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import os
import sys
import re
import shutil
import maya.cmds as cmds
import maya.mel as mel

def ensure_scripts_2022_path():
    """Tu dong kiem tra va them thu muc chua plugin bo tro vao sys.path"""
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
        
    # Them thu muc src cua Studio Library vao sys.path
    sl_path = os.path.join(path, "studiolibrary-2.9.6.b3", "studiolibrary-2.9.6.b3", "src")
    if os.path.exists(sl_path) and sl_path not in sys.path:
        sys.path.insert(0, sl_path)
        
    return path

# =========================================================================
# --- CAC HAM TIEN ICH QUAN LY CANH (SCENE UTILITIES) ---
# =========================================================================

def toggle_graph_editor():
    """Bat/Tat Graph Editor"""
    if cmds.window("graphEditor1Window", exists=True):
        cmds.deleteUI("graphEditor1Window", window=True)
        print("[AnimeowShelf] Da dong Graph Editor.")
    else:
        mel.eval("GraphEditor;")
        print("[AnimeowShelf] Da mo Graph Editor.")

def toggle_reference_editor():
    """Bat/Tat Reference Editor"""
    if cmds.window("referenceEditorPanel1Window", exists=True):
        cmds.deleteUI("referenceEditorPanel1Window", window=True)
        print("[AnimeowShelf] Da dong Reference Editor.")
    else:
        mel.eval("ReferenceEditor;")
        print("[AnimeowShelf] Da mo Reference Editor.")

def toggle_outliner():
    """Bat/Tat Outliner"""
    if cmds.window("outlinerPanel1Window", exists=True):
        cmds.deleteUI("outlinerPanel1Window", window=True)
        print("[AnimeowShelf] Da dong Outliner.")
    else:
        mel.eval("OutlinerWindow;")
        print("[AnimeowShelf] Da mo Outliner.")

def run_anti_virus():
    """Khoi chay quet va diet virus trong scene va he thong"""
    pkg_name = __name__.split('.')[0]
    clean_virus = __import__(pkg_name + ".core.clean_virus", fromlist=["clean_virus"])
    cleaned = clean_virus.clean_virus()
    if cleaned:
        display_items = cleaned[:10]
        msg_details = "\n".join("- " + item for item in display_items)
        if len(cleaned) > 10:
            msg_details += "\n... va %d phan tu khac." % (len(cleaned) - 10)
            
        cmds.confirmDialog(
            title="Ket qua diet Virus",
            message="Da tim thay va tieu diet thanh cong %d phan tu doc hai:\n\n%s" % (len(cleaned), msg_details),
            button=["Tuyet voi"]
        )
    else:
        cmds.confirmDialog(
            title="Ket qua diet Virus",
            message="Chuc mung! Scene va he thong cua ban hoan toan sach se, khong phat hien virus nao.",
            button=["Tuyet voi"]
        )


def create_parent_constraint(mo=True, skip_translate="none", skip_rotate="none"):
    """Tao Parent Constraint co tuy chon Maintain Offset va Skip Truc rieng cho Translate va Rotate"""
    sel = cmds.ls(sl=True) or []
    if len(sel) >= 2:
        try:
            cmds.parentConstraint(sel[:-1], sel[-1], mo=mo, skipTranslate=skip_translate, skipRotate=skip_rotate)
            print("[AnimeowShelf] Da tao Parent Constraint thanh cong.")
        except Exception as e:
            cmds.warning("Khong the tao Parent Constraint: %s" % str(e))
    else:
        cmds.warning("Vui long chon it nhat 2 doi tuong (doi tuong dau la driver, doi tuong cuoi la driven)!")

def create_point_constraint(mo=True, skip_axes="none"):
    """Tao Point Constraint co tuy chon Maintain Offset va Skip Truc"""
    sel = cmds.ls(sl=True) or []
    if len(sel) >= 2:
        try:
            cmds.pointConstraint(sel[:-1], sel[-1], mo=mo, skip=skip_axes)
            print("[AnimeowShelf] Da tao Point Constraint thanh cong.")
        except Exception as e:
            cmds.warning("Khong the tao Point Constraint: %s" % str(e))
    else:
        cmds.warning("Vui long chon it nhat 2 doi tuong!")

def create_orient_constraint(mo=True, skip_axes="none"):
    """Tao Orient Constraint co tuy chon Maintain Offset va Skip Truc"""
    sel = cmds.ls(sl=True) or []
    if len(sel) >= 2:
        try:
            cmds.orientConstraint(sel[:-1], sel[-1], mo=mo, skip=skip_axes)
            print("[AnimeowShelf] Da tao Orient Constraint thanh cong.")
        except Exception as e:
            cmds.warning("Khong the tao Orient Constraint: %s" % str(e))
    else:
        cmds.warning("Vui long chon it nhat 2 doi tuong!")

def create_scale_constraint(mo=True, skip_axes="none"):
    """Tao Scale Constraint co tuy chon Maintain Offset va Skip Truc"""
    sel = cmds.ls(sl=True) or []
    if len(sel) >= 2:
        try:
            cmds.scaleConstraint(sel[:-1], sel[-1], mo=mo, skip=skip_axes)
            print("[AnimeowShelf] Da tao Scale Constraint thanh cong.")
        except Exception as e:
            cmds.warning("Khong the tao Scale Constraint: %s" % str(e))
    else:
        cmds.warning("Vui long chon it nhat 2 doi tuong!")

def delete_obj_constraints():
    """Xoa tat ca constraint cua doi tuong dang chon"""
    sel = cmds.ls(sl=True) or []
    if not sel:
        cmds.warning("Vui long chon it nhat mot doi tuong de xoa constraint!")
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
        print("[AnimeowShelf] Da xoa thanh cong %d constraint tren cac doi tuong duoc chon." % deleted_count)
    else:
        print("[AnimeowShelf] Khong tim thay constraint nao tren cac doi tuong duoc chon.")

def save_increment():
    """Luu increment phu dang .0001, .0002..."""
    mel.eval("IncrementAndSave;")
    print("[AnimeowShelf] Da thuc hien Save Increment.")

def save_up_version():
    """Luu nang version chinh (_v01 -> _v02)"""
    scene_path = cmds.file(q=True, sceneName=True)
    if not scene_path:
        cmds.warning("Scene chua duoc luu! Hay luu file truoc khi nang Version.")
        return
        
    scene_dir, scene_file = os.path.split(scene_path)
    file_name, ext = os.path.splitext(scene_file)
    
    # Regex tim version _v01, _v02,... hoac .v01, .v02...
    version_pattern = re.compile(r'([_\.]v)(\d+)(.*)', re.IGNORECASE)
    match = version_pattern.search(file_name)
    if match:
        prefix = file_name[:match.start()]
        v_prefix = match.group(1) # '_v' hoac '.v'
        v_num_str = match.group(2) # '01', '1', '001'
        new_v_num = int(v_num_str) + 1
        new_v_num_str = str(new_v_num).zfill(len(v_num_str))
        new_file_name = prefix + v_prefix + new_v_num_str + ext
    else:
        # Neu khong co _vXX nhung co hau to increment (.0005)
        inc_pattern = re.compile(r'\.(\d{3,5})$')
        inc_match = inc_pattern.search(file_name)
        if inc_match:
            prefix = file_name[:inc_match.start()]
            new_file_name = prefix + "_v02" + ext
        else:
            new_file_name = file_name + "_v02" + ext
            
    new_scene_path = os.path.join(scene_dir, new_file_name).replace('\\', '/')
    
    # Xac nhan truoc khi nang
    res = cmds.confirmDialog(
        title="Xac nhan nang Version",
        message="Ban co muon nang version hien tai len phien ban moi khong?\nTen file moi:\n%s" % new_file_name,
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
            title="Thanh cong",
            message="Da nang version thanh cong!\nTen file moi: %s" % new_file_name,
            button=["OK"]
        )
        print("[AnimeowShelf] Da nang version thanh cong: %s" % new_file_name)
    except Exception as e:
        cmds.warning("Loi xay ra khi nang version: %s" % str(e))

def clean_folder():
    """Don dep thu muc: Giu lai 5 ban moi nhat, chuyen ban cu vao thu muc Old/"""
    scene_path = cmds.file(q=True, sceneName=True)
    if not scene_path:
        cmds.warning("Scene hien tai chua duoc luu tren dia! Hay luu file truoc khi thuc hien don dep.")
        return
        
    scene_dir, scene_file = os.path.split(scene_path)
    file_name, ext = os.path.splitext(scene_file)
    
    # Rut trich ten goc
    root_prefix = re.sub(r'([_\.]v\d+)?(\.\d{3,5})?(_org)?$', '', file_name, flags=re.IGNORECASE)
    
    try:
        files_in_dir = os.listdir(scene_dir)
    except Exception as e:
        cmds.warning("Khong the truy cap thu muc scene: %s" % str(e))
        return
        
    matched_files = []
    for f in files_in_dir:
        f_path = os.path.join(scene_dir, f).replace('\\', '/')
        if os.path.isfile(f_path) and f.lower().startswith(root_prefix.lower()) and f.lower().endswith(('.ma', '.mb')):
            mtime = os.path.getmtime(f_path)
            matched_files.append((f, f_path, mtime))
            
    if not matched_files:
        cmds.confirmDialog(title="Thong bao", message="Khong tim thay file nao khop trong thu muc de don dep!", button=["OK"])
        return
        
    matched_files.sort(key=lambda x: x[2], reverse=True)
    keep_filenames = [x[0] for x in matched_files[:5]]
    
    if scene_file not in keep_filenames:
        keep_filenames.append(scene_file)
        
    files_to_move = [x for x in matched_files if x[0] not in keep_filenames]
    
    if not files_to_move:
        cmds.confirmDialog(
            title="Thong bao",
            message="Thu muc hien tai dang rat sach se!\nChi co %d tep khop va toan bo da duoc giu lai (toi da 5 tep gan nhat)." % len(matched_files),
            button=["OK"]
        )
        return
        
    confirm_msg = "Ban co muon don dep thu muc nay khong?\n\n"
    confirm_msg += "- Giu lai %d tep moi nhat (bao gom file dang mo).\n" % len(keep_filenames)
    confirm_msg += "- Di chuyen %d tep cu hon vao thu muc 'Old'.\n\nDanh sach file se di chuyen:\n" % len(files_to_move)
    for f, _, _ in files_to_move[:10]:
        confirm_msg += "  + %s\n" % f
    if len(files_to_move) > 10:
        confirm_msg += "  + ... va %d file khac.\n" % (len(files_to_move) - 10)
        
    res = cmds.confirmDialog(
        title="Xac nhan don dep thu muc",
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
            cmds.warning("Khong the tao thu muc Old: %s" % str(e))
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
            
    msg = "Da don dep xong!\n- Di chuyen thanh cong: %d file vao thu muc 'Old'." % moved_count
    if errors:
        msg += "\n- Loi xay ra tren %d file:\n" % len(errors)
        msg += "\n".join(errors[:5])
        if len(errors) > 5:
            msg += "\n... va %d loi khac." % (len(errors) - 5)
            
    cmds.confirmDialog(title="Ket qua don dep", message=msg, button=["OK"])
    print("[AnimeowShelf] Clean folder hoan tat: di chuyen %d file." % moved_count)

def fix_lost_shader():
    """Mo khoa default shading group de sua loi mat shader (luoi xanh la)"""
    try:
        if cmds.objExists('initialShadingGroup'):
            cmds.lockNode('initialShadingGroup', lock=False, lockUnpublished=False)
        if cmds.objExists('defaultTextureList1'):
            cmds.lockNode('defaultTextureList1', lock=False, lockUnpublished=False)
        cmds.confirmDialog(
            title="Thanh cong",
            message="Da mo khoa cac node mac dinh thanh cong!\nBan co the thu gan lai shader hoac import/export binh thuong.",
            button=["OK"]
        )
    except Exception as e:
        cmds.warning("Khong the mo khoa cac node mac dinh: %s" % str(e))

# =========================================================================
# --- CAC HAM KHOI CHAY UNG DUNG PHU (LAUNCHERS CORES) ---
# =========================================================================

def launch_studiolibrary():
    """Khoi chay Studio Library nhanh tu Shelf"""
    ensure_scripts_2022_path()
    try:
        import studiolibrary
        window = getattr(studiolibrary, "_window", None)
        if window is not None:
            try:
                window.close()
                studiolibrary._window = None
                print("[StudioLibrary] Da dong Studio Library cu.")
                return
            except Exception:
                pass
        studiolibrary._window = None
        studiolibrary.main()
    except Exception as e:
        cmds.warning("Khong the chay Studio Library: %s" % str(e))

def launch_dwpicker():
    """Khoi chay DWPicker nhanh tu Shelf"""
    ensure_scripts_2022_path()
    try:
        import dwpicker
        from dwpicker.main import WINDOW_CONTROL_NAME
        if cmds.workspaceControl(WINDOW_CONTROL_NAME, exists=True):
            dwpicker.close()
            print("[DWPicker] Da dong DWPicker.")
        else:
            dwpicker.show()
    except Exception as e:
        cmds.warning("Khong the chay DWPicker: %s" % str(e))

def launch_tweenmachine():
    """Khoi chay Tween Machine nhanh tu Shelf"""
    path = ensure_scripts_2022_path()
    if not path:
        return
    tween_mel_path = os.path.join(path, "tweenMachine.mel").replace("\\", "/")
    if not os.path.exists(tween_mel_path):
        cmds.warning("Khong tim thay file tweenMachine.mel tai: %s" % tween_mel_path)
        return
        
    # Them thu muc chua tweenMachine vao MAYA_SCRIPT_PATH cua Maya
    try:
        current_script_path = os.environ.get("MAYA_SCRIPT_PATH", "")
        if path not in current_script_path:
            os.environ["MAYA_SCRIPT_PATH"] = path + os.pathsep + current_script_path
            # Dong bo lai voi Maya
            mel.eval("rehash;")
    except Exception:
        pass
        
    try:
        if cmds.window("tweenMachineWin", exists=True):
            cmds.deleteUI("tweenMachineWin")
            print("[TweenMachine] Da dong Tween Machine.")
        else:
            mel.eval('source "%s"; tweenMachine;' % tween_mel_path)
            print("[TweenMachine] Da mo Tween Machine.")
    except Exception as e:
        cmds.warning("Khong the chay Tween Machine: %s" % str(e))

def launch_atools():
    """Khoi chay aTools nhanh tu Shelf"""
    ensure_scripts_2022_path()
    try:
        from aTools.animTools.animBar import animBarUI
        animBarUI.show(mode="toggle")
    except Exception as e:
        try:
            import aTools.general.main as aToolsMain
            aToolsMain.show()
        except Exception as e2:
            cmds.warning("Khong the chay aTools: %s" % str(e))




def create_arc_trail():
    """Tao Arc Trail cho cac vat the dang chon (chay nhanh tu Shelf)"""
    sel = cmds.ls(sl=True) or []
    if not sel:
        cmds.warning("Vui long chon it nhat mot vat the de tao Arc Trail!")
        return
        
    start_frame = cmds.playbackOptions(q=True, minTime=True)
    end_frame = cmds.playbackOptions(q=True, maxTime=True)
    
    show_ticks = cmds.optionVar(query="animeow_at_show_ticks") if cmds.optionVar(exists="animeow_at_show_ticks") else True
    show_keys = cmds.optionVar(query="animeow_at_show_keys") if cmds.optionVar(exists="animeow_at_show_keys") else True
    tick_size = cmds.optionVar(query="animeow_at_tick_size") if cmds.optionVar(exists="animeow_at_tick_size") else 0.1
    
    show_ticks = bool(show_ticks)
    show_keys = bool(show_keys)
    tick_size = float(tick_size)
    
    pkg_name = __name__.split('.')[0]
    arc_tracker = __import__(pkg_name + ".core.arc_tracker", fromlist=["arc_tracker"])
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
        print("[AnimeowShelf] Da ve Arc Trail thanh cong cho %d vat the!" % len(sel))
    except Exception as e:
        cmds.warning("Loi ve Trail: %s" % str(e))
    finally:
        cmds.undoInfo(closeChunk=True)

# =========================================================================
# --- LOGIC TAO VA CAP NHAT SHELF ---
# =========================================================================

def create_shelf():
    """Tao hoac cap nhat Shelf 'Animeow' voi day du 20 nut cong cu nhanh"""
    shelf_name = "Animeow"
    
    # 1. Tim shelf tab layout cua Maya
    gShelfTopLevel = mel.eval("$tmpVar=$gShelfTopLevel")
    if not gShelfTopLevel:
        cmds.warning("Khong tim thay thanh Shelf cua Maya!")
        return
        
    # 2. Tao shelf neu chua co
    if not cmds.shelfLayout(shelf_name, exists=True):
        cmds.shelfLayout(shelf_name, parent=gShelfTopLevel)
        print("[AnimeowShelf] Da tao Shelf moi: %s" % shelf_name)
    else:
        # Neu da co, don dep cac nut cu truoc de cap nhat sach se
        children = cmds.shelfLayout(shelf_name, query=True, childArray=True) or []
        for child in children:
            try:
                cmds.deleteUI(child)
            except Exception:
                pass
        print("[AnimeowShelf] Da lam sach Shelf cu de cap nhat.")
        
    # 3. Tim thu muc icons va ham nap icon tuyet doi
    core_dir = os.path.dirname(os.path.abspath(__file__))
    package_dir = os.path.dirname(core_dir)
    parent_dir = os.path.dirname(package_dir).replace("\\", "/")
    icons_dir = os.path.join(package_dir, "icons")
    
    def get_icon(icon_name, fallback):
        full_path = os.path.join(icons_dir, icon_name)
        if os.path.exists(full_path):
            return full_path
        return fallback

    # Them code dinh nghia path chung cho moi nut
    common_path_init = "import sys\npath = '%s'\nif path not in sys.path: sys.path.insert(0, path)\n" % parent_dir
    package_name = os.path.basename(package_dir)

    # 4. Dinh nghia danh sach cac nut bam
    tools = [
        {
            "label": "ATB",
            "annotation": "Mo Animeow Toolboard day du",
            "image": get_icon("atb_icon.png", "fileOpen.png"),
            "command": common_path_init + "for m in list(sys.modules.keys()):\n    if m.startswith('{pkg}'):\n        del sys.modules[m]\nimport {pkg}\n{pkg}.show()".format(pkg=package_name)
        },
        {
            "label": "Link",
            "annotation": "Mo cua so Constraint & Smart Link doc lap",
            "image": get_icon("link_icon.png", "parentConstraint.png"),
            "command": common_path_init + "for m in list(sys.modules.keys()):\n    if m.startswith('{pkg}'):\n        del sys.modules[m]\nimport {pkg}\n{pkg}.show(standalone_tab='smart_link')".format(pkg=package_name)
        },
        {
            "label": "Bake",
            "annotation": "Mo cua so Smart World Bake & Pivot doc lap",
            "image": get_icon("bake_icon.png", "save.png"),
            "command": common_path_init + "for m in list(sys.modules.keys()):\n    if m.startswith('{pkg}'):\n        del sys.modules[m]\nimport {pkg}\n{pkg}.show(standalone_tab='world_bake')".format(pkg=package_name)
        },
        {
            "label": "FakeConst",
            "annotation": "Mo cua so Fake Constraint doc lap",
            "image": get_icon("fake_const_icon.png", "parentConstraint.png"),
            "command": common_path_init + "for m in list(sys.modules.keys()):\n    if m.startswith('{pkg}'):\n        del sys.modules[m]\nimport {pkg}\n{pkg}.show(standalone_tab='fake_constraint')".format(pkg=package_name)
        },
        {
            "label": "Curve",
            "annotation": "Mo cua so Curve & Motion doc lap",
            "image": get_icon("curve_icon.png", "menuIconWindow.png"),
            "command": common_path_init + "for m in list(sys.modules.keys()):\n    if m.startswith('{pkg}'):\n        del sys.modules[m]\nimport {pkg}\n{pkg}.show(standalone_tab=1)".format(pkg=package_name)
        },
        {
            "label": "Fav",
            "annotation": "Mo cua so cong cu yeu thich (Favorite Tools: Lam tron so & Don Key)",
            "image": get_icon("fav_icon.png", "menuIconWindow.png"),
            "command": common_path_init + "for m in list(sys.modules.keys()):\n    if m.startswith('{pkg}'):\n        del sys.modules[m]\nimport {pkg}\n{pkg}.show(standalone_tab='fav_tools')".format(pkg=package_name)
        },
        {
            "label": "Rig",
            "annotation": "Mo cua so Rig & Mirror doc lap",
            "image": get_icon("rig_icon.png", "polyMesh.png"),
            "command": common_path_init + "for m in list(sys.modules.keys()):\n    if m.startswith('{pkg}'):\n        del sys.modules[m]\nimport {pkg}\n{pkg}.show(standalone_tab=2)".format(pkg=package_name)
        },
        {
            "label": "Play",
            "annotation": "Mo cua so Output & Scene (Playblast) doc lap",
            "image": get_icon("play_icon.png", "playblast.png"),
            "command": common_path_init + "for m in list(sys.modules.keys()):\n    if m.startswith('{pkg}'):\n        del sys.modules[m]\nimport {pkg}\n{pkg}.show(standalone_tab=3)".format(pkg=package_name)
        },
        {
            "label": "Arc",
            "annotation": "Mo cua so cau hinh ve Arc Tracker doc lap",
            "image": get_icon("arc_icon.png", "motionTrail.png"),
            "command": common_path_init + "for m in list(sys.modules.keys()):\n    if m.startswith('{pkg}'):\n        del sys.modules[m]\nimport {pkg}\n{pkg}.show(standalone_tab='arc_tracker')".format(pkg=package_name)
        },
        {
            "label": "Overlap",
            "annotation": "Mo cua so Overlapper (Chuyen dong tre & Follow Through) doc lap",
            "image": get_icon("overlap_icon.png", "menuIconWindow.png"),
            "command": common_path_init + "for m in list(sys.modules.keys()):\n    if m.startswith('{pkg}'):\n        del sys.modules[m]\nimport {pkg}\n{pkg}.show(standalone_tab='overlapper')".format(pkg=package_name)
        },
        {
            "label": "Jitter",
            "annotation": "Mo hop cong cu khu rung Fix Jitter doc lap",
            "image": get_icon("jitter_icon.png", "commandButton.png"),
            "command": common_path_init + "for m in list(sys.modules.keys()):\n    if m.startswith('{pkg}'):\n        del sys.modules[m]\nimport {pkg}\n{pkg}.show(standalone_tab='fix_jitter')".format(pkg=package_name)
        },
        {
            "label": "Tr2Cr",
            "annotation": "Chuyen Motion Trail thanh Curve (Motion Trail to Curve)",
            "image": "motionTrail.png",
            "command": common_path_init + "import maya.mel as mel; import os; f=os.path.join('{parent}', '{pkg}', 'mel', 'motionTrailToCurve.mel').replace('\\\\','/'); mel.eval('source \"'+f+'\";'); mel.eval('motionTrailToCurve();')".format(parent=parent_dir, pkg=package_name)
        },
        {
            "label": "L.Scale",
            "annotation": "Mo hop cong cu Curve Local Scale (NP_curveLocalScale)",
            "image": "autoTangent.png",
            "command": common_path_init + "import maya.mel as mel; import os; f=os.path.join('{parent}', '{pkg}', 'mel', 'NP_curveLocalScale.mel').replace('\\\\','/'); mel.eval('source \"'+f+'\";')".format(parent=parent_dir, pkg=package_name)
        },
        {
            "label": "Hider",
            "annotation": "Khoi chay ANM Hider (An/Hien bo phan nhan vat)",
            "image": get_icon(os.path.join("Icons_Hider", "Hider_Icon.png"), "commandButton.png"),
            "command": common_path_init + "for m in list(sys.modules.keys()):\n    if m.startswith('{pkg}'):\n        del sys.modules[m]\nimport {pkg}.core.anm_hider as anm_hider\nanm_hider.show_hider()".format(pkg=package_name)
        },
        {
            "label": "Graph",
            "annotation": "Bat/Tat Graph Editor",
            "image": "menuIconWindow.png",
            "command": common_path_init + "import {pkg}.core.shelf as shelf; shelf.toggle_graph_editor()".format(pkg=package_name)
        },
        {
            "label": "Ref",
            "annotation": "Bat/Tat Reference Editor",
            "image": "fileOpen.png",
            "command": common_path_init + "import {pkg}.core.shelf as shelf; shelf.toggle_reference_editor()".format(pkg=package_name)
        },
        {
            "label": "Out",
            "annotation": "Bat/Tat Outliner Window",
            "image": "menuIconWindow.png",
            "command": common_path_init + "import {pkg}.core.shelf as shelf; shelf.toggle_outliner()".format(pkg=package_name)
        },
        {
            "label": "Const",
            "annotation": "Mo hop cong cu Quick Constraint doc lap",
            "image": "parentConstraint.png",
            "command": common_path_init + "for m in list(sys.modules.keys()):\n    if m.startswith('{pkg}'):\n        del sys.modules[m]\nimport {pkg}\n{pkg}.show(standalone_tab='quick_const')".format(pkg=package_name)
        },
        {
            "label": "Sets",
            "annotation": "Mo hop cong cu Selection Sets doc lap",
            "image": get_icon("sets_icon.png", "createSet.png"),
            "command": common_path_init + "for m in list(sys.modules.keys()):\n    if m.startswith('{pkg}'):\n        del sys.modules[m]\nimport {pkg}\n{pkg}.show(standalone_tab='selection_sets')".format(pkg=package_name)
        },
        {
            "label": "S.Inc",
            "annotation": "Luu Increment phien ban phu",
            "image": "save.png",
            "command": common_path_init + "import {pkg}.core.shelf as shelf; shelf.save_increment()".format(pkg=package_name)
        },
        {
            "label": "S.Up",
            "annotation": "Luu nang Version chinh",
            "image": "save.png",
            "command": common_path_init + "import {pkg}.core.shelf as shelf; shelf.save_up_version()".format(pkg=package_name)
        },
        {
            "label": "FixSh",
            "annotation": "Sua loi xanh luoi (Fix Lost Shader)",
            "image": "polyMesh.png",
            "command": common_path_init + "import {pkg}.core.shelf as shelf; shelf.fix_lost_shader()".format(pkg=package_name)
        },
        {
            "label": "Clean",
            "annotation": "Don dep scenes cu vao thu muc Old",
            "image": "delete.png",
            "command": common_path_init + "import {pkg}.core.shelf as shelf; shelf.clean_folder()".format(pkg=package_name)
        },
        {
            "label": "AntiV",
            "annotation": "Quet va diet Virus trong Scene (vaccine, gene, fuckvirus...)",
            "image": "delete.png",
            "command": common_path_init + "import {pkg}.core.shelf as shelf; shelf.run_anti_virus()".format(pkg=package_name)
        },
        {
            "label": "Studio",
            "annotation": "Khoi chay Studio Library",
            "image": "fileOpen.png",
            "command": common_path_init + "import {pkg}.core.shelf as shelf; shelf.launch_studiolibrary()".format(pkg=package_name)
        },
        {
            "label": "DWP",
            "annotation": "Khoi chay DWPicker",
            "image": "menuIconWindow.png",
            "command": common_path_init + "import {pkg}.core.shelf as shelf; shelf.launch_dwpicker()".format(pkg=package_name)
        },
        {
            "label": "Tween",
            "annotation": "Khoi chay Tween Machine",
            "image": "commandButton.png",
            "command": common_path_init + "import {pkg}.core.shelf as shelf; shelf.launch_tweenmachine()".format(pkg=package_name)
        },
        {
            "label": "aTools",
            "annotation": "Khoi chay aTools Anim School",
            "image": "commandButton.png",
            "command": common_path_init + "import {pkg}.core.shelf as shelf; shelf.launch_atools()".format(pkg=package_name)
        }
    ]
    
    # 4. Them tung nut vao Shelf
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
        
    # 5. Luu lai thiet lap shelf cua Maya
    try:
        mel.eval("saveAllShelves $gShelfTopLevel")
    except Exception:
        pass
    
    # 6. Hien thi thong bao
    cmds.confirmDialog(
        title=u"Thanh cong",
        message=u"Da tao/cap nhat thanh cong Shelf 'Animeow' voi day du %d nut cong cu nhanh!" % len(tools),
        button=[u"Tuyet voi"]
    )

