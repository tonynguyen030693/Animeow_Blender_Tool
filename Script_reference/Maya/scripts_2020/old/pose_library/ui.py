from pose_library import core
import pose_transfer
from maya import cmds


WINDOW_NAME = 'pose_library_ui'
TEXT_LIST_NAME = 'pose_names_text_list'
TEXT_FIELD_NAME = 'save_pose_text_field'


def show_ui():
    """Show pose library ui."""
    if cmds.window(WINDOW_NAME, query=True, exists=True):
        cmds.deleteUI(WINDOW_NAME)

    cmds.window(WINDOW_NAME, title='Pose Library')
    # apply pose section
    cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
    cmds.textScrollList(TEXT_LIST_NAME, allowMultiSelection=False)
    cmds.button(label='Apply Pose', height=30, command=apply_selected_pose)

    # save pose section
    cmds.frameLayout(label='Save Pose', collapsable=True, backgroundColor=(0.10, 0.54, 0.67))
    cmds.columnLayout(adjustableColumn=True)
    cmds.rowLayout(numberOfColumns=3, adjustableColumn=2)
    cmds.text(label='Name')
    cmds.textField(TEXT_FIELD_NAME)
    # set column layout as new parent
    cmds.setParent('..')
    cmds.button(label='Save Pose', height=25, command=save_pose)

    cmds.showWindow(WINDOW_NAME)

    # populate poses
    reload_poses()


def save_pose(*args):
    pose_name = cmds.textField(TEXT_FIELD_NAME, query=True, text=True)
    # validate pose name
    if pose_name == '':
        cmds.warning('Please type a pose name!')
        return

    # validate scene selection
    selected_namespaces = pose_transfer.get_selected_namespaces()
    if len(selected_namespaces) != 1:
        cmds.warning('Please select ONE rig in the scene!')
        return

    # validate unique pose
    saved_poses_dict = core.get_poses_dict()
    if pose_name in saved_poses_dict:
        cmds.warning('Pose "{}" already exists. Please choose another name.'.format(pose_name))
        return

    pose_dict = pose_transfer.get_pose_dict(selected_namespaces[0])
    core.write_pose_to_file(pose_name, pose_dict)

    cmds.confirmDialog(message='Successfully saved pose: {}'.format(pose_name))
    reload_poses()


def reload_poses():
    """Gather poses from files and populate list with them."""
    # clear out list
    cmds.textScrollList(TEXT_LIST_NAME, edit=True, removeAll=True)
    poses_dict = core.get_poses_dict()
    pose_names = poses_dict.keys()
    sorted_names = sorted(pose_names)
    for name in sorted_names:
        add_pose(name)


def add_pose(pose_name):
    """Add new pose name to text list.

    Args:
        pose_name(str):

    """
    cmds.textScrollList(TEXT_LIST_NAME, edit=True, append=pose_name)


def apply_selected_pose(*args):
    """Apply selected poses to selected characters."""
    selected_pose = get_selected_pose()
    if selected_pose is None:
        cmds.warning('Please select a pose!')
        return

    selected_namespaces = pose_transfer.get_selected_namespaces()
    if not selected_namespaces:
        cmds.warning('Please select at least one rig!')
        return

    saved_poses_dict = core.get_poses_dict()
    if selected_pose not in saved_poses_dict:
        cmds.warning('Pose: "{}" does not exist!'.format(selected_pose))
        return

    pose_file = saved_poses_dict[selected_pose]
    pose_dict = core.read_pose_from_file(pose_file)
    for namespace in selected_namespaces:
        pose_transfer.apply_pose(pose_dict, namespace)


def get_selected_pose():
    """Get selected item from list.

    Returns:
        str|None: None if nothing was selected, otherwise the selected pose name.

    """
    selection = cmds.textScrollList(TEXT_LIST_NAME, query=True, selectItem=True)
    if selection is None:
        return None
    selected_item = selection[0]
    return selected_item



