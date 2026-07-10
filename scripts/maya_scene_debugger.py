# -*- coding: utf-8 -*-
import os
import sys
import time
import codecs

# Sửa lỗi LookupError: unknown encoding: cp65001 trong Python 2.7 trên Windows
try:
    codecs.register(lambda name: codecs.lookup('utf-8') if name == 'cp65001' else None)
except Exception:
    pass

def log(msg):
    # Decode to system output encoding to print correctly in Windows CMD
    try:
        if isinstance(msg, unicode):
            print("[DEBUG] " + msg.encode("utf-8"))
        else:
            print("[DEBUG] " + msg)
    except Exception:
        print("[DEBUG] " + msg)
    sys.stdout.flush()

def get_unicode_argv():
    try:
        import ctypes
        from ctypes import wintypes
        
        GetCommandLineW = ctypes.windll.kernel32.GetCommandLineW
        GetCommandLineW.restype = ctypes.c_wchar_p
        
        CommandLineToArgvW = ctypes.windll.shell32.CommandLineToArgvW
        CommandLineToArgvW.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_int)]
        CommandLineToArgvW.restype = ctypes.POINTER(ctypes.c_wchar_p)
        
        cmd = GetCommandLineW()
        argc = ctypes.c_int(0)
        argv = CommandLineToArgvW(cmd, ctypes.byref(argc))
        
        if argv:
            return [argv[i] for i in range(argc.value)]
    except Exception:
        pass
    return [unicode(arg) for arg in sys.argv]

import re

ref_pattern = re.compile(r'^\s*file\s+-r\s+.*"([^"]+\.m[ab])"\s*;', re.IGNORECASE)

def get_references_from_ma(filepath):
    refs = []
    try:
        fs_path = filepath
        if isinstance(filepath, unicode):
            try:
                fs_path = filepath.encode(sys.getfilesystemencoding())
            except Exception:
                fs_path = filepath.encode("utf-8")
            
        with open(fs_path, "rb") as f:
            for line in f:
                match = ref_pattern.match(line)
                if match:
                    ref_path = match.group(1).decode("utf-8", errors="replace")
                    ref_path = os.path.normpath(ref_path)
                    if ref_path not in refs:
                        refs.append(ref_path)
    except Exception as e:
        log("Loi khi quet reference tu file .ma: " + str(e))
    return refs

