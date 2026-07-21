from __future__ import print_function, division, absolute_import

import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma
import os
import json
import copy
import time

try:
    from PySide6.QtCore import QTimer
except ImportError:
    from PySide2.QtCore import QTimer


_prefs_path = None
_offsets_cache = None
_cache_valid = False

PIVOT_NULL = "Animo_Pivot"
PIVOT_SET = "Animo_Pivot_objects"


def get_prefs_path():
    global _prefs_path
    if _prefs_path:
        return _prefs_path
    
    if os.name == 'nt':
        docs = os.path.join(os.environ['USERPROFILE'], "Documents", "maya", "scripts", "Animo_Data", "Animo_Prefs")
    else:
        docs = os.path.join(os.path.expanduser("~"), "Documents", "maya", "scripts", "Animo_Data", "Animo_Prefs")
    if not os.path.exists(docs):
        os.makedirs(docs)
    _prefs_path = os.path.join(docs, "temp_pivot.json")
    return _prefs_path


def load_offsets():
    global _offsets_cache, _cache_valid
    if _cache_valid and _offsets_cache is not None:
        return _offsets_cache
    
    path = get_prefs_path()
    if os.path.exists(path):
        with open(path, "r") as f:
            _offsets_cache = json.load(f)
    else:
        _offsets_cache = {"single_offsets": {}, "multi_offsets": [], "last_selection": []}
    
    if "last_selection" not in _offsets_cache:
        _offsets_cache["last_selection"] = []
    
    _cache_valid = True
    return _offsets_cache


def save_offsets(data):
    global _offsets_cache, _cache_valid
    path = get_prefs_path()
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    _offsets_cache = data
    _cache_valid = True


def get_mobject(name):
    sel = om.MSelectionList()
    try:
        sel.add(name)
        return sel.getDependNode(0)
    except:
        return None


def obj_exists(name):
    sel = om.MSelectionList()
    try:
        sel.add(name)
        return True
    except:
        return False


def get_current_time():
    return oma.MAnimControl.currentTime().value


def set_current_time(frame):
    oma.MAnimControl.setCurrentTime(om.MTime(frame, om.MTime.uiUnit()))


def set_selection(names):
    sel = om.MSelectionList()
    for name in names:
        try:
            sel.add(name)
        except:
            pass
    om.MGlobal.setActiveSelectionList(sel)


def has_keyframes(name, attrs):
    if not obj_exists(name):
        return False
    for attr in attrs:
        try:
            keys = cmds.keyframe(name + '.' + attr, q=True, keyframeCount=True) or 0
            if keys > 0:
                return True
        except:
            pass
    return False


def get_all_keyframes(name, attrs):
    keyframes = set()
    if not obj_exists(name):
        return []
    for attr in attrs:
        try:
            keys = cmds.keyframe(name + '.' + attr, q=True, timeChange=True)
            if keys:
                keyframes.update(keys)
        except:
            pass
    return sorted(keyframes)


def get_key_count(name, attrs):
    """Get total number of keyframes across all attributes"""
    count = 0
    if not obj_exists(name):
        return 0
    for attr in attrs:
        try:
            keys = cmds.keyframe(name + '.' + attr, q=True, keyframeCount=True) or 0
            count += keys
        except:
            pass
    return count


def has_key_at_time(name, attrs, time):
    """Check if object has a keyframe at specified time on any of the attrs"""
    if not obj_exists(name):
        return False
    for attr in attrs:
        try:
            keys = cmds.keyframe(name + '.' + attr, q=True, time=(time, time), keyframeCount=True) or 0
            if keys > 0:
                return True
        except:
            pass
    return False


def remove_keys_at_time(name, attrs, time):
    """Remove keyframes at specified time on all attrs"""
    if not obj_exists(name):
        return
    for attr in attrs:
        try:
            cmds.cutKey(name, attribute=attr, time=(time, time))
        except:
            pass


