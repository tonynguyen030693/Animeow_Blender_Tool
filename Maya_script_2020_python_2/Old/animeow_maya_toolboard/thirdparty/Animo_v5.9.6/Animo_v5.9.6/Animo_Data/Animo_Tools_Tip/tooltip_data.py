"""
Tooltip Data for Animo Toolbar
Contains all tooltip content: titles, descriptions, tips, and GIF references
"""
from __future__ import absolute_import, division, print_function, unicode_literals

TOOLTIP_DATA = {
    # ============================================
    # Main Toolbar Icons (Group 0: Transify group)
    # ============================================
    
    "transify_launcher": {
        "title": "Anim Transfer",
        "description": "Copy animation or poses between characters, or even across different Maya scenes with ease.",
        "info_lines": [
            "Transfer animation between rigs.",
            "Copy poses across scenes.",
            "Works with different character setups."
        ],
        "shortcut": "",
        "gif": "transify",
        "title_color": "#E07070"
    },
    
    "keys_time_launcher": {
        "title": "Keys Time",
        "description": "Save and restore your keyframe timing. Perfect for when you bake animation and want your clean keys back.",
        "info_lines": [
            "Copy key positions from controls.",
            "Paste timing back after baking.",
            "Preserve your original key structure."
        ],
        "shortcut": "",
        "gif": "keys_time",
        "title_color": "#E07070"
    },
    
    "fast_anim_layer_launcher": {
        "title": "Fast Merge AnimLayers",
        "description": "Merge animation layers 10-50x faster than Maya's native tool. A must-have for animation layer workflows.",
        "info_lines": [
            "Blazing fast layer merging.",
            "Smart merge preserves key timing.",
            "Works with selected or all layers."
        ],
        "shortcut": "",
        "gif": "fast_anim_layer",
        "title_color": "#E07070"
    },
    
    # ============================================
    # Group 1: Pickify/Tweenify/Tracify
    # ============================================
    
    "pickify_launcher": {
        "title": "Selection Sets",
        "description": "Create powerful, color-coded selection sets. Export and reuse them across different animations.",
        "info_lines": [
            "Organize controls with color coding.",
            "Export sets for other scenes.",
            "Never recreate sets again."
        ],
        "shortcut": "",
        "gif": "pickify",
        "title_color": "#E8608C"
    },
    
    "tweenify_launcher": {
        "title": "Anim Sliders",
        "description": "Powerful animation sliders including Tween Machine, Blend to Neighbor, and more. Works great with Graph Editor and Channel Box selection.",
        "info_lines": [
            "Tween between keyframes smoothly.",
            "Blend values to neighboring keys.",
            "Works with timeline selection too."
        ],
        "shortcut": "",
        "gif": "tweenify",
        "title_color": "#E8608C"
    },
    
    "tracify_launcher": {
        "title": "Arc Tracker",
        "description": "A lightning-fast arc tracker that won't slow down your scene, even on heavy rigs.",
        "info_lines": [
            "Visualize motion arcs in real-time.",
            "Much faster than Maya's native tracker.",
            "Essential for polishing animation."
        ],
        "shortcut": "",
        "gif": "tracify",
        "title_color": "#E8608C"
    },
    
    # ============================================
    # Group 2: Spacify/Xform/Attributes
    # ============================================
    
    "spacify_launcher": {
        "title": "Temp Controls",
        "description": "An awesome toolset for space-switching and temporary animation controls. Play around and discover new workflows!",
        "info_lines": [
            "Create temporary animation controls.",
            "Space-switch without losing poses.",
            "Flexible workflow for any rig."
        ],
        "shortcut": "",
        "gif": "spacify",
        "title_color": "#B478C8"
    },
    
    "xform_align_launcher": {
        "title": "Xform - Align",
        "description": "Two powerful tools in one! Xform stores world positions and applies them back after space changes. Align matches objects to a target's transform.",
        "info_lines": [
            "Xform: Store and restore world positions.",
            "Great after switching control spaces.",
            "Align: Match position/rotation to target."
        ],
        "shortcut": "",
        "gif": "xform_align",
        "title_color": "#B478C8"
    },
    
    "attributes_space_switcher_launcher": {
        "title": "Attributes Space Switcher",
        "description": "Change the space of your controls without losing animation. Also helps find the best rotate order to avoid gimbal lock.",
        "info_lines": [
            "Switch spaces seamlessly.",
            "Preserves all your animation.",
            "Optimize rotate order automatically."
        ],
        "shortcut": "",
        "gif": "attributes_space_switcher",
        "title_color": "#B478C8"
    },
    
    "temp_pivot_launcher": {
        "title": "Temp Pivot",
        "description": "Change the pivot point of your current pose without breaking the animation. Perfect for rotating entire characters from a custom pivot point.",
        "info_lines": [
            "Adjust pivot for current pose only.",
            "Rotate characters from any point.",
            "Grab world controls for full body rotation."
        ],
        "shortcut": "",
        "gif": "temp_pivot",
        "title_color": "#B478C8"
    },
    
    # ============================================
    # Group 3: Global Offset/Twosify/Vectorify
    # ============================================
    
    "global_offset_launcher": {
        "title": "Global Offset",
        "description": "Quickly offset poses for an entire range or selection. Like animation layers, but faster and without the merge cleanup.",
        "info_lines": [
            "Offset entire pose ranges.",
            "No layer merging needed.",
            "Keeps your keyframes clean."
        ],
        "shortcut": "",
        "gif": "global_offset",
        "title_color": "#4A90D9"
    },
    
    "twosify_launcher": {
        "title": "Twosify",
        "description": "Make your splined animation look stepped without destroying your curves. Attach to camera space for that Spider-Verse style!",
        "info_lines": [
            "Stepped look, splined data.",
            "Camera-space attachment option.",
            "Perfect for stylized animation."
        ],
        "shortcut": "",
        "gif": "twosify",
        "title_color": "#4A90D9"
    },
    
    "vectorify_launcher": {
        "title": "Vectorify",
        "description": "A powerful tool for repathing animation while keeping feet locked to the ground. Your planted feet stay solid throughout the repath.",
        "info_lines": [
            "Repath motion trajectories.",
            "Maintains planted feet positions.",
            "Perfect for redirecting locomotion."
        ],
        "shortcut": "",
        "gif": "vectorify",
        "title_color": "#4A90D9"
    },
    
    # ============================================
    # Group 4: Tools Editor/Quick Exporter/Playblaster
    # ============================================
    
    "tools_editor_launcher": {
        "title": "Tools Editor",
        "description": "Discover more animation tools! Add them to your shelf or assign hotkeys for quick access.",
        "info_lines": [
            "Browse all available tools.",
            "Add tools to your shelf.",
            "Assign custom hotkeys."
        ],
        "shortcut": "",
        "gif": "tools_editor",
        "title_color": "#D8D0E8"
    },
    
    "quick_exporer_launcher": {
        "title": "Quick Exporter",
        "description": "Export selected objects and quickly import them into another Maya scene. Perfect for transferring assets between files.",
        "info_lines": [
            "Fast object export/import.",
            "Great for layout artists.",
            "Streamlines asset transfer."
        ],
        "shortcut": "",
        "gif": "quick_exporter",
        "title_color": "#D8D0E8"
    },
    
    "fast_multi_view_playblaster_launcher": {
        "title": "Multi-View Playblaster",
        "description": "Playblast multiple camera views at once with a single click. Perfect for checking animation from different angles.",
        "info_lines": [
            "Capture multiple views simultaneously.",
            "Great for review sessions.",
            "Export to your editing software."
        ],
        "shortcut": "",
        "gif": "multi_view_playblaster",
        "title_color": "#D8D0E8"
    },
    
    # ============================================
    # Left Side Icons (Reset, Bake, Share Keys)
    # ============================================
    
    "reset_pose_launcher": {
        "title": "Reset Pose",
        "description": "Reset selected controls to their default pose. Works with Timeline, Graph Editor, and Channel Box selection too!",
        "info_lines": [
            "Resets translate, rotate, and scale.",
            "Respects default attribute values.",
            "Works with custom attributes."
        ],
        "shortcut": "",
        "gif": "reset_pose",
        "title_color": "#E07080"
    },
    
    "share_keys_launcher": {
        "title": "Share Keys",
        "description": "Add keys on all keyframe positions across your timeline with one click. Works with Timeline, Graph Editor, and Channel Box selection.",
        "info_lines": [
            "Select controls to share keys.",
            "Keys added without changing values.",
            "Great for syncing timing."
        ],
        "shortcut": "",
        "gif": "share_keys",
        "title_color": "#E8C050"
    },
    
    # ============================================
    # Tangent Icons
    # ============================================
    
    "auto_tangent": {
        "title": "Auto Tangent",
        "description": "Set curve tangents to Auto mode for smooth, natural interpolation between keyframes.",
        "info_lines": [
            "All Keys: Apply to entire animation.",
            "Selected: Works with timeline or Graph Editor selection.",
            "Creates flowing, organic motion."
        ],
        "shortcut": "",
        "gif": "auto_tangent",
        "title_color": "#FF8C42"
    },
    
    "linear_tangent": {
        "title": "Linear Tangent",
        "description": "Set curve tangents to Linear mode for constant-speed, straight-line motion between keyframes.",
        "info_lines": [
            "All Keys: Apply to entire animation.",
            "Selected: Works with timeline or Graph Editor selection.",
            "Even spacing with no ease in/out."
        ],
        "shortcut": "",
        "gif": "linear_tangent",
        "title_color": "#FF8C42"
    },
    
    "step_tangent": {
        "title": "Step Tangent",
        "description": "Set curve tangents to Step mode for instant value changes with no interpolation between keyframes.",
        "info_lines": [
            "All Keys: Apply to entire animation.",
            "Selected: Works with timeline or Graph Editor selection.",
            "Perfect for blocking and pose-to-pose workflow."
        ],
        "shortcut": "",
        "gif": "step_tangent",
        "title_color": "#FF8C42"
    },
    
    # ============================================
    # Select Opposite
    # ============================================
    
    "SelectOppositeCtrls": {
        "title": "Select Opposite",
        "description": "Instantly select the opposite side controls. A hotkey is highly recommended for this one!",
        "info_lines": [
            "Left to Right, Right to Left.",
            "Works with most rig naming conventions.",
            "Essential for mirroring workflows."
        ],
        "shortcut": "Hotkey Recommended",
        "gif": "SelectOpposite",
        "title_color": "#4A90D9"
    },
    
    "SelectAddOppositeCtrls": {
        "title": "Add Opposite to Selection",
        "description": "Add the opposite side controls to your current selection without deselecting.",
        "info_lines": [
            "Keeps current selection.",
            "Adds opposite controls.",
            "Great for symmetrical edits."
        ],
        "shortcut": "",
        "gif": "SelectOpposite",
        "title_color": "#4A90D9"
    },
    
    # ============================================
    # White Icons (Right Side)
    # ============================================
    
    "SmoothSelectedKeys": {
        "title": "Smooth Selected Keys",
        "description": "Smooth out jittery animation curves like butter. Perfect for cleaning up mocap or noisy keyframes.",
        "info_lines": [
            "Removes unwanted jitter.",
            "Preserves overall motion.",
            "Works on selected keys."
        ],
        "shortcut": "",
        "gif": "SmoothSelectedKeys",
        "title_color": "#4A90D9"
    },
    
    "SmartSnapKeys": {
        "title": "Smart Snap Keys",
        "description": "Snap keys to whole frames intelligently. Much smarter than Maya's native tool - won't break your poses!",
        "info_lines": [
            "Removes sub-frame keys.",
            "Preserves pose integrity.",
            "Handles compressed keys gracefully."
        ],
        "shortcut": "",
        "gif": "SmartSnapKeys",
        "title_color": "#4A90D9"
    },
    
    "CropAnimation": {
        "title": "Crop Animation",
        "description": "Keep only the keys within your selected range and remove everything outside. Clean up made easy!",
        "info_lines": [
            "Uses playback range start/end.",
            "Preserves keys within range.",
            "Perfect for trimming clips."
        ],
        "shortcut": "",
        "gif": "CropAnimation",
        "title_color": "#4A90D9"
    },
    
    "DeleteRedundantKeys": {
        "title": "Delete Redundant Keys",
        "description": "Remove static keys and flat curves that aren't doing anything. Essential for cleaning up baked animation.",
        "info_lines": [
            "Deletes keys with identical values.",
            "Removes flat animation curves.",
            "Optimizes your scene."
        ],
        "shortcut": "",
        "gif": "DeleteRedundantKeys",
        "title_color": "#4A90D9"
    },
    
    # ============================================
    # About & Dock
    # ============================================
    
    "about_launcher": {
        "title": "About Animo",
        "description": "Information about Animo Launcher, version details, and credits.",
        "info_lines": [],
        "shortcut": "",
        "gif": "",
        "title_color": "#4A90D9"
    },
    
    "dock_position": {
        "title": "Dock Position",
        "description": "Change where the Animo toolbar is docked in Maya's interface.",
        "info_lines": [
            "Timeline, Status Line, Shelf, and more.",
            "Choose your preferred location.",
            "Remembers your setting."
        ],
        "shortcut": "",
        "gif": "",
        "title_color": "#4A90D9"
    },
    
    # ============================================
    # Fast Bake Menu Options
    # ============================================
    
    "fast_bake_launcher": {
        "title": "Fast Bake",
        "description": "Bake your animation 10-50x faster than Maya's native bake. Choose your stepping interval from the menu.",
        "info_lines": [
            "Lightning fast baking.",
            "Multiple step options (1s to 7s).",
            "Removes constraints after baking."
        ],
        "shortcut": "",
        "gif": "fast_bake",
        "title_color": "#E89050"
    },
    
    # ============================================
    # Animation Sliders
    # ============================================
    
    "tween_slider": {
        "title": "Tween Machine",
        "description": "Easily create breakdowns between your poses. Slide to blend toward the previous or next keyframe.",
        "info_lines": [
            "Drag left to favor previous pose.",
            "Drag right to favor next pose.",
            "Works with current time, Graph Editor, and Channel Box selection."
        ],
        "shortcut": "",
        "gif": "tween",
        "title_color": "#E1AF2D"
    },
    
    "blend_slider": {
        "title": "Blend to Neighbor",
        "description": "Blend your current pose or selected keys toward neighboring keyframes. Perfect for fine-tuning spacing and favoring poses.",
        "info_lines": [
            "Nudge animation for perfect spacing.",
            "Great for easing into poses.",
            "Works with Graph Editor and Channel Box selection."
        ],
        "shortcut": "",
        "gif": "blend_to_neighbor",
        "title_color": "#DC8C3C"
    },
    
    "scale_slider": {
        "title": "Scale Keys",
        "description": "Scale your selected keys using neighboring keyframes as pivot points. Right-click to switch between Left, Right, and Average modes.",
        "info_lines": [
            "Scale Left: Pivot on left key.",
            "Scale Right: Pivot on right key.",
            "Scale Average: Pivot at curve center."
        ],
        "shortcut": "",
        "gif": "scale_left",
        "title_color": "#64B4DC"
    },
    
    "cascade_slider": {
        "title": "Cascade",
        "description": "Connect multiple animation curves to a single selected keyframe without breaking their original motion. Best used in the Graph Editor.",
        "info_lines": [
            "Select one keyframe as anchor point.",
            "All curves connect to that key.",
            "Preserves original curve shapes."
        ],
        "shortcut": "",
        "gif": "cascade",
        "title_color": "#B478C8"
    },
}


def get_tooltip_data(launcher_name):
    """
    Get tooltip data for a specific launcher/tool
    
    Args:
        launcher_name: The launcher function name or tool identifier
        
    Returns:
        dict with title, description, info_lines, shortcut, gif, title_color
    """
    return TOOLTIP_DATA.get(launcher_name, {
        "title": launcher_name.replace("_launcher", "").replace("_", " ").title(),
        "description": "Animation tool from the Animo Launcher.",
        "info_lines": [],
        "shortcut": "",
        "gif": "",
        "title_color": "#4A90D9"
    })