def main():
    argv = get_unicode_argv()
    
    # Tìm đối số thực sự là đường dẫn file Maya (.ma hoặc .mb)
    filepath = None
    for arg in argv[1:]:
        if arg.lower().endswith(".ma") or arg.lower().endswith(".mb"):
            filepath = arg
            break
            
    if not filepath:
        # Fallback nếu kéo thả không có đuôi chuẩn hoặc chạy trực tiếp
        if len(argv) > 1:
            filepath = argv[-1]
            
    if not filepath or not os.path.exists(filepath):
        print("Huong dan: Keo tha file .ma hoac .mb vao file .bat de debug.")
        if filepath:
            print("Loi: File khong ton tai: " + filepath.encode("utf-8"))
        return
        
    log(u"Khởi tạo Maya Standalone (Vui lòng chờ)...")
    try:
        # Khởi tạo QApplication để thiết lập đầy đủ môi trường Qt5Core cho Maya/V-Ray
        try:
            from PySide2 import QtWidgets
            app = QtWidgets.QApplication.instance()
            if not app:
                app = QtWidgets.QApplication([])
            log(u"-> Đã khởi tạo môi trường Qt thành công.")
        except Exception as qte:
            log(u"-> Cảnh báo khởi tạo Qt: " + unicode(qte))
            
        import maya.standalone
        maya.standalone.initialize(name="python")
    except Exception as e:
        print("Loi: Khong the khoi tao Maya Standalone: " + str(e))
        return
        
    import maya.cmds as cmds
    
    # 0. Quét trước danh sách reference từ file .ma bằng Python
    log(u"Bước 0: Quét nhanh danh sách references bằng Python...")
    ref_files = get_references_from_ma(filepath)
    log(u"-> Phát hiện %d references liên kết từ file cảnh." % len(ref_files))
    
    log(u"Đang phân tích file cảnh: " + filepath)
    
    # 1. Đo thời gian mở file gốc
    log(u"Bước 1: Mở file gốc (Bỏ qua hoàn toàn References để tránh crash)...")
    t0 = time.time()
    try:
        # Chuyển đổi đường dẫn hệ thống an toàn
        fs_path = filepath
        if isinstance(filepath, unicode):
            fs_path = filepath.encode(sys.getfilesystemencoding())
            
        cmds.file(fs_path, open=True, force=True, ignoreReference=True)
        base_time = time.time() - t0
        log(u"-> Mở file gốc thành công! Thời gian: %.2f giây" % base_time)
    except Exception as e:
        log(u"-> LỖI khi mở file gốc: " + str(e))
        return
        
    # 2. Liệt kê và load từng reference
    log(u"Bước 2: Nạp lần lượt từng reference...")
    
    ref_success_count = 0
    ref_failed_count = 0
    
    for i, ref_file in enumerate(ref_files, 1):
        try:
            ref_node = cmds.referenceQuery(ref_file, referenceNode=True)
        except Exception:
            ref_node = "UnknownNode"
            
        log(u"Nạp Reference [%d/%d]: %s (%s)..." % (i, len(ref_files), unicode(ref_node), os.path.basename(ref_file)))
        t_ref_start = time.time()
        try:
            # Chuyển đổi đường dẫn reference
            fs_ref = ref_file
            if isinstance(ref_file, unicode):
                fs_ref = ref_file.encode(sys.getfilesystemencoding())
                
            cmds.file(fs_ref, reference=True)
            ref_time = time.time() - t_ref_start
            ref_success_count += 1
            log(u"   -> THÀNH CÔNG! Thời gian nạp: %.2f giây" % ref_time)
        except Exception as ref_err:
            ref_time = time.time() - t_ref_start
            ref_failed_count += 1
            log(u"   -> LỖI NẠP: %s (Thời gian: %.2f giây)" % (str(ref_err), ref_time))
            
    # 3. Quét script nodes
    log(u"Bước 3: Quét danh sách các Script Nodes...")
    script_nodes = cmds.ls(type="script") or []
    log(u"-> Tìm thấy %d script nodes." % len(script_nodes))
    for node in script_nodes:
        try:
            script_type = cmds.getAttr(node + ".scriptType")
            script_val = cmds.getAttr(node + ".before") or ""
            if not script_val:
                script_val = cmds.getAttr(node + ".after") or ""
            
            # Rút gọn code preview hiển thị một dòng
            preview = script_val[:80].replace("\n", " ").replace("\r", "").strip()
            log(u"   - Node: %s (Type: %d) | Code preview: %s..." % (unicode(node), script_type, unicode(preview)))
        except Exception as se:
            log(u"   - Lỗi đọc node %s: %s" % (unicode(node), str(se)))
            
    # Tính toán kết quả
    total_time = time.time() - start_total
    print("\n")
    log(u"==================================================")
    log(u"          KẾT QUẢ CHẨN ĐOÁN CHI TIẾT (DONE)       ")
    log(u"==================================================")
    log(u"- Tổng thời gian mở cảnh: %.2f giây" % total_time)
    log(u"- Thời gian nạp file gốc: %.2f giây" % base_time)
    log(u"- Tổng số References: %d (Thành công: %d, Lỗi: %d)" % (len(ref_files), ref_success_count, ref_failed_count))
    log(u"- Số lượng Script Nodes: %d" % len(script_nodes))
    log(u"==================================================")
    
    # Dọn dẹp file tạm
    try:
        if os.path.exists(temp_ma_path) and temp_ma_path != filepath:
            os.remove(temp_ma_path)
    except Exception:
        pass

