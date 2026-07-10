import os
import json
ROOT_DIR = r'C:\Users\Animeow\Documents\maya\2020\scripts\pose_library'
EXT = 'json'



def get_poses_dict():
    poses_dict = {}
    for file_name in os.listdir(ROOT_DIR):
        if not file_name.endswith(EXT):
            continue
        pose_name = file_name.splite('.')[0]
        file_path = os.path.join(ROOT_DIR, file_name)
        poses_dict[pose_name] = file_path
    return poses_dict    



def write_pose_to_file(pose_name, pose_dict):
    file_name = '{}.{}'.format(pose_name, EXT)
    file_path = os.path.join(ROOT_DIR,file_name)

    with open(file_path, 'w') as f:
        json.dump(pose_dict, f, indent=4)

def read_pose_from_file(file_path):
    with open(file_path, 'r') as f:
        pose_dict = json.load(f)
        return pose_dict