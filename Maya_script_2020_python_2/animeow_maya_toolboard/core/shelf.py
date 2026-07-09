# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import os
import sys
import re
import shutil
import maya.cmds as cmds
import maya.mel as mel

def ensure_scripts_2022_path():
    """Tự động kiểm tra và thêm thư mục chứa plugin bổ trợ vào sys.path"""
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
    return path

# =========================================================================
# --- CÁC HÀM TIỆN ÍCH QUẢN LÝ CẢNH (SCENE UTILITIES) ---
# =========================================================================

def toggle_graph_editor():
    """Bật/Tắt Graph Editor"""
    if cmds.window("graphEditor1Window", exists=True):
        cmds.deleteUI("graphEditor1Window", window=True)
        print("[AnimeowShelf] Đã đóng Graph Editor.")
    else:
        mel.eval("GraphEditor;")
        print("[AnimeowShelf] Đã mở Graph Editor.")

def toggle_reference_editor():
    """Bật/Tắt Reference Editor"""
    if cmds.window("referenceEditorPanel1Window", exists=True):
        cmds.deleteUI("referenceEditorPanel1Window", window=True)
        print("[AnimeowShelf] Đã đóng Reference Editor.")
    else:
        mel.eval("ReferenceEditor;")
        print("[AnimeowShelf] Đã mở Reference Editor.")

def save_increment():
    """Lưu increment phụ dạng .0001, .0002..."""
    mel.eval("IncrementAndSave;")
    print("[AnimeowShelf] Đã thực hiện Save Increment.")

def save_up_version():
    """Lưu nâng version chính (_v01 -> _v02)"""
    scene_path = cmds.file(q=True, sceneName=True)
    if not scene_path:
        cmds.warning("Scene chưa được lưu! Hãy lưu file trước khi nâng Version.")
        return
        
    scene_dir, scene_file = os.path.split(scene_path)
    file_name, ext = os.path.splitext(scene_file)
    
    # Regex tìm version _v01, _v02,... hoặc .v01, .v02...
    version_pattern = re.compile(r'([_\.]v)(\d+)(.*)', re.IGNORECASE)
    match = version_pattern.search(file_name)
    if match:
        prefix = file_name[:match.start()]
        v_prefix = match.group(1) # '_v' hoặc '.v'
        v_num_str = match.group(2) # '01', '1', '001'
        new_v_num = int(v_num_str) + 1
        new_v_num_str = str(new_v_num).zfill(len(v_num_str))
        new_file_name = prefix + v_prefix + new_v_num_str + ext
    else:
        # Nếu không có _vXX nhưng có hậu tố increment (.0005)
        inc_pattern = re.compile(r'\.(\d{3,5})$')
        inc_match = inc_pattern.search(file_name)
        if inc_match:
            prefix = file_name[:inc_match.start()]
            new_file_name = prefix + "_v02" + ext
        else:
            new_file_name = file_name + "_v02" + ext
            
    new_scene_path = os.path.join(scene_dir, new_file_name).replace('\\', '/')
    
    # Xác nhận trước khi nâng
    res = cmds.confirmDialog(
        title="Xác nhận nâng Version",
        message="Bạn có muốn nâng version hiện tại lên phiên bản mới không?\nTên file mới:\n%s" % new_file_name,
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
            title="Thành công",
            message="Đã nâng version thành công!\nTên file mới: %s" % new_file_name,
            button=["OK"]
        )
        print("[AnimeowShelf] Đã nâng version thành công: %s" % new_file_name)
    except Exception as e:
        cmds.warning("Lỗi xảy ra khi nâng version: %s" % str(e))

