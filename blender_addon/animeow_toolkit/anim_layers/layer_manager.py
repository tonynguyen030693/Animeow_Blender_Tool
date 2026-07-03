"""
layer_manager.py — Animeow Toolkit / Anim Layers
====================================================
Lớp quản lý trung tâm (LayerManager) chịu trách nhiệm dịch mọi thao tác
Animation Layer sang lệnh NLA (Non-Linear Animation) tương ứng của Blender.

KIẾN TRÚC GLOBAL:
- Danh sách layer được lưu trên Scene (`scene.animeow_global_layers`).
- Mỗi thao tác sẽ lặp qua TẤT CẢ objects có NLA track tương ứng
  để thực thi đồng bộ.
- Bất kể đang chọn object nào, danh sách layer luôn cố định.
"""

import bpy
import re
from ..core.utils import get_action_fcurves, clean_fcurve_keyframes

# Tiền tố đặt tên cho các Action/Track do module tạo
ANL_PREFIX = "ANL_"
ANL_BASE_NAME = "ANL_Base"


def is_valid_action(action):
    """Kiểm tra xem Action có hợp lệ hay đã bị xóa khỏi Blender (ReferenceError)"""
    if not action:
        return False
    try:
        _ = action.name
        return True
    except ReferenceError:
        return False


def strip_blender_suffix(name):
    """Cắt bỏ hậu tố trùng lặp .00x của Blender ở cuối chuỗi nếu có"""
    return re.sub(r'\.\d{3}$', '', name)


def is_track_for_action(track, action):
    """So sánh tên track và action bỏ qua hậu tố .00x của Blender"""
    if not action:
        return False
    t_name = strip_blender_suffix(track.name)
    a_name = strip_blender_suffix(action.name)
    return t_name == a_name


def _set_active_action(anim_data, action):
    """Gán active action cho anim_data và tự động cấu hình action_slot cho Blender 5.0+"""
    anim_data.action = action
    if action and hasattr(anim_data, "action_slot"):
        # 1. Thử lấy trực tiếp từ slots của Action (chính xác và không phụ thuộc DPG update)
        if hasattr(action, "slots") and len(action.slots) > 0:
            anim_data.action_slot = action.slots[0]
        # 2. Fallback: Update view_layer và lấy từ action_suitable_slots
        elif hasattr(anim_data, "action_suitable_slots"):
            bpy.context.view_layer.update()
            if anim_data.action_suitable_slots:
                anim_data.action_slot = anim_data.action_suitable_slots[0]


def _track_name_for_layer(layer_name):
    """Tạo tên NLA track từ tên layer hiển thị."""
    return f"{ANL_PREFIX}{layer_name}"


def _get_bone_select(pb):
    """Retrieve the selection state of a PoseBone in a version-agnostic way."""
    if hasattr(pb, "select"):
        return pb.select
    if hasattr(pb, "bone") and hasattr(pb.bone, "select"):
        return pb.bone.select
    return False


def _set_bone_select(pb, select):
    """Set the selection state of a PoseBone in a version-agnostic way."""
    if hasattr(pb, "select"):
        pb.select = select
    elif hasattr(pb, "bone") and hasattr(pb.bone, "select"):
        pb.bone.select = select