def is_attr_locked(name, attr):
    obj = get_mobject(name)
    if not obj:
        return True
    fn = om.MFnDependencyNode(obj)
    try:
        plug = fn.findPlug(attr, False)
        return plug.isLocked
    except:
        return True


class LiveTempPivot:
    
    def __init__(self):
        self.sel = []
        self.original_matrices = {}
        self.original_frame = None
        self.time_job = None
        self.selection_job = None
        self.locked_attrs = {}
        self.relationship_data = {}
        self.original_relationship_data = {}
        self.timer = None
        self.last_pivot_matrix = None
        self.pivot_to_ref_offset = None
        self.ref_obj = None
        self.objects_had_keys = False
        self.keys_set_this_session = False
        self.is_time_changing = False
        self.last_pivot_key_count = 0
        self.skip_next_update = False
        self.last_change_time = 0
        self.pending_reapply = False
        self.reapply_delay = 0.3
        self.time_change_cooldown = 0
        self.cooldown_duration = 0.1
        self.awaiting_real_manipulation = False
        self.original_timeline_connection = None
    
    def cleanup_setup(self):
        self.stop_timer()
        self.restore_timeline_connection()
        
        try:
            if obj_exists(PIVOT_NULL):
                cmds.delete(PIVOT_NULL)
        except:
            pass
            
        try:
            if obj_exists(PIVOT_SET):
                cmds.delete(PIVOT_SET)
        except:
            pass
        
        try:
            if self.time_job and cmds.scriptJob(exists=self.time_job):
                cmds.scriptJob(kill=self.time_job)
        except:
            pass
        self.time_job = None
        
        try:
            if self.selection_job and cmds.scriptJob(exists=self.selection_job):
                cmds.scriptJob(kill=self.selection_job)
        except:
            pass
        self.selection_job = None
        
        self.original_matrices = {}
        self.original_frame = None
        self.locked_attrs = {}
        self.relationship_data = {}
        self.original_relationship_data = {}
        self.last_pivot_matrix = None
        self.pivot_to_ref_offset = None
        self.ref_obj = None
        self.objects_had_keys = False
        self.keys_set_this_session = False
        self.is_time_changing = False
        self.last_pivot_key_count = 0
        self.skip_next_update = False
        self.last_change_time = 0
        self.pending_reapply = False
        self.time_change_cooldown = 0
        self.awaiting_real_manipulation = False
    
    def start_timer(self):
        self.stop_timer()
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer_tick)
        self.timer.start(16)
    
    def stop_timer(self):
        if self.timer:
            self.timer.stop()
            self.timer.deleteLater()
            self.timer = None
    
    def setup_timeline_connection(self):
        """Make timeline show object keys instead of pivot keys"""
        try:
            import maya.mel as mel
            
            # Get the main timeline using MEL
            time_control = mel.eval('$tmpVar=$gPlayBackSlider')
            
            if not time_control or not cmds.timeControl(time_control, exists=True):
                return
            
            # Store original connection
            self.original_timeline_connection = cmds.timeControl(
                time_control, q=True, mainListConnection=True
            )
            
            # Create a selection connection for our objects
            conn_name = "tempPivotKeysConnection"
            if cmds.selectionConnection(conn_name, exists=True):
                cmds.deleteUI(conn_name)
            
            cmds.selectionConnection(conn_name)
            
            # Add all objects to the connection
            for obj in self.sel:
                if obj_exists(obj):
                    cmds.selectionConnection(conn_name, e=True, object=obj)
            
            # Connect to timeline
            cmds.timeControl(time_control, e=True, mainListConnection=conn_name)
            
        except Exception as e:
            cmds.warning("Timeline connection setup failed: {}".format(str(e)))
    
    def restore_timeline_connection(self):
        """Restore timeline to normal selection-based display"""
        try:
            import maya.mel as mel
            
            # Get the main timeline using MEL
            time_control = mel.eval('$tmpVar=$gPlayBackSlider')
            
            if not time_control or not cmds.timeControl(time_control, exists=True):
                return
            
            # Restore original connection if we have it
            if self.original_timeline_connection:
                cmds.timeControl(time_control, e=True, 
                                mainListConnection=self.original_timeline_connection)
            
            # Delete our custom connection
            if cmds.selectionConnection("tempPivotKeysConnection", exists=True):
                cmds.deleteUI("tempPivotKeysConnection")
            
            self.original_timeline_connection = None
        except:
            pass
    
    def matrices_equal(self, m1, m2, tolerance=0.0001):
        """Compare two matrices with tolerance for floating point errors"""
        if m1 is None or m2 is None:
            return False
        for i in range(16):
            if abs(m1[i] - m2[i]) > tolerance:
                return False
        return True
    
    def matrix_moved_significantly(self, m1, m2, threshold=0.01):
        """Check if matrix moved enough to be considered intentional manipulation"""
        if m1 is None or m2 is None:
            return False
        # Check translation (indices 12, 13, 14 in row-major 4x4)
        tx_diff = abs(m1[12] - m2[12])
        ty_diff = abs(m1[13] - m2[13])
        tz_diff = abs(m1[14] - m2[14])
        if tx_diff > threshold or ty_diff > threshold or tz_diff > threshold:
            return True
        # Check rotation by comparing first 3 columns of rotation matrix
        rot_threshold = 0.005
        for i in range(12):  # First 12 elements contain rotation/scale
            if abs(m1[i] - m2[i]) > rot_threshold:
                return True
        return False
    
    def on_timer_tick(self):
        if not obj_exists(PIVOT_NULL):
            self.stop_timer()
            return
        
        if self.is_time_changing:
            return
        
        current_time_now = time.time()
        
        # Cooldown period after time change - don't apply any updates
        if current_time_now < self.time_change_cooldown:
            return
        
        current_matrix = cmds.xform(PIVOT_NULL, q=True, ws=True, matrix=True)
        
        # After time change, require significant movement before applying updates
        if self.awaiting_real_manipulation:
            if self.matrix_moved_significantly(self.last_pivot_matrix, current_matrix):
                self.awaiting_real_manipulation = False
            else:
                # Update last_pivot_matrix to track small drifts but don't apply relationship
                self.last_pivot_matrix = current_matrix
                return
        
        # Check if matrix changed
        matrix_changed = self.last_pivot_matrix is None or not self.matrices_equal(self.last_pivot_matrix, current_matrix, tolerance=0.0005)
        
        # Only apply relationship when pivot is actually being manipulated
        if matrix_changed:
            self.last_pivot_matrix = current_matrix
            self.apply_xform_relationship()
            self.store_pivot_offset()
            self.last_change_time = current_time_now
            self.pending_reapply = True
        
        # Delayed reapply after manipulation stops (0.3 sec delay)
        if self.pending_reapply and (current_time_now - self.last_change_time) >= self.reapply_delay:
            self.apply_xform_relationship()
            # Update relationship after delayed reapply (also updates last_pivot_matrix)
            self.store_relationship()
            self.pending_reapply = False
        
        # Check if pivot got a new keyframe - if so, key all objects immediately
        current_key_count = get_key_count(PIVOT_NULL, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        if current_key_count > self.last_pivot_key_count:
            # Store pivot position BEFORE deleting keys
            pivot_matrix_before = cmds.xform(PIVOT_NULL, q=True, ws=True, matrix=True)
            
            # Key all objects - this is what user actually wants
            for obj in self.sel:
                if obj_exists(obj):
                    cmds.setKeyframe(obj, attribute=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
            
            # Track that we set keys this session
            self.keys_set_this_session = True
            
            # Delete ALL pivot keys immediately - pivot keys are just triggers
            # This way timeline shows OBJECT keys, not pivot keys
            for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
                try:
                    cmds.cutKey(PIVOT_NULL, attribute=attr, clear=True)
                except:
                    pass
            
            # Restore pivot position
            cmds.xform(PIVOT_NULL, ws=True, matrix=pivot_matrix_before)
            
            # Update state
            self.store_relationship()
            self.store_pivot_offset()
            self.last_pivot_matrix = pivot_matrix_before
            self.awaiting_real_manipulation = False
            self.pending_reapply = False
            self.last_pivot_key_count = 0
    
    def cache_locked_attrs(self):
        self.locked_attrs = {}
        for obj in self.sel:
            locked = {}
            skip_t = []
            skip_r = []
            
            for axis in ['x', 'y', 'z']:
                if is_attr_locked(obj, 't' + axis):
                    locked['t' + axis] = True
                    skip_t.append(axis)
                if is_attr_locked(obj, 'r' + axis):
                    locked['r' + axis] = True
                    skip_r.append(axis)
            
            locked["skip_t"] = skip_t
            locked["skip_r"] = skip_r
            locked["all_locked"] = len(skip_t) == 3 and len(skip_r) == 3
            
            self.locked_attrs[obj] = locked
    
    def check_objects_had_keys(self):
        attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
        for obj in self.sel:
            if has_keyframes(obj, attrs):
                self.objects_had_keys = True
                return
        self.objects_had_keys = False
    
    def store_pivot_offset(self):
        if not obj_exists(PIVOT_NULL) or not self.ref_obj or not obj_exists(self.ref_obj):
            return
        
        ref_matrix = om.MMatrix(cmds.xform(self.ref_obj, q=True, ws=True, matrix=True))
        pivot_matrix = om.MMatrix(cmds.xform(PIVOT_NULL, q=True, ws=True, matrix=True))
        
        ref_inverse = ref_matrix.inverse()
        self.pivot_to_ref_offset = pivot_matrix * ref_inverse
    
    def apply_pivot_from_ref(self):
        if not obj_exists(PIVOT_NULL) or not self.ref_obj or not obj_exists(self.ref_obj):
            return
        if self.pivot_to_ref_offset is None:
            return
        
        current_ref_matrix = om.MMatrix(cmds.xform(self.ref_obj, q=True, ws=True, matrix=True))
        new_pivot_matrix = self.pivot_to_ref_offset * current_ref_matrix
        
        cmds.xform(PIVOT_NULL, matrix=list(new_pivot_matrix), worldSpace=True)
        self.last_pivot_matrix = cmds.xform(PIVOT_NULL, q=True, ws=True, matrix=True)
    
    def store_relationship(self):
        if not obj_exists(PIVOT_NULL):
            return
        
        pivot_matrix = cmds.xform(PIVOT_NULL, q=True, ws=True, matrix=True)
        self.last_pivot_matrix = pivot_matrix
        
        self.relationship_data = {
            "pivot_matrix": pivot_matrix,
            "objects": []
        }
        
        for obj in self.sel:
            if not obj_exists(obj):
                continue
            
            obj_matrix = cmds.xform(obj, q=True, ws=True, matrix=True)
            locked_info = self.locked_attrs.get(obj, {})
            
            self.relationship_data["objects"].append({
                "name": obj,
                "matrix": obj_matrix,
                "locked": locked_info
            })
    
    def apply_xform_at_frame(self, objects):
        if not obj_exists(PIVOT_NULL):
            return
        if not self.original_relationship_data:
            return
        
        pivot_matrix = om.MMatrix(cmds.xform(PIVOT_NULL, q=True, ws=True, matrix=True))
        stored_pivot_matrix = om.MMatrix(self.original_relationship_data.get("pivot_matrix", []))
        stored_pivot_inverse = stored_pivot_matrix.inverse()
        
        for obj_data in self.original_relationship_data.get("objects", []):
            obj_name = obj_data.get("name")
            if not obj_name or not obj_exists(obj_name):
                continue
            if obj_name not in objects:
                continue
            
            locked_info = obj_data.get("locked", {})
            if locked_info.get("all_locked", False):
                continue
            
            stored_obj_matrix = om.MMatrix(obj_data.get("matrix", []))
            target_matrix = stored_obj_matrix * stored_pivot_inverse * pivot_matrix
            
            skip_t = locked_info.get("skip_t", [])
            skip_r = locked_info.get("skip_r", [])
            
            if len(skip_t) == 0 and len(skip_r) == 0:
                cmds.xform(obj_name, matrix=list(target_matrix), worldSpace=True)
            else:
                xform = om.MTransformationMatrix(target_matrix)
                
                if len(skip_t) < 3:
                    new_pos = xform.translation(om.MSpace.kWorld)
                    current_pos = cmds.xform(obj_name, q=True, ws=True, t=True)
                    final_pos = [
                        current_pos[0] if 'x' in skip_t else new_pos.x,
                        current_pos[1] if 'y' in skip_t else new_pos.y,
                        current_pos[2] if 'z' in skip_t else new_pos.z
                    ]
                    cmds.xform(obj_name, ws=True, t=final_pos)
                
                if len(skip_r) < 3:
                    euler = xform.rotation()
                    new_rot = [
                        om.MAngle(euler.x).asDegrees(),
                        om.MAngle(euler.y).asDegrees(),
                        om.MAngle(euler.z).asDegrees()
                    ]
                    current_rot = cmds.xform(obj_name, q=True, ws=True, ro=True)
                    final_rot = [
                        current_rot[0] if 'x' in skip_r else new_rot[0],
                        current_rot[1] if 'y' in skip_r else new_rot[1],
                        current_rot[2] if 'z' in skip_r else new_rot[2]
                    ]
                    cmds.xform(obj_name, ws=True, ro=final_rot)
            
            cmds.setKeyframe(obj_name, attribute=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
    
    def apply_xform_relationship(self):
        if not self.relationship_data or not obj_exists(PIVOT_NULL):
            return
        
        stored_pivot_matrix = om.MMatrix(self.relationship_data.get("pivot_matrix", []))
        stored_pivot_inverse = stored_pivot_matrix.inverse()
        current_pivot_matrix = om.MMatrix(cmds.xform(PIVOT_NULL, q=True, ws=True, matrix=True))
        
        for obj_data in self.relationship_data.get("objects", []):
            obj_name = obj_data.get("name")
            if not obj_name or not obj_exists(obj_name):
                continue
            
            locked_info = obj_data.get("locked", {})
            if locked_info.get("all_locked", False):
                continue
            
            stored_obj_matrix = om.MMatrix(obj_data.get("matrix", []))
            target_matrix = stored_obj_matrix * stored_pivot_inverse * current_pivot_matrix
            
            skip_t = locked_info.get("skip_t", [])
            skip_r = locked_info.get("skip_r", [])
            
            if len(skip_t) == 0 and len(skip_r) == 0:
                cmds.xform(obj_name, matrix=list(target_matrix), worldSpace=True)
            else:
                xform = om.MTransformationMatrix(target_matrix)
                
                if len(skip_t) < 3:
                    new_pos = xform.translation(om.MSpace.kWorld)
                    current_pos = cmds.xform(obj_name, q=True, ws=True, t=True)
                    final_pos = [
                        current_pos[0] if 'x' in skip_t else new_pos.x,
                        current_pos[1] if 'y' in skip_t else new_pos.y,
                        current_pos[2] if 'z' in skip_t else new_pos.z
                    ]
                    cmds.xform(obj_name, ws=True, t=final_pos)
                
                if len(skip_r) < 3:
                    euler = xform.rotation()
                    new_rot = [
                        om.MAngle(euler.x).asDegrees(),
                        om.MAngle(euler.y).asDegrees(),
                        om.MAngle(euler.z).asDegrees()
                    ]
                    current_rot = cmds.xform(obj_name, q=True, ws=True, ro=True)
                    final_rot = [
                        current_rot[0] if 'x' in skip_r else new_rot[0],
                        current_rot[1] if 'y' in skip_r else new_rot[1],
                        current_rot[2] if 'z' in skip_r else new_rot[2]
                    ]
                    cmds.xform(obj_name, ws=True, ro=final_rot)
    
    def on_time_changed(self):
        if not obj_exists(PIVOT_NULL):
            return
        
        self.is_time_changing = True
        
        # Cancel any pending reapply from previous frame
        self.pending_reapply = False
        
        # Temporarily disable autokey
        autokey_state = cmds.autoKeyframe(q=True, state=True)
        if autokey_state:
            cmds.autoKeyframe(state=False)
        
        try:
            # Safety net: clear any stray pivot keys
            for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
                try:
                    cmds.cutKey(PIVOT_NULL, attribute=attr, clear=True)
                except:
                    pass
            
            # Reposition pivot to follow ref object
            self.apply_pivot_from_ref()
            self.store_relationship()
            self.store_pivot_offset()
            
        finally:
            if autokey_state:
                cmds.autoKeyframe(state=True)
        
        # Update last_pivot_matrix to current position
        self.last_pivot_matrix = cmds.xform(PIVOT_NULL, q=True, ws=True, matrix=True)
        
        # Pivot should never have keys (we delete them immediately)
        self.last_pivot_key_count = 0
        
        # Set cooldown period
        self.time_change_cooldown = time.time() + self.cooldown_duration
        
        # Require significant movement before applying any updates
        self.awaiting_real_manipulation = True
        
        self.is_time_changing = False
        
        self.time_job = cmds.scriptJob(runOnce=True, killWithScene=True, event=["timeChanged", time_changed])
    
    def save_relationship_to_disk(self):
        if not obj_exists(PIVOT_NULL):
            return
        if not self.original_matrices:
            return
        
        selection = list(self.original_matrices.keys())
        if not selection:
            return
        
        data = load_offsets()
        data["last_selection"] = selection
        
        # Get the PIVOT POINT position (rotatePivot in world space)
        pivot_pos = cmds.xform(PIVOT_NULL, q=True, ws=True, rp=True)
        pivot_rot = cmds.xform(PIVOT_NULL, q=True, ws=True, ro=True)
        
        # ALWAYS use last object as reference - use CURRENT position
        ref_obj = selection[-1]
        ref_pos = cmds.xform(ref_obj, q=True, ws=True, t=True)
        ref_rot = cmds.xform(ref_obj, q=True, ws=True, ro=True)
        ref_matrix = om.MMatrix(cmds.xform(ref_obj, q=True, ws=True, matrix=True))
        
        # Get world offset
        world_offset = om.MVector(
            pivot_pos[0] - ref_pos[0],
            pivot_pos[1] - ref_pos[1],
            pivot_pos[2] - ref_pos[2]
        )
        
        # Transform to ref's LOCAL space (remove ref's rotation)
        ref_xform = om.MTransformationMatrix(ref_matrix)
        ref_xform.setTranslation(om.MVector(0, 0, 0), om.MSpace.kWorld)
        rot_matrix_inv = ref_xform.asMatrix().inverse()
        
        local_offset = world_offset * rot_matrix_inv
        
        offset_rot = [
            pivot_rot[0] - ref_rot[0],
            pivot_rot[1] - ref_rot[1],
            pivot_rot[2] - ref_rot[2]
        ]
        
        offset_data = {
            "offset_pos": [local_offset.x, local_offset.y, local_offset.z],
            "offset_rot": offset_rot,
            "ref_obj": ref_obj
        }
        
        if len(selection) == 1:
            data["single_offsets"][ref_obj] = offset_data
        else:
            sel_sorted = sorted(selection)
            found = False
            for group in data["multi_offsets"]:
                if sorted(group["objects"]) == sel_sorted:
                    group["offset_data"] = offset_data
                    found = True
                    break
            if not found:
                data["multi_offsets"].append({
                    "objects": list(selection), 
                    "offset_data": offset_data
                })
        
        save_offsets(data)
    
    def apply_stored_offset(self, selection):
        if not obj_exists(PIVOT_NULL):
            return False
        
        path = get_prefs_path()
        if not os.path.exists(path):
            return False
        
        global _cache_valid
        _cache_valid = False
        data = load_offsets()
        offset_data = None
        
        if len(selection) == 1:
            obj = selection[0]
            single_offsets = data.get("single_offsets", {})
            if obj in single_offsets:
                offset_data = single_offsets[obj]
        else:
            multi_offsets = data.get("multi_offsets", [])
            sel_sorted = sorted(selection)
            for group in multi_offsets:
                if sorted(group.get("objects", [])) == sel_sorted:
                    if "offset_data" in group:
                        offset_data = group["offset_data"]
                    break
        
        if not offset_data or "offset_pos" not in offset_data:
            return False
        
        ref_obj = offset_data.get("ref_obj", selection[-1])
        if not obj_exists(ref_obj):
            ref_obj = selection[-1]
        
        ref_matrix = om.MMatrix(cmds.xform(ref_obj, q=True, ws=True, matrix=True))
        ref_pos = cmds.xform(ref_obj, q=True, ws=True, t=True)
        
        offset_pos = offset_data["offset_pos"]
        offset_rot = offset_data["offset_rot"]
        local_offset = om.MVector(offset_pos[0], offset_pos[1], offset_pos[2])
        
        ref_xform = om.MTransformationMatrix(ref_matrix)
        ref_xform.setTranslation(om.MVector(0, 0, 0), om.MSpace.kWorld)
        rot_matrix = ref_xform.asMatrix()
        
        world_offset = local_offset * rot_matrix
        
        new_pivot_pos = [
            ref_pos[0] + world_offset.x,
            ref_pos[1] + world_offset.y,
            ref_pos[2] + world_offset.z
        ]
        
        ref_rot = cmds.xform(ref_obj, q=True, ws=True, ro=True)
        new_pivot_rot = [
            ref_rot[0] + offset_rot[0],
            ref_rot[1] + offset_rot[1],
            ref_rot[2] + offset_rot[2]
        ]
        
        cmds.xform(PIVOT_NULL, ws=True, t=new_pivot_pos)
        cmds.xform(PIVOT_NULL, ws=True, ro=new_pivot_rot)
        
        return True
    
    def create(self):
        if obj_exists(PIVOT_NULL):
            self.clear()
            return
        
        self.sel = cmds.ls(selection=True)
        
        if not self.sel:
            data = load_offsets()
            last_sel = data.get("last_selection", [])
            valid_sel = [obj for obj in last_sel if obj_exists(obj)]
            
            if valid_sel:
                set_selection(valid_sel)
                self.sel = valid_sel
            else:
                return
        
        try:
            cmds.refresh(suspend=True)
            
            for _ in range(4):
                cmds.undoInfo(openChunk=True)
                cmds.undoInfo(closeChunk=True)
            cmds.undoInfo(openChunk=True)
            
            self.ref_obj = self.sel[-1]
            cmds.sets(self.sel, name=PIVOT_SET)
            
            self.original_frame = get_current_time()
            
            self.original_matrices = {}
            for obj in self.sel:
                self.original_matrices[obj] = cmds.xform(obj, q=True, ws=True, matrix=True)
            
            self.cache_locked_attrs()
            self.check_objects_had_keys()
            
            pivot_grp = cmds.group(empty=True, name=PIVOT_NULL)
            
            # Lock and hide scale and visibility attributes
            for attr in ['sx', 'sy', 'sz', 'v']:
                cmds.setAttr(PIVOT_NULL + '.' + attr, lock=True, keyable=False, channelBox=False)
            
            cmds.matchTransform(pivot_grp, self.ref_obj, pos=True, rot=True)
            self.apply_stored_offset(self.sel)
            
            self.store_relationship()
            # Store original relationship for baking keys later
            self.original_relationship_data = copy.deepcopy(self.relationship_data)
            self.store_pivot_offset()
            # Initialize key count tracking
            self.last_pivot_key_count = 0
            
            # Make timeline show OBJECT keys instead of pivot keys
            self.setup_timeline_connection()
            
            self.start_timer()
            
        except Exception as e:
            cmds.refresh(suspend=False)
            self.cleanup_setup()
            cmds.warning("Pivot tool error: {}".format(str(e)))
            return
        finally:
            cmds.refresh(suspend=False)
        
        cmds.select(PIVOT_NULL)
        cmds.setToolTo("moveSuperContext")
        cmds.ctxEditMode()
        
        self.selection_job = cmds.scriptJob(runOnce=True, killWithScene=True, event=["SelectionChanged", clear])
        self.time_job = cmds.scriptJob(runOnce=True, killWithScene=True, event=["timeChanged", time_changed])
    
    def bake_keys_from_pivot(self, objects):
        if not obj_exists(PIVOT_NULL):
            return
        
        pivot_keyframes = get_all_keyframes(PIVOT_NULL, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        if not pivot_keyframes:
            return
        
        current_frame = get_current_time()
        
        for frame in pivot_keyframes:
            set_current_time(frame)
            self.apply_xform_at_frame(objects)
        
        set_current_time(current_frame)
    
    def clear(self):
        objects = None
        transforms = {}
        
        if obj_exists(PIVOT_SET):
            objects = cmds.sets(PIVOT_SET, q=True) or []
        
        # Capture the current transforms (objects are already in correct position)
        if objects:
            for obj in objects:
                if obj_exists(obj):
                    transforms[obj] = cmds.xform(obj, q=True, ws=True, matrix=True)
        
        try:
            cmds.refresh(suspend=True)
            
            self.stop_timer()
            self.restore_timeline_connection()
            
            if objects and obj_exists(PIVOT_NULL):
                self.save_relationship_to_disk()
                # Keys are now set live when pivot is keyed, no baking needed
            
            if obj_exists(PIVOT_NULL):
                cmds.delete(PIVOT_NULL)
                
            if obj_exists(PIVOT_SET):
                cmds.delete(PIVOT_SET)
            
            for obj, mtx in transforms.items():
                if obj_exists(obj):
                    try:
                        cmds.xform(obj, ws=True, matrix=mtx)
                    except:
                        pass
            
            # Set final keys if objects had keys or we set keys during this session
            if self.objects_had_keys or self.keys_set_this_session:
                for obj in (objects or []):
                    if obj_exists(obj):
                        cmds.setKeyframe(obj, attribute=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
                
        except Exception as e:
            cmds.warning("Pivot tool error during clear: {}".format(str(e)))
            self.cleanup_setup()
        finally:
            cmds.refresh(suspend=False)
            cmds.undoInfo(closeChunk=True)
        
        self.original_matrices = {}
        self.original_frame = None
        self.relationship_data = {}
        self.original_relationship_data = {}
        self.last_pivot_key_count = 0
        self.last_change_time = 0
        self.pending_reapply = False
        self.time_change_cooldown = 0
        self.awaiting_real_manipulation = False
        self.keys_set_this_session = False
        
        try:
            if self.time_job and cmds.scriptJob(exists=self.time_job):
                cmds.scriptJob(kill=self.time_job)
        except:
            pass
        self.time_job = None
        
        try:
            if self.selection_job and cmds.scriptJob(exists=self.selection_job):
                cmds.scriptJob(kill=self.selection_job)
        except:
            pass
        self.selection_job = None
        
        if objects:
            set_selection(objects)


_pivot = LiveTempPivot()


def pivot():
    _pivot.create()
    

def clear():
    _pivot.clear()


def time_changed():
    _pivot.on_time_changed()


def save_pivot():
    _pivot.save_relationship_to_disk()


def reset_offsets():
    global _cache_valid
    _cache_valid = False
    save_offsets({"single_offsets": {}, "multi_offsets": [], "last_selection": []})


load_offsets()

pivot()