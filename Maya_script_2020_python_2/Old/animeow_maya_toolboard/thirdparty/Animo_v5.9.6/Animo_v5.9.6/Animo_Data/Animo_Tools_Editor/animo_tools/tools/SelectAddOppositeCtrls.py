import maya.cmds as cmds


PATTERNS = [
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


def select_add_opposite():
    selected_ctrls = cmds.ls(selection=True)
    if not selected_ctrls:
        cmds.warning("No controls selected.")
        return

    opposites = []

    for ctrl in selected_ctrls:
        namespace, short_name = strip_namespace(ctrl)
        found = None

        for left_pattern, right_pattern in PATTERNS:
            if left_pattern in short_name:
                candidate = short_name.replace(left_pattern, right_pattern)
                opposite_full = namespace + candidate
                if cmds.objExists(opposite_full):
                    found = opposite_full
                    break
            elif right_pattern in short_name:
                candidate = short_name.replace(right_pattern, left_pattern)
                opposite_full = namespace + candidate
                if cmds.objExists(opposite_full):
                    found = opposite_full
                    break

        if found:
            opposites.append(found)

    if opposites:
        cmds.select(opposites, add=True)
    else:
        cmds.warning("No matching opposites found for selected controls.")

select_add_opposite()