def run_from_batch():
    start_total = time.time()
    
    # Lấy filepath từ biến môi trường
    filepath = os.environ.get("MAYA_DEBUG_FILE")
    if not filepath:
        print("Loi: Khong tim thay bien moi truong MAYA_DEBUG_FILE.")
        return
        
    if isinstance(filepath, str):
        filepath = filepath.decode("utf-8")
        
    if not os.path.exists(filepath):
        print("Loi: File khong ton tai: " + filepath.encode("utf-8"))
        return
        
    import maya.cmds as cmds
    
    # 0. Quét trước danh sách reference từ file .ma bằng Python
    log(u"Bước 0: Quét nhanh danh sách references bằng Python...")
    ref_files = get_references_from_ma(filepath)
    log(u"-> Phát hiện %d references liên kết từ file cảnh." % len(ref_files))
    
    log(u"Đang phân tích file cảnh: " + filepath)
    
    # 1. Đo thời gian mở file gốc
    log(u"Bước 1: Mở file gốc (không nạp References)...")
    t0 = time.time()
    try:
        # Chuyển đổi đường dẫn hệ thống an toàn
        fs_path = filepath
        if isinstance(filepath, unicode):
            fs_path = filepath.encode(sys.getfilesystemencoding())
            
        cmds.file(fs_path, open=True, force=True, loadReferenceDepth="none")
        base_time = time.time() - t0
        log(u"-> Mở file gốc thành công! Thời gian: %.2f giây" % base_time)
    except Exception as e:
        log(u"-> LỖI khi mở file gốc: " + str(e))
        return
        
    # 2. Liệt kê và load từng reference
    log(u"Bước 2: Nạp lần lượt từng reference...")
    
    ref_success_count = 0
    ref_failed_count = 0
    
    # Lấy danh sách reference nodes thực tế từ scene đã mở
    scene_ref_files = cmds.file(q=True, reference=True) or []
    
    for i, ref_file in enumerate(scene_ref_files, 1):
        try:
            ref_node = cmds.referenceQuery(ref_file, referenceNode=True)
        except Exception:
            ref_node = "UnknownNode"
            
        log(u"Nạp Reference [%d/%d]: %s (%s)..." % (i, len(scene_ref_files), unicode(ref_node), os.path.basename(ref_file)))
        t_ref_start = time.time()
        try:
            fs_ref = ref_file
            if isinstance(ref_file, unicode):
                fs_ref = ref_file.encode(sys.getfilesystemencoding())
                
            cmds.file(fs_ref, loadReference=True)
            ref_time = time.time() - t_ref_start
            ref_success_count += 1
            log(u"   -> THÀNH CÔNG! Thời gian nạp: %.2f giây" % ref_time)
        except Exception as ref_err:
            ref_time = time.time() - t_ref_start
            ref_failed_count += 1
            log(u"   -> LỖI NẠP: %s (Thời gian: %.2f giây)" % (str(ref_err), ref_time))
            
    # 3. Quét script nodes
    log(u"Bước 3: Quét danh sách các Script Nodes...")
    script_nodes = cmds.ls(type="script") or []
    log(u"-> Tìm thấy %d script nodes." % len(script_nodes))
    for node in script_nodes:
        try:
            script_type = cmds.getAttr(node + ".scriptType")
            script_val = cmds.getAttr(node + ".before") or ""
            if not script_val:
                script_val = cmds.getAttr(node + ".after") or ""
            
            # Rút gọn code preview hiển thị một dòng
            preview = script_val[:80].replace("\n", " ").replace("\r", "").strip()
            log(u"   - Node: %s (Type: %d) | Code preview: %s..." % (unicode(node), script_type, unicode(preview)))
        except Exception as se:
            log(u"   - Lỗi đọc node %s: %s" % (unicode(node), str(se)))
            
    # Tính toán kết quả
    total_time = time.time() - start_total
    print("\n")
    log(u"==================================================")
    log(u"          KẾT QUẢ CHẨN ĐOÁN CHI TIẾT (DONE)       ")
    log(u"==================================================")
    log(u"- Tổng thời gian mở cảnh: %.2f giây" % total_time)
    log(u"- Thời gian nạp file gốc: %.2f giây" % base_time)
    log(u"- Tổng số References: %d (Thành công: %d, Lỗi: %d)" % (len(scene_ref_files), ref_success_count, ref_failed_count))
    log(u"- Số lượng Script Nodes: %d" % len(script_nodes))
    log(u"==================================================")

if __name__ == "__main__":
    main()