def clean_folder():
    """Dọn dẹp thư mục: Giữ lại 5 bản mới nhất, chuyển bản cũ vào thư mục Old/"""
    scene_path = cmds.file(q=True, sceneName=True)
    if not scene_path:
        cmds.warning("Scene hiện tại chưa được lưu trên đĩa! Hãy lưu file trước khi thực hiện dọn dẹp.")
        return
        
    scene_dir, scene_file = os.path.split(scene_path)
    file_name, ext = os.path.splitext(scene_file)
    
    # Rút trích tên gốc
    root_prefix = re.sub(r'([_\.]v\d+)?(\.\d{3,5})?(_org)?$', '', file_name, flags=re.IGNORECASE)
    
    try:
        files_in_dir = os.listdir(scene_dir)
    except Exception as e:
        cmds.warning("Không thể truy cập thư mục scene: %s" % str(e))
        return
        
    matched_files = []
    for f in files_in_dir:
        f_path = os.path.join(scene_dir, f).replace('\\', '/')
        if os.path.isfile(f_path) and f.lower().startswith(root_prefix.lower()) and f.lower().endswith(('.ma', '.mb')):
            mtime = os.path.getmtime(f_path)
            matched_files.append((f, f_path, mtime))
            
    if not matched_files:
        cmds.confirmDialog(title="Thông báo", message="Không tìm thấy file nào khớp trong thư mục để dọn dẹp!", button=["OK"])
        return
        
    matched_files.sort(key=lambda x: x[2], reverse=True)
    keep_filenames = [x[0] for x in matched_files[:5]]
    
    if scene_file not in keep_filenames:
        keep_filenames.append(scene_file)
        
    files_to_move = [x for x in matched_files if x[0] not in keep_filenames]
    
    if not files_to_move:
        cmds.confirmDialog(
            title="Thông báo",
            message="Thư mục hiện tại đang rất sạch sẽ!\nChỉ có %d tệp khớp và toàn bộ đã được giữ lại (tối đa 5 tệp gần nhất)." % len(matched_files),
            button=["OK"]
        )
        return
        
    confirm_msg = "Bạn có muốn dọn dẹp thư mục này không?\n\n"
    confirm_msg += "- Giữ lại %d tệp mới nhất (bao gồm file đang mở).\n" % len(keep_filenames)
    confirm_msg += "- Di chuyển %d tệp cũ hơn vào thư mục 'Old'.\n\nDanh sách file sẽ di chuyển:\n" % len(files_to_move)
    for f, _, _ in files_to_move[:10]:
        confirm_msg += "  + %s\n" % f
    if len(files_to_move) > 10:
        confirm_msg += "  + ... và %d file khác.\n" % (len(files_to_move) - 10)
        
    res = cmds.confirmDialog(
        title="Xác nhận dọn dẹp thư mục",
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
            cmds.warning("Không thể tạo thư mục Old: %s" % str(e))
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
            
    msg = "Đã dọn dẹp xong!\n- Di chuyển thành công: %d file vào thư mục 'Old'." % moved_count
    if errors:
        msg += "\n- Lỗi xảy ra trên %d file:\n" % len(errors)
        msg += "\n".join(errors[:5])
        if len(errors) > 5:
            msg += "\n... và %d lỗi khác." % (len(errors) - 5)
            
    cmds.confirmDialog(title="Kết quả dọn dẹp", message=msg, button=["OK"])
    print("[AnimeowShelf] Clean folder hoàn tất: di chuyển %d file." % moved_count)

def fix_lost_shader():
    """Mở khóa default shading group để sửa lỗi mất shader (lưới xanh lá)"""
    try:
        if cmds.objExists('initialShadingGroup'):
            cmds.lockNode('initialShadingGroup', lock=False, lockUnpublished=False)
        if cmds.objExists('defaultTextureList1'):
            cmds.lockNode('defaultTextureList1', lock=False, lockUnpublished=False)
        cmds.confirmDialog(
            title="Thành công",
            message="Đã mở khóa các node mặc định thành công!\nBạn có thể thử gán lại shader hoặc import/export bình thường.",
            button=["OK"]
        )
    except Exception as e:
        cmds.warning("Không thể mở khóa các node mặc định: %s" % str(e))

# =========================================================================
# --- CÁC HÀM KHỞI CHẠY ỨNG DỤNG PHỤ (LAUNCHERS CORES) ---
# =========================================================================

def launch_studiolibrary():
    """Khởi chạy Studio Library nhanh từ Shelf"""
    ensure_scripts_2022_path()
    try:
        import studiolibrary
        window = getattr(studiolibrary, "_window", None)
        if window is not None:
            try:
                window.close()
                studiolibrary._window = None
                print("[StudioLibrary] Đã đóng Studio Library cũ.")
                return
            except Exception:
                pass
        studiolibrary._window = None
        studiolibrary.main()
    except Exception as e:
        cmds.warning("Không thể chạy Studio Library: %s" % str(e))

def launch_dwpicker():
    """Khởi chạy DWPicker nhanh từ Shelf"""
    ensure_scripts_2022_path()
    try:
        import dwpicker
        from dwpicker.main import WINDOW_CONTROL_NAME
        if cmds.workspaceControl(WINDOW_CONTROL_NAME, exists=True):
            dwpicker.close()
            print("[DWPicker] Đã đóng DWPicker.")
        else:
            dwpicker.show()
    except Exception as e:
        cmds.warning("Không thể chạy DWPicker: %s" % str(e))

def launch_tweenmachine():
    """Khởi chạy Tween Machine nhanh từ Shelf"""
    path = ensure_scripts_2022_path()
    if not path:
        return
    tween_mel_path = os.path.join(path, "tweenMachine.mel").replace("\\", "/")
    if not os.path.exists(tween_mel_path):
        cmds.warning("Không tìm thấy file tweenMachine.mel tại: %s" % tween_mel_path)
        return
        
    # Thêm thư mục chứa tweenMachine vào MAYA_SCRIPT_PATH của Maya
    try:
        current_script_path = os.environ.get("MAYA_SCRIPT_PATH", "")
        if path not in current_script_path:
            os.environ["MAYA_SCRIPT_PATH"] = path + os.pathsep + current_script_path
            # Đồng bộ lại với Maya
            mel.eval("rehash;")
    except Exception:
        pass
        
    try:
        if cmds.window("tweenMachineWin", exists=True):
            cmds.deleteUI("tweenMachineWin")
            print("[TweenMachine] Đã đóng Tween Machine.")
        else:
            mel.eval('source "%s"; tweenMachine;' % tween_mel_path)
            print("[TweenMachine] Đã mở Tween Machine.")
    except Exception as e:
        cmds.warning("Không thể chạy Tween Machine: %s" % str(e))

def launch_atools():
    """Khởi chạy aTools nhanh từ Shelf"""
    ensure_scripts_2022_path()
    try:
        from aTools.animTools.animBar import animBarUI
        animBarUI.show(mode="toggle")
    except Exception as e:
        try:
            import aTools.general.main as aToolsMain
            aToolsMain.show()
        except Exception as e2:
            cmds.warning("Không thể chạy aTools: %s" % str(e))

def launch_animo():
    """Khởi chạy Animo nhanh từ Shelf"""
    thirdparty_dir = ensure_scripts_2022_path()
    if not thirdparty_dir:
        return
        
    animo_data_path = os.path.join(thirdparty_dir, "Animo_v5.9.6", "Animo_v5.9.6", "Animo_Data")
    if not os.path.exists(animo_data_path):
        cmds.warning("Không tìm thấy thư mục Animo_Data tại: %s" % animo_data_path)
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
        print("[Animo] Đã đóng Animo.")
    else:
        if cmds.workspaceControl('animo', exists=True):
            cmds.deleteUI('animo', control=True)
        if existing_qt_toolbar:
            try:
                existing_qt_toolbar.show()
                print("[Animo] Đã bật lại animo_qt_toolbar.")
                return
            except Exception:
                pass
                
        # Xoá cache sys.modules
        mods_to_delete = [mod for mod in list(sys.modules.keys()) 
                          if 'Animo' in mod or 'animo' in mod or 'styleMod' in mod or 'barMod' in mod]
        for mod in mods_to_delete:
            del sys.modules[mod]
            
        # Thêm các đường dẫn nạp vào sys.path
        animo_launcher_dir = os.path.join(animo_data_path, "Animo_Launcher")
        for p in [animo_data_path, animo_launcher_dir]:
            if p not in sys.path:
                sys.path.insert(0, p)
                
        # Load và thực thi khởi động UI Animo
        try:
            import importlib.util
            launcher_file = os.path.join(animo_launcher_dir, "Animo_Launcher.py")
            spec = importlib.util.spec_from_file_location("Animo_Launcher_Module", launcher_file)
            launcher_module = importlib.util.module_from_spec(spec)
            sys.modules["Animo_Launcher_Module"] = launcher_module
            spec.loader.exec_module(launcher_module)
            _tb = launcher_module.toolbar()
            _tb.startUI()
            print("[Animo] Đã khởi chạy Animo thành công.")
        except Exception as e:
            cmds.warning("Lỗi khởi chạy Animo: %s" % str(e))


def create_arc_trail():
    """Tạo Arc Trail cho các vật thể đang chọn (chạy nhanh từ Shelf)"""
    sel = cmds.ls(sl=True) or []
    if not sel:
        cmds.warning("Vui lòng chọn ít nhất một vật thể để tạo Arc Trail!")
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
        print("[AnimeowShelf] Đã vẽ Arc Trail thành công cho %d vật thể!" % len(sel))
    except Exception as e:
        cmds.warning("Lỗi vẽ Trail: %s" % str(e))
    finally:
        cmds.undoInfo(closeChunk=True)

# =========================================================================
# --- LOGIC TẠO VÀ CẬP NHẬT SHELF ---
# =========================================================================

def create_shelf():
    """Tạo hoặc cập nhật Shelf 'Animeow' với đầy đủ 18 nút công cụ nhanh"""
    shelf_name = "Animeow"
    
    # 1. Tìm shelf tab layout của Maya
    gShelfTopLevel = mel.eval("$tmpVar=$gShelfTopLevel")
    if not gShelfTopLevel:
        cmds.warning("Không tìm thấy thanh Shelf của Maya!")
        return
        
    # 2. Tạo shelf nếu chưa có
    if not cmds.shelfLayout(shelf_name, exists=True):
        cmds.shelfLayout(shelf_name, parent=gShelfTopLevel)
        print("[AnimeowShelf] Đã tạo Shelf mới: %s" % shelf_name)
    else:
        # Nếu đã có, dọn dẹp các nút cũ trước để cập nhật sạch sẽ
        children = cmds.shelfLayout(shelf_name, query=True, childArray=True) or []
        for child in children:
            try:
                cmds.deleteUI(child)
            except Exception:
                pass
        print("[AnimeowShelf] Đã làm sạch Shelf cũ để cập nhật.")
        
    # 3. Tìm thư mục icons và hàm nạp icon tuyệt đối
    core_dir = os.path.dirname(os.path.abspath(__file__))
    package_dir = os.path.dirname(core_dir)
    icons_dir = os.path.join(package_dir, "icons")
    
    def get_icon(icon_name, fallback):
        full_path = os.path.join(icons_dir, icon_name)
        if os.path.exists(full_path):
            return full_path
        return fallback

    # 4. Định nghĩa danh sách các nút bấm
    tools = [
        {
            "label": "ATB",
            "annotation": "Mở Animeow Toolboard đầy đủ",
            "image": get_icon("atb_icon.png", "fileOpen.png"),
            "command": "import sys\nfor m in list(sys.modules.keys()):\n    if m.startswith('animeow_maya_toolboard'):\n        del sys.modules[m]\nimport animeow_maya_toolboard\nanimeow_maya_toolboard.show()"
        },
        {
            "label": "Bake",
            "annotation": "Mở cửa sổ Space & Bake độc lập",
            "image": get_icon("bake_icon.png", "save.png"),
            "command": "import sys\nfor m in list(sys.modules.keys()):\n    if m.startswith('animeow_maya_toolboard'):\n        del sys.modules[m]\nimport animeow_maya_toolboard\nanimeow_maya_toolboard.show(standalone_tab=0)"
        },
        {
            "label": "Curve",
            "annotation": "Mở cửa sổ Curve & Motion độc lập",
            "image": get_icon("curve_icon.png", "menuIconWindow.png"),
            "command": "import sys\nfor m in list(sys.modules.keys()):\n    if m.startswith('animeow_maya_toolboard'):\n        del sys.modules[m]\nimport animeow_maya_toolboard\nanimeow_maya_toolboard.show(standalone_tab=1)"
        },
        {
            "label": "Rnd",
            "annotation": "Mở cửa sổ Làm tròn số độc lập",
            "image": get_icon("rnd_icon.png", "menuIconWindow.png"),
            "command": "import sys\nfor m in list(sys.modules.keys()):\n    if m.startswith('animeow_maya_toolboard'):\n        del sys.modules[m]\nimport animeow_maya_toolboard\nanimeow_maya_toolboard.show(standalone_tab='round_tool')"
        },
        {
            "label": "Rig",
            "annotation": "Mở cửa sổ Rig & Mirror độc lập",
            "image": get_icon("rig_icon.png", "polyMesh.png"),
            "command": "import sys\nfor m in list(sys.modules.keys()):\n    if m.startswith('animeow_maya_toolboard'):\n        del sys.modules[m]\nimport animeow_maya_toolboard\nanimeow_maya_toolboard.show(standalone_tab=2)"
        },
        {
            "label": "Play",
            "annotation": "Mở cửa sổ Output & Scene (Playblast) độc lập",
            "image": get_icon("play_icon.png", "playblast.png"),
            "command": "import sys\nfor m in list(sys.modules.keys()):\n    if m.startswith('animeow_maya_toolboard'):\n        del sys.modules[m]\nimport animeow_maya_toolboard\nanimeow_maya_toolboard.show(standalone_tab=3)"
        },
        {
            "label": "Arc",
            "annotation": "Mở cửa sổ cấu hình vẽ Arc Tracker độc lập",
            "image": get_icon("arc_icon.png", "motionTrail.png"),
            "command": "import sys\nfor m in list(sys.modules.keys()):\n    if m.startswith('animeow_maya_toolboard'):\n        del sys.modules[m]\nimport animeow_maya_toolboard\nanimeow_maya_toolboard.show(standalone_tab='arc_tracker')"
        },
        {
            "label": "Graph",
            "annotation": "Bật/Tắt Graph Editor",
            "image": "menuIconWindow.png",
            "command": "import animeow_maya_toolboard.core.shelf as shelf; shelf.toggle_graph_editor()"
        },
        {
            "label": "Ref",
            "annotation": "Bật/Tắt Reference Editor",
            "image": "fileOpen.png",
            "command": "import animeow_maya_toolboard.core.shelf as shelf; shelf.toggle_reference_editor()"
        },
        {
            "label": "S.Inc",
            "annotation": "Lưu Increment phiên bản phụ",
            "image": "save.png",
            "command": "import animeow_maya_toolboard.core.shelf as shelf; shelf.save_increment()"
        },
        {
            "label": "S.Up",
            "annotation": "Lưu nâng Version chính",
            "image": "save.png",
            "command": "import animeow_maya_toolboard.core.shelf as shelf; shelf.save_up_version()"
        },
        {
            "label": "FixSh",
            "annotation": "Sửa lỗi xanh lưới (Fix Lost Shader)",
            "image": "polyMesh.png",
            "command": "import animeow_maya_toolboard.core.shelf as shelf; shelf.fix_lost_shader()"
        },
        {
            "label": "Clean",
            "annotation": "Dọn dẹp scenes cũ vào thư mục Old",
            "image": "delete.png",
            "command": "import animeow_maya_toolboard.core.shelf as shelf; shelf.clean_folder()"
        },
        {
            "label": "Studio",
            "annotation": "Khởi chạy Studio Library",
            "image": "fileOpen.png",
            "command": "import animeow_maya_toolboard.core.shelf as shelf; shelf.launch_studiolibrary()"
        },
        {
            "label": "DWP",
            "annotation": "Khởi chạy DWPicker",
            "image": "menuIconWindow.png",
            "command": "import animeow_maya_toolboard.core.shelf as shelf; shelf.launch_dwpicker()"
        },
        {
            "label": "Tween",
            "annotation": "Khởi chạy Tween Machine",
            "image": "commandButton.png",
            "command": "import animeow_maya_toolboard.core.shelf as shelf; shelf.launch_tweenmachine()"
        },
        {
            "label": "aTools",
            "annotation": "Khởi chạy aTools Anim School",
            "image": "commandButton.png",
            "command": "import animeow_maya_toolboard.core.shelf as shelf; shelf.launch_atools()"
        },
        {
            "label": "Animo",
            "annotation": "Khởi chạy Animo Toolset",
            "image": "commandButton.png",
            "command": "import animeow_maya_toolboard.core.shelf as shelf; shelf.launch_animo()"
        }
    ]
    
    # 4. Thêm từng nút vào Shelf
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
        
    # 5. Lưu lại thiết lập shelf của Maya
    try:
        mel.eval("saveAllShelves")
    except Exception:
        pass
    
    # 6. Hiển thị thông báo
    cmds.confirmDialog(
        title="Thành công",
        message="Đã tạo/cập nhật thành công Shelf 'Animeow' với đầy đủ 18 nút công cụ nhanh!",
        button=["Tuyệt vời"]
    )