class LayerManager:
    """Bộ não điều phối NLA backend cho hệ thống Global Animation Layers.

    Danh sách layer được lưu trên Scene (scene.animeow_global_layers).
    Mỗi thao tác sẽ lặp qua tất cả objects có NLA track tương ứng
    để thực thi đồng bộ.
    """

    @staticmethod
    def _find_track_for_layer(anim_data, layer_name, is_base=False, scene=None):
        """Tìm NLA track tương ứng với layer, có hỗ trợ fallback cho Base track cũ."""
        if not anim_data:
            return None
        
        # 1. Nếu không phải Base, tìm chính xác theo tên
        track_name = _track_name_for_layer(layer_name)
        if not is_base:
            for track in anim_data.nla_tracks:
                if strip_blender_suffix(track.name) == strip_blender_suffix(track_name):
                    return track
            return None

        # 2. Nếu là Base, lấy danh sách tên các non-base layers trong scene để loại trừ
        active_scene = scene or getattr(bpy.context, "scene", None)
        non_base_names = set()
        if active_scene:
            for i, layer in enumerate(active_scene.animeow_global_layers):
                if i > 0: # Bỏ qua index 0 (Base)
                    non_base_names.add(strip_blender_suffix(layer.name).lower())

        # 3. Gom tất cả track ANL_ không nằm trong danh sách non-base layers
        candidates = []
        for track in anim_data.nla_tracks:
            if not track.name.startswith(ANL_PREFIX):
                continue
            display_name = track.name[len(ANL_PREFIX):]
            display_name_stripped = strip_blender_suffix(display_name).lower()
            if display_name_stripped not in non_base_names:
                candidates.append(track)

        if not candidates:
            return None

        # 4. Ưu tiên track có strips (chứa keyframe)
        for track in candidates:
            if len(track.strips) > 0:
                return track

        # 5. Nếu không có cái nào có strips, hoặc tất cả như nhau, ưu tiên track tên chính xác ANL_Base
        for track in candidates:
            if strip_blender_suffix(track.name) == strip_blender_suffix(track_name):
                return track

        return candidates[0]

    # ──────────────────────────────────────────
    #  ĐỌC THÔNG TIN
    # ──────────────────────────────────────────

    @staticmethod
    def get_global_layers(scene):
        """Trả về danh sách global layers từ Scene.

        Returns:
            bpy.types.bpy_prop_collection — CollectionProperty chứa
            các AnimeowGlobalLayer.
        """
        return scene.animeow_global_layers

    @staticmethod
    def get_active_index(scene):
        """Trả về index của layer đang active."""
        return scene.animeow_global_active_index

    @staticmethod
    def has_layers(scene):
        """Kiểm tra nhanh xem Scene có đang sử dụng hệ thống Layer không."""
        return len(scene.animeow_global_layers) > 0

    @staticmethod
    def get_member_objects(scene, layer_name):
        """Trả về tất cả objects trong scene có NLA track cho layer này.

        Args:
            scene: Blender Scene.
            layer_name: Tên hiển thị của layer (không có prefix ANL_).

        Returns:
            List[Object] — Danh sách objects tham gia layer.
        """
        is_base = (layer_name == "Base")
        members = []
        for obj in scene.objects:
            anim_data = obj.animation_data
            if not anim_data:
                continue
            track = LayerManager._find_track_for_layer(anim_data, layer_name, is_base)
            if track:
                members.append(obj)
        return members

    @staticmethod
    def get_all_member_objects(scene):
        """Trả về tất cả objects trong scene có bất kỳ ANL_ track nào.

        Returns:
            List[Object]
        """
        members = []
        for obj in scene.objects:
            anim_data = obj.animation_data
            if not anim_data:
                continue
            for track in anim_data.nla_tracks:
                if track.name.startswith(ANL_PREFIX):
                    members.append(obj)
                    break
        return members

    # ──────────────────────────────────────────
    #  THÊM LAYER
    # ──────────────────────────────────────────

    @staticmethod
    def add_layer(scene, name="New Layer", blend_type='ADD'):
        """Tạo layer mới trong danh sách global.

        Tạo entry trong scene.animeow_global_layers.
        KHÔNG tự động thêm objects — người dùng sẽ dùng Add Selected.

        Args:
            scene: Blender Scene.
            name: Tên hiển thị của layer mới.
            blend_type: Chế độ blend ('ADD', 'REPLACE', 'COMBINE').

        Returns:
            AnimeowGlobalLayer — entry vừa tạo, hoặc None nếu thất bại.
        """
        layers = scene.animeow_global_layers

        # Nếu chưa có layer nào → tạo Base trước
        if len(layers) == 0:
            base = layers.add()
            base.name = "Base"
            base.blend_type = 'REPLACE'
            base.influence = 1.0
            base.mute = False
            base.is_base = True

        # Đảm bảo tên không bị trùng trong global layers
        unique_name = name
        existing_names = {l.name for l in layers}
        if unique_name in existing_names:
            suffix = 1
            while f"{name}_{suffix:03d}" in existing_names:
                suffix += 1
            unique_name = f"{name}_{suffix:03d}"

        # Tạo layer mới
        new_layer = layers.add()
        new_layer.name = unique_name
        new_layer.blend_type = blend_type
        new_layer.influence = 1.0
        new_layer.mute = False
        new_layer.is_base = False

        return new_layer

    # ──────────────────────────────────────────
    #  THÊM / GỠ OBJECTS VÀO LAYER
    # ──────────────────────────────────────────

    @staticmethod
    def add_objects_to_layer(scene, objects, layer_index):
        """Thêm các objects vào layer tại layer_index.

        Với mỗi object:
        1. Nếu chưa có animation_data → tạo.
        2. Nếu chưa có Base track → push action hiện tại thành Base.
        3. Tạo NLA track + Action rỗng cho layer được chỉ định.

        Args:
            scene: Blender Scene.
            objects: Danh sách Objects cần thêm.
            layer_index: Index trong scene.animeow_global_layers.

        Returns:
            int — Số objects đã được thêm thành công.
        """
        layers = scene.animeow_global_layers
        if layer_index < 0 or layer_index >= len(layers):
            return 0

        target_layer = layers[layer_index]
        track_name = _track_name_for_layer(target_layer.name)
        frame_start = scene.frame_start
        frame_end = scene.frame_end

        count = 0
        for obj in objects:
            anim_data = obj.animation_data
            if not anim_data:
                anim_data = obj.animation_data_create()

            # Kiểm tra xem object đã có track này chưa
            existing = LayerManager._find_track_for_layer(anim_data, target_layer.name, target_layer.is_base)

            if existing:
                continue  # Đã có rồi, bỏ qua

            # Đảm bảo Base layer tồn tại trên object
            LayerManager._ensure_base_on_object(obj, scene)

            # Nếu đang thêm vào Base layer, object đã có Base rồi → bỏ qua
            if target_layer.is_base:
                count += 1
                continue

            # Push active action nếu có (để tránh conflict)
            if anim_data.action:
                LayerManager._push_active_to_nla(obj, scene)

            # Tạo Action rỗng mới cho layer
            action_name = track_name
            new_action = bpy.data.actions.new(name=action_name)
            new_action.use_fake_user = True

            # Đảm bảo tạo slot cho Action mới trong Blender 5.0+
            if hasattr(new_action, "slots"):
                id_type = 'OBJECT'
                new_slot = new_action.slots.new(id_type=id_type, name=obj.name)

            # Tạo NLA track + strip
            track = anim_data.nla_tracks.new()
            track.name = new_action.name
            track.mute = target_layer.mute

            # Đặt làm active action (pull lên)
            # Xóa strip vừa tạo → set làm active
            _set_active_action(anim_data, new_action)
            anim_data.action_blend_type = target_layer.blend_type
            anim_data.action_influence = target_layer.influence
            anim_data.use_nla = True

            count += 1

        return count

    @staticmethod
    def remove_objects_from_layer(scene, objects, layer_index):
        """Gỡ các objects khỏi layer tại layer_index.

        Xóa NLA track + Action tương ứng trên mỗi object.

        Args:
            scene: Blender Scene.
            objects: Danh sách Objects cần gỡ.
            layer_index: Index trong scene.animeow_global_layers.

        Returns:
            int — Số objects đã được gỡ thành công.
        """
        layers = scene.animeow_global_layers
        if layer_index < 0 or layer_index >= len(layers):
            return 0

        target_layer = layers[layer_index]
        track_name = _track_name_for_layer(target_layer.name)

        # Không cho gỡ khỏi Base layer
        if target_layer.is_base:
            return 0

        count = 0
        for obj in objects:
            anim_data = obj.animation_data
            if not anim_data:
                continue

            # Nếu active action thuộc layer này → xóa nó
            if anim_data.action and is_valid_action(anim_data.action):
                act_name = strip_blender_suffix(anim_data.action.name)
                if act_name == strip_blender_suffix(track_name):
                    action_to_remove = anim_data.action
                    anim_data.action = None
                    bpy.data.actions.remove(action_to_remove)
                    count += 1

            # Tìm và xóa track
            track_to_remove = LayerManager._find_track_for_layer(anim_data, target_layer.name, target_layer.is_base)

            if track_to_remove:
                # Xóa action trong strip trước
                for strip in track_to_remove.strips:
                    if strip.action:
                        bpy.data.actions.remove(strip.action)

                anim_data.nla_tracks.remove(track_to_remove)
                count += 1

        return count

    # ──────────────────────────────────────────
    #  CHỌN LAYER (SWITCH)
    # ──────────────────────────────────────────

    @staticmethod
    def select_layer(scene, layer_index):
        """Chuyển sang layer tại layer_index trên TẤT CẢ member objects.

        Logic cho mỗi object:
        1. Push active action hiện tại vào NLA track tương ứng.
        2. Pull action từ target layer track ra → set làm active.

        Args:
            scene: Blender Scene.
            layer_index: Vị trí trong danh sách global layers.

        Returns:
            True nếu thành công, False nếu thất bại.
        """
        layers = scene.animeow_global_layers
        if layer_index < 0 or layer_index >= len(layers):
            return False



        target_layer = layers[layer_index]
        track_name = _track_name_for_layer(target_layer.name)

        # Lặp qua tất cả objects có ANL tracks
        all_members = LayerManager.get_all_member_objects(scene)
        for obj in all_members:
            anim_data = obj.animation_data
            if not anim_data:
                continue

            # 1. Push active action hiện tại vào NLA (sử dụng index cũ vẫn đang lưu trên scene)
            if anim_data.action:
                LayerManager._push_active_to_nla(obj, scene)

        # Cập nhật active index MỚI trên Scene sau khi đã push xong
        scene.animeow_global_active_index = layer_index

        for obj in all_members:
            anim_data = obj.animation_data
            if not anim_data:
                continue

            # Tìm track của target layer trên object này
            target_track = LayerManager._find_track_for_layer(anim_data, target_layer.name, target_layer.is_base)

            if not target_track:
                continue  # Object không tham gia layer này

            # 3. Pull action từ NLA → active
            if len(target_track.strips) > 0:
                strip = target_track.strips[0]
                action = strip.action
                blend_type = strip.blend_type
                influence = strip.influence

                # Xóa strip nhưng giữ track rỗng
                target_track.strips.remove(strip)

                # Set active
                _set_active_action(anim_data, action)
                anim_data.action_blend_type = blend_type
                anim_data.action_influence = influence
            else:
                # Nếu track rỗng → tìm và khôi phục action tương ứng từ memory (nếu có)
                target_action_name = _track_name_for_layer(target_layer.name)
                action = bpy.data.actions.get(target_action_name)
                
                # Nếu là Base layer, thử tìm action cũ tên ANL_Action hoặc ANL_Base
                if not action and target_layer.is_base:
                    action = bpy.data.actions.get("ANL_Action") or bpy.data.actions.get("ANL_Base")

                if action:
                    _set_active_action(anim_data, action)
                    anim_data.action_blend_type = 'REPLACE' if target_layer.is_base else 'ADD'
                    anim_data.action_influence = 1.0
                else:
                    # Nếu hoàn toàn không có action trong memory → tạo mới rỗng
                    new_action = bpy.data.actions.new(name=target_action_name)
                    new_action.use_fake_user = True
                    # Đảm bảo tạo slot cho Blender 5.0+
                    if hasattr(new_action, "slots"):
                        id_type = 'POSE' if obj.type == 'ARMATURE' else 'OBJECT'
                        new_action.slots.new(id_type=id_type, name=obj.name)
                    
                    _set_active_action(anim_data, new_action)
                    anim_data.action_blend_type = 'REPLACE' if target_layer.is_base else 'ADD'
                    anim_data.action_influence = 1.0

        return True

    # ──────────────────────────────────────────
    #  XÓA LAYER
    # ──────────────────────────────────────────

    @staticmethod
    def delete_layer(scene, layer_index):
        """Xóa layer tại layer_index.

        Xóa entry khỏi global list + NLA track trên tất cả objects.
        Không cho xóa Base layer nếu chỉ còn 1 layer.

        Args:
            scene: Blender Scene.
            layer_index: Vị trí trong danh sách global layers.

        Returns:
            True nếu thành công, False nếu thất bại.
        """
        layers = scene.animeow_global_layers
        if layer_index < 0 or layer_index >= len(layers):
            return False

        target_layer = layers[layer_index]

        # Không cho xóa nếu chỉ còn 1 layer
        if len(layers) <= 1:
            return False

        # Không cho xóa Base layer
        if target_layer.is_base:
            return False

        track_name = _track_name_for_layer(target_layer.name)

        # Xóa NLA tracks trên tất cả objects
        all_members = LayerManager.get_all_member_objects(scene)
        for obj in all_members:
            anim_data = obj.animation_data
            if not anim_data:
                continue

            # Nếu active action thuộc layer bị xóa → clear nó
            if anim_data.action and is_valid_action(anim_data.action):
                act_name = strip_blender_suffix(anim_data.action.name)
                if act_name == strip_blender_suffix(track_name):
                    action_to_remove = anim_data.action
                    anim_data.action = None
                    bpy.data.actions.remove(action_to_remove)

            # Tìm và xóa track
            track_to_remove = LayerManager._find_track_for_layer(anim_data, target_layer.name, target_layer.is_base)

            if track_to_remove:
                for strip in track_to_remove.strips:
                    if strip.action:
                        bpy.data.actions.remove(strip.action)
                anim_data.nla_tracks.remove(track_to_remove)

        # Xóa khỏi global list
        layers.remove(layer_index)

        # Điều chỉnh active index
        if scene.animeow_global_active_index >= len(layers):
            scene.animeow_global_active_index = max(0, len(layers) - 1)

        # Chuyển sang layer mới nếu cần
        if len(layers) > 0:
            LayerManager.select_layer(scene, scene.animeow_global_active_index)

        return True

    # ──────────────────────────────────────────
    #  MUTE / SOLO
    # ──────────────────────────────────────────

    @staticmethod
    def set_mute(scene, layer_index, mute):
        """Bật/tắt mute cho layer trên TẤT CẢ member objects.

        Args:
            scene: Blender Scene.
            layer_index: Vị trí layer.
            mute: True để mute, False để unmute.

        Returns:
            True nếu thành công.
        """
        layers = scene.animeow_global_layers
        if layer_index < 0 or layer_index >= len(layers):
            return False

        target_layer = layers[layer_index]

        # Không thể mute layer đang active
        if layer_index == scene.animeow_global_active_index:
            return False

        # Cập nhật trạng thái mute trên global entry
        target_layer.mute = mute

        # Đồng bộ lên tất cả objects
        track_name = _track_name_for_layer(target_layer.name)
        all_members = LayerManager.get_all_member_objects(scene)
        for obj in all_members:
            anim_data = obj.animation_data
            if not anim_data:
                continue
            track = LayerManager._find_track_for_layer(anim_data, target_layer.name, target_layer.is_base)
            if track:
                track.mute = mute

        return True

    @staticmethod
    def set_solo(scene, layer_index):
        """Solo layer — mute tất cả track khác, chỉ unmute track được solo.

        Áp dụng trên TẤT CẢ member objects.

        Args:
            scene: Blender Scene.
            layer_index: Vị trí layer.

        Returns:
            True nếu thành công.
        """
        layers = scene.animeow_global_layers
        if layer_index < 0 or layer_index >= len(layers):
            return False

        # Kiểm tra xem layer này đã đang solo chưa
        target_layer = layers[layer_index]
        is_already_solo = not target_layer.mute
        for i, layer in enumerate(layers):
            if i == layer_index:
                continue
            if i == scene.animeow_global_active_index:
                continue  # Skip active layer
            if not layer.mute:
                is_already_solo = False
                break

        if is_already_solo:
            # Tắt solo → unmute tất cả
            for layer in layers:
                layer.mute = False
        else:
            # Bật solo
            for i, layer in enumerate(layers):
                if i == scene.animeow_global_active_index:
                    continue  # Không mute active layer
                layer.mute = (i != layer_index)

        # Đồng bộ mute state lên tất cả objects
        all_members = LayerManager.get_all_member_objects(scene)
        for obj in all_members:
            anim_data = obj.animation_data
            if not anim_data:
                continue
            for layer in layers:
                track = LayerManager._find_track_for_layer(anim_data, layer.name, layer.is_base)
                if track:
                    track.mute = layer.mute

        return True

    # ──────────────────────────────────────────
    #  WEIGHT / BLEND MODE
    # ──────────────────────────────────────────

    @staticmethod
    def set_weight(scene, layer_index, weight):
        """Đặt trọng số (influence) cho layer trên TẤT CẢ member objects.

        Args:
            scene: Blender Scene.
            layer_index: Vị trí layer.
            weight: Giá trị float 0.0 → 1.0.

        Returns:
            True nếu thành công.
        """
        layers = scene.animeow_global_layers
        if layer_index < 0 or layer_index >= len(layers):
            return False

        target_layer = layers[layer_index]
        weight = max(0.0, min(1.0, weight))
        target_layer.influence = weight

        track_name = _track_name_for_layer(target_layer.name)
        is_active = (layer_index == scene.animeow_global_active_index)

        all_members = LayerManager.get_all_member_objects(scene)
        for obj in all_members:
            anim_data = obj.animation_data
            if not anim_data:
                continue

            if is_active:
                # Active layer → set trên animation_data
                if anim_data.action:
                    anim_data.action_influence = weight
            else:
                # Non-active → set trên NLA strip
                track = LayerManager._find_track_for_layer(anim_data, target_layer.name, target_layer.is_base)
                if track and len(track.strips) > 0:
                    track.strips[0].influence = weight

        return True

    @staticmethod
    def set_blend_mode(scene, layer_index, mode):
        """Đổi blend mode cho layer trên TẤT CẢ member objects.

        Args:
            scene: Blender Scene.
            layer_index: Vị trí layer.
            mode: 'ADD', 'REPLACE', 'COMBINE', 'SUBTRACT', 'MULTIPLY'.

        Returns:
            True nếu thành công.
        """
        layers = scene.animeow_global_layers
        if layer_index < 0 or layer_index >= len(layers):
            return False

        target_layer = layers[layer_index]
        target_layer.blend_type = mode

        track_name = _track_name_for_layer(target_layer.name)
        is_active = (layer_index == scene.animeow_global_active_index)

        all_members = LayerManager.get_all_member_objects(scene)
        for obj in all_members:
            anim_data = obj.animation_data
            if not anim_data:
                continue

            if is_active:
                if anim_data.action:
                    anim_data.action_blend_type = mode
            else:
                track = LayerManager._find_track_for_layer(anim_data, target_layer.name, target_layer.is_base)
                if track and len(track.strips) > 0:
                    track.strips[0].blend_type = mode

        return True

    @staticmethod
    def keyframe_weight(scene, layer_index, frame, weight):
        """Keyframe weight (influence) tại frame cụ thể trên TẤT CẢ member objects.

        Args:
            scene: Blender Scene.
            layer_index: Vị trí layer.
            frame: Frame number.
            weight: Giá trị weight.

        Returns:
            True nếu thành công.
        """
        layers = scene.animeow_global_layers
        if layer_index < 0 or layer_index >= len(layers):
            return False

        target_layer = layers[layer_index]
        track_name = _track_name_for_layer(target_layer.name)
        is_active = (layer_index == scene.animeow_global_active_index)
        weight = max(0.0, min(1.0, weight))

        success = False
        all_members = LayerManager.get_all_member_objects(scene)
        for obj in all_members:
            anim_data = obj.animation_data
            if not anim_data:
                continue

            if is_active:
                if anim_data.action:
                    anim_data.action_influence = weight
                    anim_data.keyframe_insert(data_path="action_influence", frame=frame)
                    success = True
            else:
                track = LayerManager._find_track_for_layer(anim_data, target_layer.name, target_layer.is_base)
                if track and len(track.strips) > 0:
                    strip = track.strips[0]
                    strip.use_animated_influence = True
                    strip.influence = weight
                    strip.keyframe_insert(data_path="influence", frame=frame)
                    success = True

        return success

    # ──────────────────────────────────────────
    #  DI CHUYỂN LAYER
    # ──────────────────────────────────────────

    @staticmethod
    def move_layer(scene, layer_index, direction):
        """Di chuyển layer lên hoặc xuống trong global stack.

        Hoán đổi thứ tự trong scene.animeow_global_layers
        và đồng bộ NLA tracks trên tất cả objects.

        Args:
            scene: Blender Scene.
            layer_index: Vị trí layer hiện tại.
            direction: 'UP' hoặc 'DOWN'.

        Returns:
            int — index mới của layer, hoặc -1 nếu thất bại.
        """
        layers = scene.animeow_global_layers
        if layer_index < 0 or layer_index >= len(layers):
            return -1

        # UP trên màn hình = tăng index (vì UI vẽ ngược)
        target_index = layer_index + 1 if direction == 'UP' else layer_index - 1
        if target_index < 0 or target_index >= len(layers):
            return -1

        # Không cho di chuyển Base layer
        if layers[layer_index].is_base or layers[target_index].is_base:
            return -1

        # 1. Push active action trên tất cả objects
        all_members = LayerManager.get_all_member_objects(scene)
        for obj in all_members:
            anim_data = obj.animation_data
            if anim_data and anim_data.action:
                LayerManager._push_active_to_nla(obj, scene)

        # 2. Hoán đổi NLA tracks trên tất cả objects
        layer_a = layers[layer_index]
        layer_b = layers[target_index]
        track_name_a = _track_name_for_layer(layer_a.name)
        track_name_b = _track_name_for_layer(layer_b.name)

        for obj in all_members:
            anim_data = obj.animation_data
            if not anim_data:
                continue

            t_a = LayerManager._find_track_for_layer(anim_data, layer_a.name, layer_a.is_base)
            t_b = LayerManager._find_track_for_layer(anim_data, layer_b.name, layer_b.is_base)

            if t_a and t_b and len(t_a.strips) > 0 and len(t_b.strips) > 0:
                s_a = t_a.strips[0]
                s_b = t_b.strips[0]

                # Hoán đổi tên tracks
                temp = t_a.name
                t_a.name = t_b.name + "_temp"
                t_b.name = temp
                t_a.name = t_a.name.replace("_temp", "")

                # Hoán đổi actions
                temp_act = s_a.action
                s_a.action = s_b.action
                s_b.action = temp_act

                # Hoán đổi blend_type
                temp_blend = s_a.blend_type
                s_a.blend_type = s_b.blend_type
                s_b.blend_type = temp_blend

                # Hoán đổi influence
                temp_inf = s_a.influence
                s_a.influence = s_b.influence
                s_b.influence = temp_inf

                # Hoán đổi mute
                temp_mute = t_a.mute
                t_a.mute = t_b.mute
                t_b.mute = temp_mute

        # 3. Hoán đổi trong global list
        # Blender CollectionProperty hỗ trợ move()
        layers.move(layer_index, target_index)

        # 4. Cập nhật active index
        scene.animeow_global_active_index = target_index

        # 5. Re-select layer (pull active)
        LayerManager.select_layer(scene, target_index)

        return target_index

    # ──────────────────────────────────────────
    #  MERGE / BAKE
    # ──────────────────────────────────────────

    @staticmethod
    def merge_down(scene, layer_index):
        """Gộp layer tại layer_index xuống layer ngay bên dưới.

        Thực hiện bake cho TỪNG object riêng biệt.

        Args:
            scene: Blender Scene.
            layer_index: Vị trí layer trên.

        Returns:
            True nếu thành công.
        """
        layers = scene.animeow_global_layers
        below_index = layer_index - 1  # Index nhỏ hơn = layer dưới

        # Save original active object, selection, and mode
        context = bpy.context
        orig_active = context.view_layer.objects.active
        orig_selected_objs = list(context.selected_objects)
        orig_mode = orig_active.mode if orig_active else 'OBJECT'

        # Switch to OBJECT mode for safe execution of object selection and NLA bake
        if orig_mode != 'OBJECT' and bpy.ops.object.mode_set.poll():
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception:
                pass

        if below_index < 0:
            # Restore mode before returning False
            if orig_mode != 'OBJECT' and bpy.ops.object.mode_set.poll():
                try:
                    bpy.ops.object.mode_set(mode=orig_mode)
                except Exception:
                    pass
            return False

        upper_layer = layers[layer_index]
        lower_layer = layers[below_index]
        upper_track_name = _track_name_for_layer(upper_layer.name)
        lower_track_name = _track_name_for_layer(lower_layer.name)

        # Push active trên tất cả objects
        all_members = LayerManager.get_all_member_objects(scene)
        for obj in all_members:
            anim_data = obj.animation_data
            if anim_data and anim_data.action:
                LayerManager._push_active_to_nla(obj, scene)

        # Bake cho từng object
        frame_start = scene.frame_start
        frame_end = scene.frame_end

        for obj in all_members:
            anim_data = obj.animation_data
            if not anim_data:
                continue

            # Tìm 2 tracks
            t_upper = LayerManager._find_track_for_layer(anim_data, upper_layer.name, upper_layer.is_base)
            t_lower = LayerManager._find_track_for_layer(anim_data, lower_layer.name, lower_layer.is_base)

            if not t_upper and not t_lower:
                continue  # Object không tham gia cả 2 layer

            # Mute tất cả track khác
            original_mute = {}
            for track in anim_data.nla_tracks:
                original_mute[track.name] = track.mute
                if track != t_upper and track != t_lower:
                    track.mute = True
                else:
                    track.mute = False

            # Bake
            bake_types = {'POSE'} if obj.type == 'ARMATURE' else {'OBJECT'}
            # Deselect all objects first using low-level API to avoid context errors
            for o in context.view_layer.objects:
                o.select_set(False)
 
            # Select target object only
            obj.select_set(True)
            context.view_layer.objects.active = obj
 
            # Switch mode specifically for baking this object
            target_mode = 'POSE' if obj.type == 'ARMATURE' else 'OBJECT'
            if bpy.ops.object.mode_set.poll():
                try:
                    bpy.ops.object.mode_set(mode=target_mode)
                except Exception:
                    pass

            # Save and select all bones if Armature
            selected_bone_names = []
            if obj.type == 'ARMATURE' and obj.pose:
                selected_bone_names = [b.name for b in obj.pose.bones if _get_bone_select(b)]
                for b in obj.pose.bones:
                    _set_bone_select(b, True)
 
            try:
                bpy.ops.nla.bake(
                    frame_start=int(frame_start),
                    frame_end=int(frame_end),
                    step=1,
                    only_selected=True,
                    visual_keying=True,
                    clear_constraints=False,
                    clear_parents=False,
                    bake_types=bake_types
                )
            except Exception as e:
                # Restore bone selection
                if obj.type == 'ARMATURE' and obj.pose:
                    for b in obj.pose.bones:
                        _set_bone_select(b, b.name in selected_bone_names)
                # Switch back to OBJECT mode before restoring selections
                if obj.type == 'ARMATURE' and bpy.ops.object.mode_set.poll():
                    try:
                        bpy.ops.object.mode_set(mode='OBJECT')
                    except Exception:
                        pass
                # Restore object selection
                for o in context.view_layer.objects:
                    o.select_set(False)
                for o in orig_selected_objs:
                    try:
                        o.select_set(True)
                    except Exception:
                        pass
                context.view_layer.objects.active = orig_active
 
                # Khôi phục mute
                for track in anim_data.nla_tracks:
                    if track.name in original_mute:
                        track.mute = original_mute[track.name]
                continue
 
            # Restore bone selection
            if obj.type == 'ARMATURE' and obj.pose:
                for b in obj.pose.bones:
                    _set_bone_select(b, b.name in selected_bone_names)
 
            # Switch back to OBJECT mode before restoring selections
            if obj.type == 'ARMATURE' and bpy.ops.object.mode_set.poll():
                try:
                    bpy.ops.object.mode_set(mode='OBJECT')
                except Exception:
                    pass

            # Restore object selection
            for o in context.view_layer.objects:
                o.select_set(False)
            for o in orig_selected_objs:
                try:
                    o.select_set(True)
                except Exception:
                    pass
            context.view_layer.objects.active = orig_active

            # Lấy action baked
            merged_action = anim_data.action
            if merged_action:
                merged_action.name = lower_track_name
                merged_action.use_fake_user = True

            # Xóa 2 tracks cũ
            actions_to_remove = []
            for t in [t_upper, t_lower]:
                if t:
                    for strip in t.strips:
                        if strip.action and strip.action != merged_action:
                            actions_to_remove.append(strip.action)
                    try:
                        anim_data.nla_tracks.remove(t)
                    except Exception:
                        pass

            for act in actions_to_remove:
                try:
                    bpy.data.actions.remove(act)
                except Exception:
                    pass

            # Khôi phục mute
            for track in anim_data.nla_tracks:
                if track.name in original_mute:
                    track.mute = original_mute[track.name]

        # Xóa layer upper khỏi global list
        layers.remove(layer_index)

        # Điều chỉnh active index
        # Restore original active object, selection, and mode
        for o in context.view_layer.objects:
            o.select_set(False)
        for o in orig_selected_objs:
            try:
                o.select_set(True)
            except Exception:
                pass
        context.view_layer.objects.active = orig_active

        if orig_mode != 'OBJECT' and bpy.ops.object.mode_set.poll():
            try:
                # Switch active back to the original active object to restore its mode successfully
                bpy.context.view_layer.objects.active = orig_active
                bpy.ops.object.mode_set(mode=orig_mode)
            except Exception:
                pass

        return True

    @staticmethod
    def merge_all(scene, smart_clean=False, threshold=0.005):
        """Gộp tất cả layers thành 1 Action duy nhất cho TỪNG object.

        Args:
            scene: Blender Scene.
            smart_clean: Bật thuật toán lọc keyframe.
            threshold: Ngưỡng lọc.

        Returns:
            True nếu thành công.
        """
        layers = scene.animeow_global_layers
        # Save original active object, selection, and mode
        context = bpy.context
        orig_active = context.view_layer.objects.active
        orig_selected_objs = list(context.selected_objects)
        orig_mode = orig_active.mode if orig_active else 'OBJECT'

        # Switch to OBJECT mode for safe execution of object selection and NLA bake
        if orig_mode != 'OBJECT' and bpy.ops.object.mode_set.poll():
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception:
                pass

        if len(layers) == 0:
            # Restore mode before returning False
            if orig_mode != 'OBJECT' and bpy.ops.object.mode_set.poll():
                try:
                    bpy.ops.object.mode_set(mode=orig_mode)
                except Exception:
                    pass
            return False

        frame_start = scene.frame_start
        frame_end = scene.frame_end

        # Push active trên tất cả objects
        all_members = LayerManager.get_all_member_objects(scene)
        for obj in all_members:
            anim_data = obj.animation_data
            if anim_data and anim_data.action:
                LayerManager._push_active_to_nla(obj, scene)

        # Bake cho từng object
        for obj in all_members:
            anim_data = obj.animation_data
            if not anim_data:
                continue

            # Unmute tất cả ANL tracks
            for track in anim_data.nla_tracks:
                if track.name.startswith(ANL_PREFIX):
                    track.mute = False

            bake_types = {'POSE'} if obj.type == 'ARMATURE' else {'OBJECT'}
            # Deselect all objects first using low-level API to avoid context errors
            for o in context.view_layer.objects:
                o.select_set(False)
 
            # Select target object only
            obj.select_set(True)
            context.view_layer.objects.active = obj
 
            # Switch mode specifically for baking this object
            target_mode = 'POSE' if obj.type == 'ARMATURE' else 'OBJECT'
            if bpy.ops.object.mode_set.poll():
                try:
                    bpy.ops.object.mode_set(mode=target_mode)
                except Exception:
                    pass

            # Save and select all bones if Armature
            selected_bone_names = []
            if obj.type == 'ARMATURE' and obj.pose:
                selected_bone_names = [b.name for b in obj.pose.bones if _get_bone_select(b)]
                for b in obj.pose.bones:
                    _set_bone_select(b, True)
 
            try:
                bpy.ops.nla.bake(
                    frame_start=int(frame_start),
                    frame_end=int(frame_end),
                    step=1,
                    only_selected=True,
                    visual_keying=True,
                    clear_constraints=False,
                    clear_parents=False,
                    bake_types=bake_types
                )
            except Exception as e:
                # Restore bone selection
                if obj.type == 'ARMATURE' and obj.pose:
                    for b in obj.pose.bones:
                        _set_bone_select(b, b.name in selected_bone_names)
                # Switch back to OBJECT mode before restoring selections
                if obj.type == 'ARMATURE' and bpy.ops.object.mode_set.poll():
                    try:
                        bpy.ops.object.mode_set(mode='OBJECT')
                    except Exception:
                        pass
                # Restore object selection
                for o in context.view_layer.objects:
                    o.select_set(False)
                for o in orig_selected_objs:
                    try:
                        o.select_set(True)
                    except Exception:
                        pass
                context.view_layer.objects.active = orig_active
                continue
 
            # Restore bone selection
            if obj.type == 'ARMATURE' and obj.pose:
                for b in obj.pose.bones:
                    _set_bone_select(b, b.name in selected_bone_names)
 
            # Switch back to OBJECT mode before restoring selections
            if obj.type == 'ARMATURE' and bpy.ops.object.mode_set.poll():
                try:
                    bpy.ops.object.mode_set(mode='OBJECT')
                except Exception:
                    pass

            # Restore object selection
            for o in context.view_layer.objects:
                o.select_set(False)
            for o in orig_selected_objs:
                try:
                    o.select_set(True)
                except Exception:
                    pass
            context.view_layer.objects.active = orig_active

            merged_action = anim_data.action
            if merged_action:
                merged_action.use_fake_user = True

            # Xóa tất cả ANL tracks
            tracks_to_remove = [t for t in anim_data.nla_tracks if t.name.startswith(ANL_PREFIX)]
            actions_to_remove = set()
            for track in tracks_to_remove:
                for strip in track.strips:
                    if strip.action and strip.action != merged_action:
                        actions_to_remove.add(strip.action)

            for track in tracks_to_remove:
                try:
                    anim_data.nla_tracks.remove(track)
                except Exception:
                    pass

            for act in actions_to_remove:
                try:
                    bpy.data.actions.remove(act)
                except Exception:
                    pass

            # Smart Clean
            if smart_clean and merged_action:
                fcurves = get_action_fcurves(merged_action)
                for fc in fcurves:
                    clean_fcurve_keyframes(fc, threshold)
                    for kp in fc.keyframe_points:
                        kp.interpolation = 'BEZIER'
                        kp.handle_left_type = 'AUTO'
                        kp.handle_right_type = 'AUTO'
                    fc.update()

        # Xóa tất cả global layers
        layers.clear()
        scene.animeow_global_active_index = 0

        # Restore original active object, selection, and mode
        for o in context.view_layer.objects:
            o.select_set(False)
        for o in orig_selected_objs:
            try:
                o.select_set(True)
            except Exception:
                pass
        context.view_layer.objects.active = orig_active

        if orig_mode != 'OBJECT' and bpy.ops.object.mode_set.poll():
            try:
                # Switch active back to the original active object to restore its mode successfully
                bpy.context.view_layer.objects.active = orig_active
                bpy.ops.object.mode_set(mode=orig_mode)
            except Exception:
                pass

        return True

    # ──────────────────────────────────────────
    #  INTERNAL HELPERS
    # ──────────────────────────────────────────

    @staticmethod
    def _ensure_base_on_object(obj, scene):
        """Đảm bảo object có Base NLA track.

        Nếu object có active action nhưng chưa có Base track →
        push action thành Base.
        Nếu không có action → tạo Base rỗng.
        """
        anim_data = obj.animation_data
        if not anim_data:
            anim_data = obj.animation_data_create()

        base_track_name = _track_name_for_layer("Base")
        frame_start = scene.frame_start
        frame_end = scene.frame_end

        # Kiểm tra xem đã có Base track chưa (sử dụng _find_track_for_layer để hỗ trợ tương thích ngược)
        existing_base = LayerManager._find_track_for_layer(anim_data, "Base", True, scene)
        if existing_base:
            return  # Đã có

        if anim_data.action:
            # Push action hiện tại thành Base
            base_action = anim_data.action
            base_action.use_fake_user = True

            if not base_action.name.startswith(ANL_PREFIX):
                base_action.name = f"{ANL_PREFIX}{base_action.name}"

            track = anim_data.nla_tracks.new()
            track.name = base_track_name

            strip = track.strips.new(
                name=base_track_name,
                start=int(frame_start),
                action=base_action
            )
            # Tương thích Blender 5.0+ Action Slots cho NlaStrip
            if hasattr(strip, "action_slot") and base_action:
                if hasattr(base_action, "slots") and len(base_action.slots) > 0:
                    strip.action_slot = base_action.slots[0]
                elif hasattr(strip, "action_suitable_slots") and strip.action_suitable_slots:
                    strip.action_slot = strip.action_suitable_slots[0]
            strip.blend_type = 'REPLACE'
            strip.frame_start = frame_start
            strip.frame_end = frame_end
            strip.action_frame_start = frame_start
            strip.action_frame_end = frame_end
            strip.extrapolation = 'HOLD'

            anim_data.action = None
        else:
            # Tạo Base rỗng
            base_action = bpy.data.actions.new(name=base_track_name)
            base_action.use_fake_user = True

            # Đảm bảo tạo slot cho Base Action mới trong Blender 5.0+
            if hasattr(base_action, "slots"):
                id_type = 'POSE' if obj.type == 'ARMATURE' else 'OBJECT'
                new_slot = base_action.slots.new(id_type=id_type, name=obj.name)

            track = anim_data.nla_tracks.new()
            track.name = base_track_name

            strip = track.strips.new(
                name=base_track_name,
                start=int(frame_start),
                action=base_action
            )
            # Tương thích Blender 5.0+ Action Slots cho NlaStrip
            if hasattr(strip, "action_slot") and base_action:
                if hasattr(base_action, "slots") and len(base_action.slots) > 0:
                    strip.action_slot = base_action.slots[0]
                elif hasattr(strip, "action_suitable_slots") and strip.action_suitable_slots:
                    strip.action_slot = strip.action_suitable_slots[0]
            strip.blend_type = 'REPLACE'
            strip.frame_start = frame_start
            strip.frame_end = frame_end
            strip.action_frame_start = frame_start
            strip.action_frame_end = frame_end
            strip.extrapolation = 'HOLD'

    @staticmethod
    def _push_active_to_nla(obj, scene):
        """Push active action xuống NLA track tương ứng.

        Nếu đã có track ANL_ trùng tên → gắn lại strip vào track đó.
        Nếu chưa có → tạo track mới.
        """
        anim_data = obj.animation_data
        if not anim_data or not anim_data.action:
            return

        action = anim_data.action
        frame_start = scene.frame_start
        frame_end = scene.frame_end

        # Lưu lại blend type và influence từ active action
        blend_type = anim_data.action_blend_type
        influence = anim_data.action_influence

        # Xác định xem action này có thuộc Base layer hay không dựa vào active index trên scene
        active_index = scene.animeow_global_active_index
        layers = scene.animeow_global_layers
        is_base = False
        layer_display_name = ""
        
        if 0 <= active_index < len(layers):
            is_base = layers[active_index].is_base
            layer_display_name = layers[active_index].name
        else:
            # Fallback nếu index không khớp
            layer_display_name = action.name
            if layer_display_name.startswith(ANL_PREFIX):
                layer_display_name = layer_display_name[len(ANL_PREFIX):]
            is_base = (layer_display_name == "Base")

        # Xác định tên track thực tế
        if is_base:
            track_name = _track_name_for_layer("Base")
        else:
            if action.name.startswith(ANL_PREFIX):
                track_name = action.name
            else:
                track_name = f"{ANL_PREFIX}{action.name}"

        # Tìm track đã tồn tại
        existing_track = LayerManager._find_track_for_layer(anim_data, layer_display_name, is_base, scene)

        # Ngắt active action trước khi tạo strip
        anim_data.action = None

        if existing_track:
            # Track đã có → xóa strip cũ nếu có, tạo strip mới
            for strip in list(existing_track.strips):
                existing_track.strips.remove(strip)

            strip = existing_track.strips.new(
                name=track_name,
                start=int(frame_start),
                action=action
            )
        else:
            # Tạo track mới
            track = anim_data.nla_tracks.new()
            track.name = track_name

            strip = track.strips.new(
                name=track_name,
                start=int(frame_start),
                action=action
            )

        # Cấu hình strip
        # Tương thích Blender 5.0+ Action Slots cho NlaStrip
        if hasattr(strip, "action_slot") and action:
            if hasattr(action, "slots") and len(action.slots) > 0:
                strip.action_slot = action.slots[0]
            elif hasattr(strip, "action_suitable_slots") and strip.action_suitable_slots:
                strip.action_slot = strip.action_suitable_slots[0]

        strip.frame_start = frame_start
        strip.frame_end = frame_end
        strip.action_frame_start = frame_start
        strip.action_frame_end = frame_end
        strip.blend_type = blend_type
        strip.influence = influence
        strip.extrapolation = 'HOLD'
