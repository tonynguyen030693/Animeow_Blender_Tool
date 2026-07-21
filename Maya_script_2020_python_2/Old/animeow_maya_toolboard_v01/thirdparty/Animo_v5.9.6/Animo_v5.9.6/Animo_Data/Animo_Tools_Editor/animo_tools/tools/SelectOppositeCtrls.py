import maya.cmds as cmds
import re


BASE_PATTERNS = [
    ("_Left_", "_Right_"), ("_left_", "_right_"),
    ("_Left", "_Right"), ("_left", "_right"),
    ("Left_", "Right_"), ("left_", "right_"),
    ("Left", "Right"), ("left", "right"),
    ("_L_", "_R_"), ("_l_", "_r_"),
    ("_L__", "_R__"), ("_l__", "_r__"),
    ("__L_", "__R_"), ("__l_", "__r_"),
    ("_L", "_R"), ("_l", "_r"),
    ("L_", "R_"), ("l_", "r_"),
    (".L.", ".R."), (".l.", ".r."),
    (".L", ".R"), (".l", ".r"),
    ("-L-", "-R-"), ("-l-", "-r-"),
    ("-L", "-R"), ("-l", "-r"),
    ("_Lf_", "_Rt_"), ("_lf_", "_rt_"),
    ("_Lf", "_Rt"), ("_lf", "_rt"),
    ("Lf_", "Rt_"), ("lf_", "rt_"),
    ("Lf", "Rt"), ("lf", "rt"),
    ("Lt", "Rt"), ("lt", "rt"),
    ("Lft", "Rgt"), ("lft", "rgt"),
    ("Lft_", "Rgt_"), ("lft_", "rgt_"),
    ("_Lt_", "_Rt_"), ("_lt_", "_rt_"),
    ("_LHS_", "_RHS_"), ("_lhs_", "_rhs_"),
    ("_LHS", "_RHS"), ("_lhs", "_rhs"),
    ("_LH_", "_RH_"), ("_lh_", "_rh_"),
    ("_LH", "_RH"), ("_lh", "_rh"),
    ("LH", "RH"), ("lh", "rh"),
    ("LHS", "RHS"), ("lhs", "rhs"),
    ("SideL", "SideR"), ("sideL", "sideR"),
    ("_SideL_", "_SideR_"), ("_sideL_", "_sideR_"),
    ("L_Side", "R_Side"), ("l_side", "r_side"),
    ("L0", "R0"), ("l0", "r0"),
    ("L1", "R1"), ("l1", "r1"),
    ("L2", "R2"), ("l2", "r2"),
    ("L3", "R3"), ("l3", "r3"),
    ("L4", "R4"), ("l4", "r4"),
    ("L01", "R01"), ("l01", "r01"),
    ("L02", "R02"), ("l02", "r02"),
    ("_L01", "_R01"), ("_l01", "_r01"),
    ("LeftArm", "RightArm"), ("leftArm", "rightArm"),
    ("Arm_L", "Arm_R"), ("arm_l", "arm_r"),
    ("ArmL", "ArmR"), ("armL", "armR"),
    ("LegL", "LegR"), ("legL", "legR"),
    ("HandL", "HandR"), ("handL", "handR"),
    ("_ArmL_", "_ArmR_"), ("_armL_", "_armR_"),
    ("_Lft_", "_Rgt_"), ("_lft_", "_rgt_"),
    ("Lft_", "Rgt_"), ("lft_", "rgt_"),
    ("_Lft", "_Rgt"), ("_lft", "_rgt"),
    ("__Left__", "__Right__"), ("__left__", "__right__"),
    ("LeftSide", "RightSide"), ("leftSide", "rightSide"),
    ("_LeftSide_", "_RightSide_"), ("_leftSide_", "_rightSide_"),
    ("L", "R"), ("l", "r")
]


def strip_namespace(obj):
    if ":" in obj:
        ns, name = obj.rsplit(":", 1)
        return ns + ":", name
    return "", obj


def learn_scene_patterns():
    scene_objects = cmds.ls(dag=True, long=False) or []
    detected = set()
    token_pattern = re.compile(r"[\W_]([A-Z]?[lLrR](?:\d*)?)[\W_]?")
    for obj in scene_objects:
        name = strip_namespace(obj)[1]
        matches = token_pattern.findall(name)
        for m in matches:
            if len(m) <= 4 and any(ch in m.lower() for ch in ("l", "r")):
                detected.add(m)
    dynamic = set()
    for token in detected:
        if "l" in token.lower():
            dynamic.add((token, token.replace("l", "r").replace("L", "R")))
        elif "r" in token.lower():
            dynamic.add((token.replace("r", "l").replace("R", "L"), token))
    return list(dynamic)


def get_patterns():
    all_patterns = BASE_PATTERNS + learn_scene_patterns()
    seen = set()
    unique = []
    for pair in all_patterns:
        if pair not in seen:
            seen.add(pair)
            unique.append(pair)
    return unique


def select_opposite():
    selected_ctrls = cmds.ls(selection=True)
    if not selected_ctrls:
        cmds.warning("No controls selected.")
        return

    patterns = get_patterns()
    opposites = []

    for ctrl in selected_ctrls:
        ns, name = strip_namespace(ctrl)
        found = None

        for left, right in patterns:
            if left in name:
                cand = name.replace(left, right)
                full = ns + cand
                if cmds.objExists(full):
                    found = full
                    break
            elif right in name:
                cand = name.replace(right, left)
                full = ns + cand
                if cmds.objExists(full):
                    found = full
                    break

        if found:
            opposites.append(found)

    if opposites:
        cmds.select(opposites, r=True)
    else:
        cmds.warning("No matching opposites found.")


select_opposite()